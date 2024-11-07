import asyncio
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import logging


sys.path.append(str(Path(__file__).parent.parent))

from src.server.translation_server import TranslationServer
from src.client.translation_client import TranslationClient, TranslationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_translation_flow():
    
    server = TranslationServer()
    test_client = TestClient(server.app)
    
    
    client = TranslationClient(
        base_url="http://localhost:8000",
        initial_delay=0.5,
        max_delay=2.0
    )

    def on_status_change(status: TranslationStatus):
        logger.info(f"Status changed to: {status}")

    def on_completion(data: dict):
        logger.info(f"Job completed with data: {data}")

    try:
        # Create a job
        job_id = await client.create_job(video_length=5)
        logger.info(f"Created job with ID: {job_id}")

        # Monitor status
        final_status = await client.get_status(
            job_id,
            on_status_change=on_status_change,
            on_completion=on_completion
        )

        assert final_status in (TranslationStatus.COMPLETED, TranslationStatus.ERROR)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_translation_flow())