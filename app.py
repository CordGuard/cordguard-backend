"""
CordGuard Application Server

This module implements the main FastAPI application server for CordGuard, providing
malware analysis capabilities through a REST API. It handles file uploads, analysis and
worker coordination.

The server uses AWS S3 for secure file storage and SurrealDB for data persistence.
It provides three main API routes:

- /analysis/api/: Endpoints for submitting files and checking analysis status
- /discovery/service/api/: Discovery service endpoints for worker registration and coordination 
- /mission/api/: Mission service endpoints for worker task coordination

Key Components:
    - FastAPI application server with REST API endpoints
    - S3 integration for secure file storage
    - SurrealDB for data persistence and queuing
    - Distributed VM workers for file analysis
    - Ed25519 cryptographic signatures for worker authentication

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key for S3
    AWS_SECRET_ACCESS_KEY: AWS secret key for S3 
    AWS_ENDPOINT_URL_S3: S3 endpoint URL
    AWS_REGION: AWS region for S3
    BUCKET_NAME_S3: S3 bucket name for file storage

Usage:
    Run directly:
        $ python app.py
    
    The server will start on port 5000

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""
import logging
from fastapi import FastAPI
from routes.analysis_api import analysis_api_endpoint_router
from routes.discovery_service_api import ds_api_endpoint_router
from routes.mission_api import mission_api_endpoint_router
from cordguard_core import init_fastapi_app
import uvicorn
from cordguard_database import CordGuardDatabase
from pydantic import BaseModel
from fastapi import HTTPException, Request
from cordguard_utils import is_sub_host
import os
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CordGuard API",
    description="CordGuard malware analysis REST API",
    version="1.0.0"
)

# Initialize application with routers
logger.info('Initializing application with routers')
app = init_fastapi_app(app, [
    analysis_api_endpoint_router,
        ds_api_endpoint_router,
        mission_api_endpoint_router
])
    

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions and log request details
    """
    logger.error(f"""
    404 Error Details:
    URL: {request.url}
    Method: {request.method}
    Headers: {request.headers}
    Client Host: {request.client.host}
    Path Params: {request.path_params}
    Query Params: {request.query_params}
    """)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found on this server",
            "path": str(request.url),
            "method": request.method
        }
    )

@app.get("/ping")
async def ping(request: Request = None):
    """
    Health check endpoint to verify server status.

    Returns:
        dict: Response indicating the server is alive
    """
    logger.info('Ping request received')
    # Extract subdomain from request
    subdomain = request.headers.get('host').split('.')[0]
    logger.debug(f'Extracted subdomain: {subdomain}')
    try:
        await CordGuardDatabase.test_connection()
        logger.info('Database connection successful')
    except Exception as e:
        logger.error(f'Database connection failed: {e}')
        return {"status": "pong", "subdomain": subdomain, "database_works": False}
    return {"status": "pong", "subdomain": subdomain, "database_works": True}


class WaitlistEntry(BaseModel):
    email: str
    feature: str

@app.post("/feature/join-waitlist")
async def join_waitlist(request: WaitlistEntry, full_request: Request = None):
    """
    Join the waitlist for a feature
    """
    logger.info(f'Join waitlist request received for feature: {request.feature} from email: {request.email}')
    
    if not is_sub_host(full_request, os.getenv('GENERIC_HOST', 'generic.')):
        logger.warning('Access denied: Generic API only allowed through generic subdomain')
        raise HTTPException(status_code=403, detail="Generic API only allowed through generic subdomain")
    
    if full_request.headers.get('x-api-key') != os.getenv('GENERIC_API_KEY'):
        logger.warning('Access denied: Invalid Generic API key')
        raise HTTPException(status_code=403, detail="Invalid Generic API key")
    
    db: CordGuardDatabase = await CordGuardDatabase.create()
    record = await db.create_waitlist_entry(request.feature, request.email)
    logger.info(f'Waitlist entry created: {record}')
    return {"success": record}

if __name__ == '__main__':
 
    # Start background consumer thread
    # consumer_thread = threading.Thread(target=run_async_consumer, daemon=True)
    # consumer_thread.start()

    PORT = os.getenv('PORT')
    if not PORT:
        logger.error("PORT environment variable is not set")
        raise ValueError("PORT environment variable is not set")
    logger.info(f'Starting FastAPI server on port {PORT}')
    # Start FastAPI server
    uvicorn.run(app, host='0.0.0.0', port=PORT)