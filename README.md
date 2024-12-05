# Video Translation Process Example

## Setup and Installation

1. Create and activate virtual environment:
```bash

# Create virtual environment
python -m venv venv


# Activate on MacOS
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```


## Running the Application

1. First, start the server in one terminal:
```bash
# Make sure your virtual environment is activated
python -m src.server.translation_server
```
It starts the FastAPI server on http://localhost:8000

2. In a new terminal, run the example:
```bash
# Make sure your virtual environment is activated
python examples/example.py
```

## Understanding the Components

### 1. Server (translation_server.py)
- Simulates a video translation service
- Provides two endpoints:
  - POST /jobs: Create new translation job
  - GET /status/{job_id}: Check job status
- Simulates random completion times and occasional errors

### 2. Client Library (translation_client.py)
- Provides a user-friendly interface to the translation service
- Features:
  - Smart polling with exponential backoff
  - Status change notifications via callbacks
  - Automatic retry handling
  - Resource cleanup via context manager

### 3. Usage Example (example.py)
Demonstrates typical usage of the client library:
```python
async with TranslationClient("http://localhost:8000") as client:
    job_id = await client.create_job(video_length=10)
    
    # Monitor status with callbacks
    final_status = await client.get_status(
        job_id,
        on_status_change=lambda status: print(f"Status: {status}"),
        on_completion=lambda data: print(f"Complete: {data}")
    )
```


### 4. Integration Testing (test_integration.py)
Tests the entire system end-to-end:
```bash
# Run integration tests
pytest tests/test_integration.py -v
```

The test:
- Creates a test server instance
- Sets up a client with faster polling
- Creates and monitors a test job
- Verifies correct status transitions
- Ensures proper resource cleanup

Test output example:
```
tests/test_integration.py::test_translation_flow 
INFO:__main__:Created job with ID: 4f69cc76-5b9f-4b46-a514-bdd2c0e3314a
INFO:__main__:Status changed to: pending
INFO:__main__:Status changed to: completed
INFO:__main__:Job completed with data: {'result': 'completed'}
PASSED
```

## Client Library Configuration

When creating a TranslationClient, you can configure:
- `initial_delay`: Starting delay between status checks (default: 1.0s)
- `max_delay`: Maximum delay between checks (default: 30.0s)
- `backoff_factor`: How quickly delay increases (default: 1.5)
- `max_retries`: Maximum retry attempts (default: 7)
- `timeout`: Overall timeout (default: 250s)

Example:
```python
client = TranslationClient(
    base_url="http://localhost:8000",
    initial_delay=0.5,  # Start with 0.5s delay
    max_delay=5.0,      # Never wait more than 5s
    backoff_factor=2.0  # Double delay after each check
)
```

## Error Handling

The client library handles various error scenarios:
- Network errors (with automatic retries)
- Invalid responses
- Timeouts
- Server errors


