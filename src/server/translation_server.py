from fastapi import FastAPI, HTTPException
import time
import random
from enum import Enum
import uuid

class JobStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ERROR = "error"

class TranslationServer:
    def __init__(self):
        self.app = FastAPI()
        self.jobs = {}
        
        @self.app.post("/jobs")
        async def create_job(video_length: int):
            job_id = str(uuid.uuid4())
            completion_time = time.time() + random.uniform(video_length * 0.5, video_length * 1.5)
            error_chance = 0.1  # 10% chance of error
            
            self.jobs[job_id] = {
                "completion_time": completion_time,
                "error": random.random() < error_chance
            }
            
            return {"job_id": job_id}

        @self.app.get("/status/{job_id}")
        async def get_status(job_id: str):
            if job_id not in self.jobs:
                raise HTTPException(status_code=404, detail="Job not found")
                
            job = self.jobs[job_id]
            
            if job["error"]:
                return {"result": JobStatus.ERROR}
                
            if time.time() >= job["completion_time"]:
                return {"result": JobStatus.COMPLETED}
                
            return {"result": JobStatus.PENDING}

if __name__ == "__main__":
    import uvicorn
    server = TranslationServer()
    uvicorn.run(server.app, host="0.0.0.0", port=8000) 