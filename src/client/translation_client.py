import httpx
import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class TranslationStatus(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    ERROR = "error"

class TranslationClient:
    def __init__(
        self,
        base_url: str,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 1.5,
        max_retries: int = 7,
        timeout: float = 250.0  # 5 minutes default timeout
    ):
        self.base_url = base_url.rstrip('/')
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries
        self.timeout = timeout
        self._client = httpx.AsyncClient()

    async def create_job(self, video_length: int) -> str:
        """Create a new translation job and return the job ID."""
        try:
            response = await self._client.post(
                f"{self.base_url}/jobs",
                params={"video_length": video_length}
            )
            response.raise_for_status()
            return response.json()["job_id"]
        except httpx.HTTPError as e:
            logger.error(f"Failed to create job: {e}")
            raise

    async def get_status(
        self,
        job_id: str,
        on_status_change: Optional[Callable[[TranslationStatus], None]] = None,
        on_completion: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> TranslationStatus:
        """
        Smart status checking with exponential backoff and callbacks.
        Returns immediately if status is COMPLETED or ERROR.
        """
        current_delay = self.initial_delay
        last_status = None
        start_time = asyncio.get_event_loop().time()
        retries = 0

        while True:
            try:
                response = await self._client.get(f"{self.base_url}/status/{job_id}")
                response.raise_for_status()
                status_data = response.json()
                current_status = TranslationStatus(status_data["result"])

                # Call status change callback if status changed
                if current_status != last_status and on_status_change:
                    await asyncio.create_task(
                        asyncio.to_thread(on_status_change, current_status)
                    )
                
                last_status = current_status

                if current_status in (TranslationStatus.COMPLETED, TranslationStatus.ERROR):
                    if on_completion:
                        await asyncio.create_task(
                            asyncio.to_thread(on_completion, status_data)
                        )
                    return current_status

                # Check timeout
                if asyncio.get_event_loop().time() - start_time > self.timeout:
                    raise TimeoutError("Status check timed out")

                # Wait exponential backoff
                await asyncio.sleep(current_delay)
                current_delay = min(current_delay * self.backoff_factor, self.max_delay)
                retries = 0  # Reset retries on successful request

            except httpx.HTTPError as e:
                retries += 1
                if retries >= self.max_retries:
                    raise Exception(f"Max retries exceeded: {e}")
                
                logger.warning(f"Request failed, retrying in {current_delay}s: {e}")
                await asyncio.sleep(current_delay)
                current_delay = min(current_delay * self.backoff_factor, self.max_delay)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()