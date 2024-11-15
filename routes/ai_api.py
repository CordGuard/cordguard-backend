from fastapi import APIRouter, HTTPException
import logging
from cordguard_database import CordGuardAnalysisStatus, CordGuardDatabase
from cordguard_ai import OpenAIMaliciousTextDetector
logging.basicConfig(level=logging.INFO)

ai_api_endpoint_router = APIRouter(prefix="/ai/api", tags=["ai"])
HARDCODED_MAX_TOKENS = 2048

class AIDetectRequest:
    text: str
    signed_hwid: str

@ai_api_endpoint_router.get("/detect/{analysis_id}")
async def detect(request: AIDetectRequest):
    # Create the database instance
    db: CordGuardDatabase = await CordGuardDatabase.create()

    # Is it already in the database?
    ai_response = await db.get_ai_response_by_analysis_id(request.analysis_id)
    if ai_response is not None:
        return ai_response.get_dict()
    
    # Estimate tokens using rough 4 chars/token ratio for GPT models
    estimated_tokens = len(request.text) // 4
    if estimated_tokens > HARDCODED_MAX_TOKENS:
        raise HTTPException(status_code=400, detail="Text is too long - exceeds 2048 tokens")
    
    # Get machine from signed_hwid
    machine = await db.get_machine_by_signed_hwid(request.signed_hwid)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Get the analysis record
    analysis_record = await db.get_analysis_record_by_analysis_id(request.analysis_id)
    if analysis_record is None:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    # Check if the analysis record is pending
    if analysis_record.status != CordGuardAnalysisStatus.PENDING:
        raise HTTPException(status_code=400, detail="Analysis is not pending")
    
    detector = OpenAIMaliciousTextDetector()
    response = detector.detect(request.text)
    await db.save_ai_response(request.analysis_id, request.text, response.get_dict())
    return response.get_dict()