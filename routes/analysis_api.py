"""
Analysis API Router

This module provides the API endpoints for file analysis functionality.
It handles file uploads and status checks for malware analysis operations.

Routes:
    /status/{analysis_id} (GET): Check status of an analysis
    /upload (POST): Upload a file for analysis

The router integrates with S3 for file storage and maintains an analysis queue
for processing uploaded files asynchronously.

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from cordguard_globals import BUCKET_NAME_S3
from cordguard_utils import safe_read_file, safe_filename, does_file_have_extension
from cordguard_file import CordGuardAnalysisFile
import magic
from cordguard_database import CordGuardDatabase
from cordguard_database import CordGuardAnalysisStatus # TODO: This(CordGuardAnalysisStatus) should not be here, but i'm lazy to move it :P (#V0ID)

logging.basicConfig(level=logging.INFO)

analysis_api_endpoint_router = APIRouter(prefix="/analysis/api", tags=["analysis"])

@analysis_api_endpoint_router.get("/status/{analysis_id}")
async def status(analysis_id: str):
    """
    Get the status of a file analysis.

    Args:
        analysis_id (str): The unique ID of the analysis to check

    Returns:
        dict: Analysis status information
    """
    db: CordGuardDatabase = await CordGuardDatabase.create()
    analysis_record = await db.get_analysis_record_by_analysis_id(analysis_id)
    if analysis_record is None:
        raise HTTPException(status_code=404, detail="Analysis record not found")
    
    # If it's still pending, return that
    if analysis_record.status == CordGuardAnalysisStatus.PENDING:
        return {
            "message": "Analysis is pending",
            "analysis_id": analysis_id,
            "status": analysis_record.status
        }
    elif analysis_record.status == CordGuardAnalysisStatus.FAILED:
        return {
            "message": "Analysis failed, request the operator to check the file please.\nGive them the following analysis_id: " + analysis_id,
            "analysis_id": analysis_id,
            "status": analysis_record.status
        }
    elif analysis_record.status == CordGuardAnalysisStatus.COMPLETED:
        # Get results from database and form it correctly
        results = await db.get_analysis_results_by_analysis_id(analysis_id)
        if results is None:
            raise HTTPException(status_code=500, detail="Analysis results not found. Internal error.")
        # File data
        file_record = await db.get_file_record_by_file_hash(analysis_record.file_hash)
        if file_record is None:
            raise HTTPException(status_code=500, detail="File record not found. Internal error.")
        # AI response
        ai_response_record = await db.get_ai_response_by_analysis_id(analysis_id)
        if ai_response_record is None:
            raise HTTPException(status_code=500, detail="AI response not found. Internal error.")
        return {
            "message": "Analysis successful",
            "analysis_id": analysis_id,
            "status": analysis_record.status,
            "results": results.get_dict(),
            "file_data": file_record.get_safe_dict(),
            "ai_response": ai_response_record.get_dict()
        }
    else:
        raise HTTPException(status_code=500, detail="Unknown analysis status")

@analysis_api_endpoint_router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Upload a file for malware analysis.

    Accepts script files and executables up to 10MB in size.
    Files are stored in S3 and queued for asynchronous analysis.

    Args:
        file (UploadFile): The file to analyze, must be one of the accepted types

    Returns:
        dict: Upload status and analysis ID
        
    Raises:
        HTTPException: 
            400: Invalid file type or size
            500: Server error (S3 upload failed)
    """
    logging.info('File upload request received')

    # Define accepted file extensions
    list_of_accepted_file_types = [
        # Scripts
        '.py', '.sh', '.bat', '.ps1', '.psm1', '.psd1', '.vbs', '.js', '.ts',
        # Windows executables and libraries  
        '.exe', '.dll', '.com',
        # Windows scripting
        '.vb', '.cmd', '.jse', '.ws', '.wsf', '.wsc', '.wsh',
        # PowerShell specific
        '.msh', '.msh1', '.msh2', '.msh1xml', '.msh2xml',
        '.msh1script', '.msh2script', '.msh1xmlscript', '.msh2xmlscript',
        '.msh1xmlsc', '.msh2xmlsc', '.msh1xmlsrc', '.msh2xmlsrc',
        '.msh1xmlsrcsc', '.msh2xmlsrcsc'
    ]
    
    # Validate file extension
    if not file.filename.endswith(tuple(list_of_accepted_file_types)):
        logging.error('Invalid file type uploaded')
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Sanitize filename
    filename = safe_filename(file.filename)

    if not does_file_have_extension(filename):
        logging.error('File has no extension, we are unable to process this file.')
        raise HTTPException(status_code=400, detail="File has no extension, we are unable to process this file.")

    # Read and validate file content
    content = safe_read_file(file.file)
    if content is None:
        raise HTTPException(status_code=400, detail="File too large or empty")
    
    # Create analysis file object
    mime_type = file.content_type or magic.from_buffer(content, mime=True)

    # if it's ELF, we need to reject it
    if mime_type == "application/x-executable":
        raise HTTPException(status_code=400, detail="ELF files are not supported yet.")

    file_obj = CordGuardAnalysisFile(filename, mime_type, len(content), content, bucket_name_s3=BUCKET_NAME_S3, s3_client=None)

    # Check the hash if file is already in the database
    db: CordGuardDatabase = await CordGuardDatabase.create()
    file_record = await db.get_file_record_by_file_hash(file_obj.file_hash)
    if file_record is not None:
        return {
            "message": "File already in database",
            "analysis_id": file_record.analysis_id
        }
    
    # Upload to S3
    if not file_obj.upload_to_s3():
        raise HTTPException(status_code=500, detail="Failed to upload file")

    logging.info(f'File uploaded with analysis_id: {file_obj.analysis_id} and file_id: {file_obj.file_id}')

    # Create DATABASE record
    record = await db.new_analysis_for_file(file_obj)
    if record is None:
        # Delete the file from S3 or find a way to get it back or something
        raise HTTPException(status_code=500, detail="Failed to create analysis record")

    return {
        "message": "File uploaded and queued for analysis",
        "analysis_id": file_obj.analysis_id
    }
