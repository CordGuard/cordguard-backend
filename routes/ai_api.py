from fastapi import APIRouter, HTTPException, Request
import logging
from cordguard_database import CordGuardAnalysisStatus, CordGuardDatabase
from cordguard_ai import OpenAIMaliciousTextDetector
from cordguard_utils import is_sub_host
import os

logging.basicConfig(level=logging.INFO)

ai_api_endpoint_router = APIRouter(prefix="/ai/api", tags=["ai"])
HARDCODED_MAX_TOKENS = 2048

class AIDetectRequest:
    text: str
    signed_hwid: str
    analysis_id: str

@ai_api_endpoint_router.post("/detect")
async def detect(request: AIDetectRequest, full_request: Request = None):
    logging.info("Received detection request for analysis_id: %s", request.analysis_id)
    
    # Create the database instance
    db: CordGuardDatabase = await CordGuardDatabase.create()
    logging.info("Database instance created.")

    if not is_sub_host(full_request, os.getenv('AI_API_HOST', 'ai.')):
        logging.warning("Unauthorized access attempt from host: %s", full_request.client.host)
        raise HTTPException(status_code=403, detail="AI API only allowed through AI subdomain")
    
    if full_request.headers.get('x-api-key') != os.getenv('AI_API_KEY'):
        logging.warning("Invalid API key provided.")
        raise HTTPException(status_code=403, detail="Invalid AI API key")

    # Is it already in the database?
    ai_response = await db.get_ai_response_by_analysis_id(request.analysis_id)
    if ai_response is not None:
        logging.info("AI response found in database for analysis_id: %s", request.analysis_id)
        return ai_response.get_dict()
    
    # Estimate tokens using rough 4 chars/token ratio for GPT models
    estimated_tokens = len(request.text) // 4
    logging.info("Estimated tokens for the request: %d", estimated_tokens)
    
    if estimated_tokens > HARDCODED_MAX_TOKENS:
        logging.error("Text is too long - exceeds 2048 tokens")
        raise HTTPException(status_code=400, detail="Text is too long - exceeds 2048 tokens")
    
    # Get machine from signed_hwid
    machine = await db.get_machine_by_signed_hwid(request.signed_hwid)
    if machine is None:
        logging.error("Machine not found for signed_hwid: %s", request.signed_hwid)
        raise HTTPException(status_code=404, detail="Machine not found")

    # Get the analysis record
    analysis_record = await db.get_analysis_record_by_analysis_id(request.analysis_id)
    if analysis_record is None:
        logging.error("Analysis record not found for analysis_id: %s", request.analysis_id)
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    # Check if the analysis record is pending
    if analysis_record.status != CordGuardAnalysisStatus.PENDING:
        logging.error("Analysis is not pending for analysis_id: %s", request.analysis_id)
        raise HTTPException(status_code=400, detail="Analysis is not pending")
    
    detector = OpenAIMaliciousTextDetector()
    response = detector.detect(request.text)
    await db.save_ai_response(request.analysis_id, request.text, response.get_dict())
    logging.info("AI response saved for analysis_id: %s", request.analysis_id)
    return response.get_dict()