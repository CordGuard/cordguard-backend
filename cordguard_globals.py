"""
CordGuard Globals Module

This module defines global variables and configurations used throughout the CordGuard application.
It handles AWS S3 client initialization, logging setup, and maintains global queues and DATABASE
connections.

Author: security@cordguard.org
Version: 1.0.0
"""

import os
import boto3
# from cordguard_queue import CordGuardQueue
import logging
from dotenv import load_dotenv
import asyncio
import threading
from cordguard_database import CordGuardDatabase
# Global flag to ensure single initialization
_initialized = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def globals_initialize():
    global _initialized,\
          AWS_CONFIG, \
          BUCKET_NAME_S3
        
    if _initialized:
        return
    load_dotenv()
    # AWS Configuration
    AWS_CONFIG = {
        'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'endpoint_url': os.getenv('AWS_ENDPOINT_URL_S3'),
        'region': os.getenv('AWS_REGION')
    }

    BUCKET_NAME_S3 = os.getenv('BUCKET_NAME_S3')
     
    # Log configuration (safely handling secrets)
    logger.info(f'S3 client initialized with endpoint: {AWS_CONFIG["endpoint_url"]}')
    logger.info(f'BUCKET_NAME_S3: {BUCKET_NAME_S3}')
    logger.info(f'AWS_ACCESS_KEY_ID: {AWS_CONFIG["access_key_id"][:5]}{"*" * len(AWS_CONFIG["access_key_id"])}')
    logger.info(f'AWS_SECRET_ACCESS_KEY: {AWS_CONFIG["secret_access_key"][:5]}{"*" * len(AWS_CONFIG["secret_access_key"])}')
    logger.info(f'AWS_ENDPOINT_URL: {AWS_CONFIG["endpoint_url"]}')

    #APP_QUEUE = CordGuardQueue(maxsize=20)
     
    try:
        # Create and run a new event loop for database initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        DATABASE = loop.run_until_complete(CordGuardDatabase.create())
        loop.close()
        logger.info('Database initialized')
    except Exception as e:
        logger.error(f"Failed to initialize DB: {e}", exc_info=True)
        raise  # Re-raise the exception to prevent partial initialization

    
    _initialized = True
    logger.info('CordGuard Globals initialized')

globals_initialize()