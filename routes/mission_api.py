"""
Mission API Router

This module provides API endpoints for managing worker missions and results.
It handles mission assignment and result collection from VM workers.

Routes:
    /get/mission (POST): Get a new mission for a worker
    /set/result (POST): Submit analysis results for a mission

Dependencies:
    fastapi: Web framework for API endpoints
    asyncio: Async/await support
    logging: Application logging
    cordguard_worker: Worker management models
    cordguard_database: Database interface
    cordguard_auth: Authentication utilities

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""

import logging
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from cordguard_auth import CordguardAuth
from cordguard_database import CordGuardDatabase, CordGuardAnalysisStatus
from cordguard_worker_mission import CordguardWorkerMission
from cordguard_worker import CordguardWorker
from cordguard_result import CordguardResult
from cordguard_utils import is_sub_host

mission_api_endpoint_router = APIRouter(prefix="/mission/api", tags=["mission"])


class MissionGetRequest(BaseModel):
    """
    Data model for mission request payload.
    """
    signed_hwid: str
    hwid: str

# TODO: This endpoint("/mission/api/get") is used by the VM worker to get a new mission, it should be a websocket as it's in the state
#       can be low latency and low bandwidth, cost and operational for a long time.
#       This will work for now.
@mission_api_endpoint_router.post("/get")
async def get_mission(mission_request: MissionGetRequest, request: Request = None):
    """
    Get a new mission for a VM worker.
    
    Validates worker authentication and assigns a pending analysis as a new mission.
    
    Args:
        mission_request (MissionGetRequest): Request containing worker credentials
            
    Returns:
        dict: Mission details if successful
        
    Raises:
        HTTPException:
            400: Invalid request, worker already busy, or no pending analysis
        
    Example:
        >>> POST /get/mission
        >>> {
        >>>     "signed_hwid": "abc123...",
        >>>     "hwid": "worker1"
        >>> }
        >>> Returns: {"mission_id": "...", "analysis_id": "..."}
    """
    logging.info(f'Get mission request received: {mission_request.signed_hwid}')
    db: CordGuardDatabase = await CordGuardDatabase.create()

    if os.getenv('DEBUG') == 'true':
        logging.info('DEBUG is true, skipping host check')
    else:
        if not is_sub_host(request, os.getenv('WORKER_HOST', 'workers.')):
            logging.warning("Unauthorized access attempt from host: %s", request.client.host)
            raise HTTPException(status_code=403, detail="Worker API only allowed through workers subdomain")
    
        if request.headers.get('x-api-key') != os.getenv('WORKER_API_KEY'):
            logging.warning("Invalid Worker API key provided.")
            raise HTTPException(status_code=403, detail="Invalid Worker API key")
    
    worker = await db.get_worker_by_signed_hwid(mission_request.signed_hwid)
    if worker is None:
        logging.error("Invalid request, worker not found for signed_hwid: %s", mission_request.signed_hwid)
        raise HTTPException(status_code=400, detail="Invalid request, worker not found")
    
    # Verify worker is available
    if worker.is_acquired():
        logging.info("Worker %s is already acquired.", worker.signed_hwid)
        mission = await db.get_mission_by_worker_signed_hwid(worker.signed_hwid)
        if mission is not None:
            logging.info("Returning existing mission for worker %s.", worker.signed_hwid)
            return mission.get_mission_response()
        logging.error("Worker is acquired but no mission assigned. Contact support.")
        raise HTTPException(status_code=500, detail="Worker is acquired but no mission assigned. Contact support.")
    
    # Verify worker signature
    auth = CordguardAuth()
    hwid_bytes = mission_request.hwid.encode('utf-8')
    signed_hwid_bytes = bytes.fromhex(mission_request.signed_hwid)
    
    if not auth.verify(hwid_bytes, signed_hwid_bytes):
        logging.error("Signature verification failed for worker: %s", mission_request.hwid)
        raise HTTPException(status_code=400, detail="VM worker is not signed")
    
    worker.is_signed = True
    logging.info("Worker %s is now marked as signed.", worker.signed_hwid)

    async def handle_request_and_get_mission(worker: CordguardWorker) -> CordguardWorkerMission | None:
        """
        Find and assign a pending analysis to the worker.
        
        Returns:
            CordguardWorkerMission | None: Created mission if successful
        """

        # TODO: To ensure atomicity, create a transaction method/solution. | Not important now due to very small scale

        # Get pending analysis
        analysis = await db.get_any_pending_analysis()
        if analysis is None:
            logging.info("No pending analysis found for worker %s.", worker.signed_hwid)
            return None
        
        logging.info("Found pending analysis for worker %s: %s", worker.signed_hwid, analysis.analysis_id)
        
        # Update analysis status
        analysis_updated = await db.update_analysis_record_status_by_analysis_id(
            analysis, 
            CordGuardAnalysisStatus.ANALYZING
        )
        if not analysis_updated:
            logging.error("Failed to update analysis status for analysis_id: %s", analysis.analysis_id)
            return None
        
        # Update worker status
        worker_updated = await db.set_worker_acquired_status(worker, True)
        if not worker_updated:
            logging.error("Failed to update worker status for signed_hwid: %s", worker.signed_hwid)
            return None
        
        # Create mission assignment
        mission = await db.create_mission_for_worker(worker, analysis)
        logging.info("Mission created for worker %s with analysis_id: %s", worker.signed_hwid, analysis.analysis_id)
        return mission

    mission = await handle_request_and_get_mission(worker)
    
    if mission is None:
        logging.error("No pending analysis found for worker %s.", worker.signed_hwid)
        raise HTTPException(status_code=400, detail="No pending analysis found")
    
    logging.info("Returning mission response for worker %s.", worker.signed_hwid)
    return mission.get_mission_response()


@mission_api_endpoint_router.post("/set/result")
async def set_result(result: CordguardResult, request: Request = None):
    """
    Submit analysis results for a completed mission.
    
    Args:
        result (CordguardResult): Analysis results data
            
    Returns:
        dict: Success message
        
    Example:
        >>> POST /set/result 
        >>> {
        >>>     "analysis_id": "abc123",
        >>>     "type": "static",
        >>>     ...
        >>> }
        >>> Returns: {"message": "Results received"}
    """
    logging.info('Set result request received for analysis_id: %s', result.analysis_id)
    
    if os.getenv('DEBUG') == 'true':
        logging.info('DEBUG is true, skipping host check')
    else:
        if not is_sub_host(request, os.getenv('WORKER_HOST', 'workers.')):
            logging.warning("Unauthorized access attempt from host: %s", request.client.host)
            raise HTTPException(status_code=403, detail="Worker API only allowed through workers subdomain")
    
        if request.headers.get('x-api-key') != os.getenv('WORKER_API_KEY'):
            logging.warning("Invalid Worker API key provided.")
            raise HTTPException(status_code=403, detail="Invalid Worker API key")
    
    # Set result in database
    db: CordGuardDatabase = await CordGuardDatabase.create()
    analysis_record = await db.get_analysis_record_by_analysis_id(result.analysis_id)
    if analysis_record is None:
        logging.error("Analysis not found for analysis_id: %s", result.analysis_id)
        return {"message": "Analysis not found"}
    
    # Set analysis to completed or failed based on results
    if result.type == "unknown":
        logging.info("Setting analysis status to FAILED for analysis_id: %s", result.analysis_id)
        analysis_updated = await db.update_analysis_record_status_by_analysis_id(
            analysis_record,
            CordGuardAnalysisStatus.FAILED
        )
    else:
        logging.info("Setting analysis status to COMPLETED for analysis_id: %s", result.analysis_id)
        analysis_updated = await db.update_analysis_record_status_by_analysis_id(
            analysis_record,
            CordGuardAnalysisStatus.COMPLETED
        )
    
    if not analysis_updated:
        logging.error("Failed to update analysis status for analysis_id: %s", result.analysis_id)
        return {"message": "Failed to update analysis status"}
    
    # Update machine state to not acquired
    worker = await db.get_worker_by_signed_hwid(result.signed_hwid)
    if worker is None:
        logging.error("Worker not found for signed_hwid: %s", result.signed_hwid)
        return {"message": "Worker not found"}
    
    worker_updated = await db.set_worker_acquired_status(worker, False)
    if not worker_updated:
        logging.error("Failed to update worker state for signed_hwid: %s", result.signed_hwid)
        return {"message": "Failed to update worker state"}

    # Create result in database
    result_created = await db.create_result_for_mission(result.analysis_id, result.get_dict())
    if not result_created:
        logging.error("Failed to create result for analysis_id: %s", result.analysis_id)
        return {"message": "Failed to create result"}

    logging.info("Results received for analysis_id: %s", result.analysis_id)
    return {"message": "Results received"}