"""
CordGuard Application Server

This module implements the main Flask application server for CordGuard, providing
malware analysis capabilities through a REST API. It handles file uploads, analysis
queuing, and worker coordination.

The server uses AWS S3 for file storage and maintains a queue for
processing analysis requests. It provides two main API routes:

- /analysis/api/: Endpoints for submitting files and checking analysis status
- /discovery/service/api/: Discovery service endpoints for worker registration and coordination
- /mission/api/: Mission service endpoints for worker coordination

Key Components:
    - Flask application server with REST API endpoints
    - S3 integration for secure file storage
    - Async queue for managing analysis workload
    - Background workers for file processing
    - Database integration for analysis results

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key for S3
    AWS_SECRET_ACCESS_KEY: AWS secret key for S3
    AWS_ENDPOINT_URL_S3: S3 endpoint URL
    AWS_REGION: AWS region for S3
    BUCKET_NAME_S3: S3 bucket name for file storage

Usage:
    Run directly:
        $ python app.py

Author: security@cordguard.org
Version: 1.0.0
"""
import logging
from fastapi import FastAPI
from routes.analysis_api import analysis_api_endpoint_router
from routes.ds_api import ds_api_endpoint_router
from routes.mission_api import mission_api_endpoint_router
from cordguard_core import init_fastapi_app
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CordGuard API",
    description="CordGuard malware analysis REST API",
    version="1.0.0"
)

@app.get("/ping")
async def ping():
    """
    Health check endpoint to verify server status.

    Returns:
        dict: Response indicating the server is alive
    """
    logger.info('Ping request received')
    return {"status": "pong"}

if __name__ == '__main__':
    # Initialize application with routers
    init_fastapi_app(app, [
        analysis_api_endpoint_router,
        ds_api_endpoint_router,
        mission_api_endpoint_router
    ])
    
    # Start background consumer thread
    # consumer_thread = threading.Thread(target=run_async_consumer, daemon=True)
    # consumer_thread.start()

    # Start FastAPI server
    uvicorn.run(app, host='0.0.0.0', port=5000)