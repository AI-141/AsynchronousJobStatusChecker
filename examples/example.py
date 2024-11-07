import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.client.translation_client import TranslationClient, TranslationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    async with TranslationClient("http://localhost:8000") as client:
        # Create a translation job
        job_id = await client.create_job(video_length=10)
        logger.info(f"Created translation job: {job_id}")

        # Define callbacks
        def on_status_change(status: TranslationStatus):
            logger.info(f"Job status changed to: {status}")

        def on_completion(data: dict):
            logger.info(f"Job completed with result: {data}")

        # Monitor status with callbacks
        try:
            final_status = await client.get_status(
                job_id,
                on_status_change=on_status_change,
                on_completion=on_completion
            )
            logger.info(f"Final status: {final_status}")
        except TimeoutError:
            logger.error("Status check timed out")
        except Exception as e:
            logger.error(f"Error checking status: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 