"""
Discovery Service (DS) API Router

This module provides API endpoints for the Discovery Service (DS) which handles
VM worker registration and management.

Routes:
    /register/vm/worker (POST): Register a new VM worker node

Dependencies:
    fastapi: Web framework for API endpoints
    asyncio: Async/await support
    logging: Application logging
    cordguard_worker: Worker management models
    cordguard_database: Database interface
    cordguard_auth: Authentication utilities

Usage:
    # Register a new worker
    POST /register/vm/worker
    {
        "hwid": "worker-hardware-id",
        "signed_hwid": "signed-hardware-id-hex"
    }

Author: security@cordguard.org
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from cordguard_worker import CordguardWorker, CordguardWorkerStatus
from cordguard_database import CordGuardDatabase
from cordguard_auth import CordguardAuth

logging.basicConfig(level=logging.INFO)

ds_api_endpoint_router = APIRouter(prefix="/discovery/service/api", tags=["discovery"])

class WorkerRegistration(BaseModel):
    hwid: str
    signed_hwid: str
    public_ip: str

@ds_api_endpoint_router.post("/register/vm/worker")
async def register_vm_worker(registration: WorkerRegistration):
    """
    Register a new VM worker node with the system.
    
    Validates the worker's hardware ID signature and registers it in the database
    if not already registered.

    Args:
        registration (WorkerRegistration): Worker registration details containing:
            - hwid (str): Worker hardware ID
            - signed_hwid (str): Signed hardware ID in hex format

    Returns:
        dict: Registration status and message

    Raises:
        HTTPException: 
            400: Invalid request or signature verification failed
            500: Registration failed due to server error

    Example:
        >>> POST /register/vm/worker
        >>> {
        >>>     "hwid": "worker-123",
        >>>     "signed_hwid": "a1b2c3..."
        >>> }
        >>> Returns: {"status": "success", "message": "VM worker registered successfully"}
    """
    logging.info('Register VM worker request received')
    
    try:
        # Create worker instance with initial unsigned status
        worker = CordguardWorker(
            hwid=registration.hwid,
            public_ip=registration.public_ip,
            signed_hwid=registration.signed_hwid,
            is_signed=False,
            status=CordguardWorkerStatus.NOT_ACQUIRED
        )
        db: CordGuardDatabase = await CordGuardDatabase.create()

        # Verify worker signature
        auth = CordguardAuth()
        hwid_bytes = worker.hwid.encode('utf-8')
        signed_hwid_bytes = bytes.fromhex(worker.signed_hwid)
        
        if not auth.verify(hwid_bytes, signed_hwid_bytes):
            raise HTTPException(status_code=400, detail="VM worker is not signed")
        
        # Mark as signed and register
        worker.is_signed = True

        """
        Check if worker exists and register if new.
        Returns existing or newly registered worker.
        """
        logging.info(f'Checking if worker exists: {worker.signed_hwid}')
        db = await CordGuardDatabase.create()
        existing_worker = await db.get_worker_by_signed_hwid(worker.signed_hwid)
        if existing_worker is not None:
            return {"status": "success", "message": "VM worker already registered"}
        
        logging.info(f'Registering worker: {worker.get_dict()}')

        worker = await db.register_vm_worker(worker)

        if worker:
            logging.info(f'Worker registered: {worker.get_dict()}')
            return {"status": "success", "message": "VM worker registered successfully"}
        
        logging.error(f'Worker registration failed: {worker.get_dict()}')
        raise HTTPException(status_code=500, detail="VM worker registration failed")

    except HTTPException as e:
        logging.error(f'HTTPException registering VM worker: {e}')
        raise e
    except Exception as e:
        logging.error(f'Error registering VM worker: {e}')
        raise HTTPException(status_code=400, detail="Invalid request body")
