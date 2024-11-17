"""
CordGuard Database Module

This module provides the database interface for the CordGuard system, handling all database operations
for file analysis, worker management, and mission tracking.

The module uses SurrealDB as the backend database and provides an async interface for all operations.

Key Components:
-------------
- CordGuardDatabase: Main database interface class
- CordGuardAnalysisStatus: Enum-like class for analysis status states 
- CordGuardTableMetadata: Constants for database table names
- CordGuardAnalysisRecordFields: Field names for analysis records
- CordGuardFileRecord: Data model for file records
- CordGuardAnalysisRecord: Data model for analysis records
- CordguardResult: Data model for analysis results
- CordguardWorker: Data model for worker nodes
- CordguardWorkerMission: Data model for worker missions

Database Schema:
--------------
The database uses the following tables:
- files: Stores file metadata and content references
- analysis: Stores analysis records and status
- workers: Stores registered VM worker information 
- missions: Stores worker mission assignments
- results: Stores analysis results from completed missions

Dependencies:
-----------
- surrealdb: Database driver for SurrealDB
- cordguard_file: File handling models
- cordguard_worker: Worker management models
- cordguard_worker_mission: Mission tracking models
- cordguard_result: Analysis result models
- cordguard_codes: ID generation utilities
- datetime: Timestamp handling
- logging: Application logging
- re: Regular expressions for input sanitization
- json: JSON data handling

Usage:
-----
    # Create database instance
    db = await CordGuardDatabase.create()
    
    # Create new analysis
    analysis = await db.new_analysis_for_file(file)
    
    # Update analysis status
    await db.update_analysis_record_status_by_analysis_id(
        analysis.analysis_id, 
        CordGuardAnalysisStatus.COMPLETED
    )
    
    # Store analysis results
    await db.store_analysis_results(mission_id, results)

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""

from surrealdb import Surreal
from cordguard_file import CordGuardAnalysisFile
from datetime import datetime
import logging
from cordguard_worker import CordguardWorker
from cordguard_worker_mission import CordguardWorkerMission
from cordguard_worker import CordguardWorkerStatus
from cordguard_result import CordguardResult
from cordguard_codes import create_trackable_id
import re
from cordguard_ai import OpenAIResponse
import os
# Configure logging
logging.basicConfig(level=logging.INFO)

class CordGuardAnalysisStatus:
    """
    Analysis status constants used throughout the system.
    Represents the different states an analysis can be in.

    PENDING: Analysis is queued but not started
    ANALYZING: Analysis is currently in progress
    COMPLETED: Analysis has finished successfully
    FAILED: Analysis encountered an error
    """
    PENDING = 'pending'     # Analysis is queued but not started
    ANALYZING = 'analyzing' # Analysis is currently in progress
    COMPLETED = 'completed' # Analysis has finished successfully
    FAILED = 'failed'      # Analysis encountered an error

class CordGuardTableMetadata:
    """
    Database table name constants.
    Centralizes table naming to avoid string literals in code.

    ANALYSIS_NAME: Table for analysis records
    FILE_NAME: Table for file metadata
    WORKERS_NAME: Table for worker registration
    MISSIONS_NAME: Table for worker missions
    RESULTS_NAME: Table for mission results
    AI_RESPONSES_NAME: Table for AI responses
    """
    ANALYSIS_NAME = 'analysis'  # Table for analysis records
    FILE_NAME = 'files'        # Table for file metadata
    WORKERS_NAME = 'workers'    # Table for worker registration
    MISSIONS_NAME = 'missions'  # Table for worker missions
    RESULTS_NAME = 'results'   # Table for mission results
    WAITLIST_NAME = 'waitlist' # Table for waitlist entries
    AI_RESPONSES_NAME = 'ai_responses' # Table for AI responses
    
class CordGuardAnalysisRecordFields:
    """
    Field name constants for analysis records.
    Standardizes field access across the codebase.

    analysis_id: Unique identifier for the analysis record
    status: Current analysis status
    percent_complete: Progress percentage
    created_at: Timestamp of record creation
    updated_at: Timestamp of last update
    file_hash: Hash of the associated file
    """
    analysis_id = 'analysis_id'
    status = 'status'
    percent_complete = 'percent_complete'
    created_at = 'created_at'
    updated_at = 'updated_at'
    file_hash = 'file_hash'

class CordGuardWorkerFields:
    is_acquired = 'is_acquired'

class CordGuardFileRecordFields:
    id = 'id'
    file_hash = 'file_hash'
    analysis_id = 'analysis_id'
    file_id = 'file_id'
    file_name = 'file_name'
    file_full_url = 'file_full_url'
    file_extension = 'file_extension'
    file_size = 'file_size'
    file_type = 'file_type'

class CordGuardFileRecord:
    """
    Data model representing a file record in the database.
    Contains file metadata and references.
    """
    def __init__(self, 
                 id: str, 
                 file_hash: str, 
                 analysis_id: str, 
                 file_id: str, 
                 file_name: str, 
                 file_type: str, 
                 file_size: int,
                 file_extension: str,
                 file_full_url: str):
        self.id = id
        self.file_hash = file_hash
        self.analysis_id = analysis_id
        self.file_id = file_id
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.file_extension = file_extension
        self.file_full_url = file_full_url

    def get_dict(self) -> dict:
        """Convert record to dictionary format for database storage"""
        return {
            f"{CordGuardFileRecordFields.id}": self.id,
            f"{CordGuardFileRecordFields.file_hash}": self.file_hash,
            f"{CordGuardFileRecordFields.file_name}": self.file_name,
            f"{CordGuardFileRecordFields.file_full_url}": self.file_full_url,
            f"{CordGuardFileRecordFields.file_extension}": self.file_extension,
            f"{CordGuardFileRecordFields.file_size}": self.file_size,
            f"{CordGuardFileRecordFields.file_type}": self.file_type,
        }

    def get_safe_dict(self) -> dict:
        """Convert record to dictionary format for database storage, without the id and confidential data"""
        return {
            f"{CordGuardFileRecordFields.file_hash}": self.file_hash,
            f"{CordGuardFileRecordFields.file_name}": self.file_name,
            f"{CordGuardFileRecordFields.file_extension}": self.file_extension,
            f"{CordGuardFileRecordFields.file_size}": self.file_size,
            f"{CordGuardFileRecordFields.file_type}": self.file_type,
        }

class CordGuardAnalysisRecord:
    """
    Data model representing an analysis record in the database.
    Tracks the status and progress of file analysis.
    """
    def __init__(self, 
                 id: str,
                 status: str, 
                 file: CordGuardFileRecord,
                 file_hash: str,
                 percent_complete: int,
                 created_at: datetime,
                 updated_at: datetime,
                 analysis_id: str = ""):
        self.id = id.removeprefix(CordGuardTableMetadata.ANALYSIS_NAME + ':') if id else ""
        self.analysis_id = analysis_id if analysis_id else self.id
        self.status = status
        self.file = file
        self.file_hash = file_hash
        self.percent_complete = percent_complete
        self.created_at = created_at
        self.updated_at = updated_at

    def get_dict(self) -> dict:
        """Convert record to dictionary format for database storage"""
        return {
            f"{CordGuardAnalysisRecordFields.status}": self.status,
            f"{CordGuardAnalysisRecordFields.percent_complete}": self.percent_complete,
            f"{CordGuardAnalysisRecordFields.created_at}": str(self.created_at),
            f"{CordGuardAnalysisRecordFields.updated_at}": str(self.updated_at),
            f"{CordGuardAnalysisRecordFields.file_hash}": f"{self.file_hash}", # it will be file:hash_here
        }

class CordGuardDatabase:
    """
    CordGuardDatabase class for interacting with the database.
    Its initialization is handled by the factory method create()

    This class provides an interface to interact with a SurrealDB database for storing
    and managing analysis records. It uses an async factory pattern for initialization.

    Attributes:
        surreal_db: The SurrealDB client connection instance

    Example:
        >>> db = await CordGuardDatabase.create()
        >>> analysis = await db.new_analysis_for_file(file)
        >>> status = await db.update_analysis_record_status_by_analysis_id(id, new_status)
    """
    def __init__(self):
        """Initialize an empty database instance. Use create() instead of calling directly."""
        self.surreal_db: Surreal | None = None

    def _sanitize_input(self, value: str) -> str:
        """Sanitize input to prevent SQL injection"""
        if not isinstance(value, str):
            return value
        # Remove any non-alphanumeric characters except underscores and hyphens
        return re.sub(r'[^a-zA-Z0-9_\-]', '', value)

    @classmethod
    async def create(cls) -> 'CordGuardDatabase':
        """Factory method to create and initialize the database connection
        
        Returns:
            CordGuardDatabase: A new database instance with an initialized connection

        Raises:
            Exception: If database connection or initialization fails
        """
        db = cls()
        await db._init_surreal_db()
        logging.info("Database instance created and initialized.")
        return db
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Test the database connection"""
        db = cls()
        await db._init_surreal_db()
        logging.info("Database connection tested successfully.")
        return True

    async def _init_surreal_db(self):
        """Initialize the SurrealDB connection and authenticate
        
        Sets up the websocket connection to SurrealDB, authenticates with root credentials,
        and selects the cordguard namespace and database.
        
        Raises:
            Exception: If connection, authentication or database selection fails
        """
        SURREALDB_URL = os.getenv('SURREALDB_URL')
        self.surreal_db = Surreal(SURREALDB_URL)

        logging.info(f'Initializing SurrealDB connection at {SURREALDB_URL}')
        await self.surreal_db.connect()
        SURREALDB_USERNAME = os.getenv('SURREALDB_USERNAME')
        SURREALDB_PASSWORD = os.getenv('SURREALDB_PASSWORD')
        if SURREALDB_USERNAME is None or SURREALDB_PASSWORD is None:
            logging.error('SurrealDB credentials not found')
            raise Exception('SurrealDB credentials not found')
        await self.surreal_db.signin({'user': SURREALDB_USERNAME, 'pass': SURREALDB_PASSWORD})
        await self.surreal_db.use('cordguard', 'guard')

        # Try to create tables if they don't exist
        try:
            await self.surreal_db.query(f"""
                DEFINE TABLE {CordGuardTableMetadata.FILE_NAME};
                DEFINE TABLE {CordGuardTableMetadata.ANALYSIS_NAME};
                DEFINE TABLE {CordGuardTableMetadata.WORKERS_NAME};
                DEFINE TABLE {CordGuardTableMetadata.MISSIONS_NAME};
                DEFINE TABLE {CordGuardTableMetadata.RESULTS_NAME};
                DEFINE TABLE {CordGuardTableMetadata.WAITLIST_NAME};
                DEFINE TABLE {CordGuardTableMetadata.AI_RESPONSES_NAME};
            """)
            logging.info('Database initialized with tables successfully.')
        except Exception as e:
            logging.warning(f"Tables may already exist: {e}")
            pass
            
        logging.info('SurrealDB initialized')
    
    async def create_file_record(self, file: CordGuardAnalysisFile) -> CordGuardFileRecord | None:
        sanitized_hash = self._sanitize_input(file.file_hash)
        record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.FILE_NAME}:{sanitized_hash}', 
            file.get_dict()
        )
        logging.info(f'File record created for hash: {sanitized_hash}')
        return CordGuardFileRecord(**record) if record else None

    async def get_file_record_by_file_hash(self, file_hash: str) -> CordGuardFileRecord | None:
        if ':' in file_hash:
            file_hash = file_hash.split(':')[1]
        record = await self.surreal_db.select(
            f'{CordGuardTableMetadata.FILE_NAME}:{file_hash}'
        )   
        logging.info(f'File record retrieved for hash: {file_hash}')
        return CordGuardFileRecord(**record) if record else None

    async def new_analysis_for_file(self, cordguard_file: CordGuardAnalysisFile) -> CordGuardAnalysisRecord | None:
        """
        Create a new analysis record in the database for a given file.

        Args:
            cordguard_file (CordGuardAnalysisFile): The file object to create an analysis record for.
                                                   Must have an analysis_id property.

        Returns:
            CordGuardAnalysisRecord | None: The created analysis record if successful, containing:
                - analysis_id: Unique identifier for the analysis
                - status: Current analysis status (starts as 'pending') 
                - percent_complete: Progress percentage (starts at 0)
                - created_at: Timestamp of record creation
                - updated_at: Timestamp of last update
            Returns None if record creation fails.

        Example:
            >>> file = CordGuardAnalysisFile(...)
            >>> record = await db.new_analysis_for_file(file)
            >>> if record:
            >>>     print(record.status)
            'pending'
        """

        # Check if the file already exists in the database
        file_record = await self.get_file_record_by_file_hash(cordguard_file.file_hash)
        if file_record:

            # Change the file object to the file record from the database
            cordguard_file = file_record

            logging.info(f'File already exists in the database: {cordguard_file.file_hash}')
            # Get the analysis_id from the file record
            analysis_record = await self.get_analysis_record_by_analysis_id(file_record.analysis_id, file_record)
            if analysis_record:
                logging.info(f'The file exists, and has an analysis record already.')
                return analysis_record
            logging.info(f'The file exists, but there is no analysis process for it')
            logging.info(f'Creating new analysis record for file: {cordguard_file.file_hash}')
        else:
            logging.info(f'File does not exist in the database, creating new file record.')
            # Create a file record in the database
            file_record = await self.create_file_record(cordguard_file)
            if file_record is None:
                logging.error(f'Failed to create file record for file: {cordguard_file.file_hash}')
                return None
            logging.info(f'File record created: {file_record}')
            logging.info(f'Creating new analysis record for file: {cordguard_file.file_hash}')

        created_at = datetime.now()
        updated_at = datetime.now()
        sanitized_analysis_id = self._sanitize_input(cordguard_file.analysis_id)
        sanitized_file_hash = self._sanitize_input(file_record.file_hash)
        
        analysis_record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.ANALYSIS_NAME}:{sanitized_analysis_id}', 
            {
                f'{CordGuardAnalysisRecordFields.status}':               f'{CordGuardAnalysisStatus.PENDING}',
                f'{CordGuardAnalysisRecordFields.percent_complete}':     0,
                f'{CordGuardAnalysisRecordFields.created_at}':           f'{created_at}',
                f'{CordGuardAnalysisRecordFields.updated_at}':           f'{updated_at}',
                f'{CordGuardAnalysisRecordFields.file_hash}':            f'{CordGuardTableMetadata.FILE_NAME}:{sanitized_file_hash}',
        }
        )
        logging.info(f'Analysis record created: {analysis_record}')
        return CordGuardAnalysisRecord(file=file_record, analysis_id=cordguard_file.analysis_id, **analysis_record) if analysis_record else None
    
    async def update_analysis_record_status_by_analysis_id(self, analysis_record: CordGuardAnalysisRecord, status: CordGuardAnalysisStatus) -> bool:
        """
        Update the status of an analysis record in the database.

        Args:
            analysis_id (str): The unique identifier of the analysis record to update
            status (CordGuardAnalysisStatus): The new status to set for the record

        Returns:
            bool: True if the record was updated successfully, False otherwise
            None: If no record is found with the given analysis_id

        Example:
            >>> record = await db.update_analysis_record_status_by_analysis_id(
            ...     "cordguard_abc123", 
            ...     CordGuardAnalysisStatus.COMPLETED
            ... )
            >>> if record:
            >>>     print(record.status)
            'completed'
        """
        sanitized_analysis_id = self._sanitize_input(analysis_record.analysis_id)
        analysis_record.updated_at = datetime.now()
        analysis_record.status = status
        record = await self.surreal_db.update(
            f'{CordGuardTableMetadata.ANALYSIS_NAME}:{sanitized_analysis_id}', 
            analysis_record.get_dict()
        )
        logging.info(f'Analysis record updated: {record}')
        return True if record else False

    async def get_analysis_record_by_analysis_id(self, analysis_id: str, file_record: CordGuardFileRecord = None) -> CordGuardAnalysisRecord | None:
        sanitized_analysis_id = self._sanitize_input(analysis_id)
        # Get the analysis record from the database
        record = await self.surreal_db.select(f'{CordGuardTableMetadata.ANALYSIS_NAME}:{sanitized_analysis_id}')
        if not record:
            logging.warning(f'No analysis record found for ID: {sanitized_analysis_id}')
            return None
        
        # Get the file record from the database if not provided
        if file_record is None:
            file_record = await self.get_file_record_by_file_hash(record['file_hash'])

        # Create and return the analysis record
        logging.info(f'Analysis record retrieved: {record}')
        return CordGuardAnalysisRecord(
            id=record.get('id', ''),
            status=record.get('status', ''),
            file=file_record,
            file_hash=record.get('file_hash', ''),
            percent_complete=record.get('percent_complete', 0),
            created_at=record.get('created_at', datetime.now()),
            updated_at=record.get('updated_at', datetime.now()),
            analysis_id=analysis_id
        )
    
    async def get_any_pending_analysis(self, file_record: CordGuardFileRecord = None) -> CordGuardAnalysisRecord | None:
        """
        Get any pending analysis
        """
        record = await self.surreal_db.query(
            f"SELECT * FROM {CordGuardTableMetadata.ANALYSIS_NAME} WHERE status = '{CordGuardAnalysisStatus.PENDING}' LIMIT 1",
        )
        if record is None:
            logging.info('No pending analysis found.')
            return None
        try:
            record = record[0]["result"][0]
        except Exception as e:
            logging.error(f'Error getting pending analysis: {e}, probably no pending analysis')
            return None
        logging.info(f'Pending analysis record retrieved: {record}')
        # Get the file record from the database if not provided
        if file_record is None and record is not None:
            file_record = await self.get_file_record_by_file_hash(record['file_hash'])

        return CordGuardAnalysisRecord(file=file_record, **record) if record else None

    async def register_vm_worker(self, worker: CordguardWorker) -> CordguardWorker | None:
        """
        Register a new VM worker in the database
        
        Args:
            worker (CordguardWorker): The worker to register
            
        Returns:
            CordguardWorker | None: The registered worker if successful, containing:
                - hwid: The worker's hardware ID
                - signed_hwid: The worker's signed hardware ID
                - mission_status: The worker's mission status
                - public_ip: The worker's public IP address
                - is_signed: Whether the worker's hardware ID is signed
        """
        sanitized_hwid = self._sanitize_input(worker.signed_hwid)
        record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.WORKERS_NAME}:{sanitized_hwid}', 
            worker.get_dict()
        )
        logging.info(f'Worker registered: {sanitized_hwid}')
        return worker if record else None
    
    async def get_worker_by_signed_hwid(self, signed_hwid: str) -> CordguardWorker | None:
        """
        Get a worker from the database by signed hardware ID
        
        Args:
            signed_hwid (str): The signed hardware ID to look up

        Returns:
            CordguardWorker | None: The worker if found, None otherwise
        """
        sanitized_hwid = self._sanitize_input(signed_hwid)
        record = await self.surreal_db.select(f'{CordGuardTableMetadata.WORKERS_NAME}:{sanitized_hwid}')
        
        if not record:
            logging.warning(f'No worker found for signed HWID: {sanitized_hwid}')
            return None
            
        logging.info(f'Found worker record: {record}')
        
        # Clean up internal DB fields before creating worker object
        worker_data = record.copy()
        is_acquired = worker_data.pop('is_acquired', False)
        worker_data.pop('id', None)
        
        # Set status based on acquisition state
        status = (CordguardWorkerStatus.ACQUIRED if is_acquired 
                 else CordguardWorkerStatus.NOT_ACQUIRED)
        
        return CordguardWorker(**worker_data, status=status)

    async def set_worker_acquired_status(self, worker: CordguardWorker, acquired: bool) -> CordguardWorker | None:
        """
        Update the status of a worker in the database.
        """
        sanitized_hwid = self._sanitize_input(worker.signed_hwid)
        worker.set_acquired(acquired) 
        worker = await self.surreal_db.update(
            f'{CordGuardTableMetadata.WORKERS_NAME}:{sanitized_hwid}', 
            worker.get_dict()
        )
        if worker:
            logging.info(f'Worker status updated: {sanitized_hwid}, acquired: {acquired}')
            del worker['id']
            is_acquired = worker.pop('is_acquired', False)
            status = (CordguardWorkerStatus.ACQUIRED if is_acquired 
                     else CordguardWorkerStatus.NOT_ACQUIRED)
            return CordguardWorker(**worker, status=status)
        logging.error(f'Failed to update worker status for: {sanitized_hwid}')
        return None
    
    async def create_mission_for_worker(self, worker: CordguardWorker, analysis: CordGuardAnalysisFile) -> CordguardWorkerMission | None:
        """
        Create a new mission for a worker in the database
        
        Args:
            worker (CordguardWorker): The worker to create a mission for
            mission (CordguardWorkerMission): The mission to create
            
        Returns:
            CordguardWorkerMission | None: The created mission if successful, containing:
        """
        analysis_record = await self.get_analysis_record_by_analysis_id(analysis.analysis_id)
        if analysis_record is None:
            logging.error(f'Analysis record not found for analysis: {analysis.analysis_id}')
            return None
        
        file_record = await self.get_file_record_by_file_hash(analysis_record.file_hash)
        if file_record is None:
            logging.error(f'File record not found for analysis: {analysis_record.file_hash}')
            return None
        
        mission = CordguardWorkerMission(worker, analysis_record, file_record)

        record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.MISSIONS_NAME}:{worker.signed_hwid}', 
            mission.get_dict()
        )
        logging.info(f'Mission created for worker: {worker.signed_hwid}')
        return mission if record else None
    
    async def get_mission_by_worker_signed_hwid(self, signed_hwid: str) -> CordguardWorkerMission | None:
        """
        Get a mission from the database by worker signed hardware ID
        """
        record = await self.surreal_db.select(f'{CordGuardTableMetadata.MISSIONS_NAME}:{signed_hwid}')
        if record is None:
            logging.warning(f'No mission found for worker signed HWID: {signed_hwid}')
            return None
        analysis_record = await self.get_analysis_record_by_analysis_id(record['file']['analysis_id'])
        if analysis_record is None:
            logging.warning(f'No analysis record found for mission: {record}')
            return None
        file_record = await self.get_file_record_by_file_hash(analysis_record.file_hash)
        if file_record is None:
            logging.warning(f'No file record found for analysis: {analysis_record.file_hash}')
            return None
        del record['id']

        worker = await self.get_worker_by_signed_hwid(signed_hwid)
        if worker is None:
            logging.warning(f'No worker found for signed HWID: {signed_hwid}')
            return None

        logging.info(f'Mission retrieved for worker: {signed_hwid}')
        return CordguardWorkerMission(worker=worker, analysis=analysis_record, file=file_record) if record else None
    
    async def create_result_for_mission(self, analysis_id: str, result: dict) -> dict | None:
        """
        Create a result for a mission in the database
        """
        
        # Create record with proper dictionary structure
        record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.RESULTS_NAME}:{analysis_id}', 
            {
                'result_data': result,
                'created_at': str(datetime.now())
            }
        )
        logging.info(f'Result created for mission: {analysis_id}')
        return result if record else None

    async def get_analysis_results_by_analysis_id(self, analysis_id: str) -> CordguardResult | None:
        """
        Get the results of an analysis by analysis_id
        """
        sanitized_analysis_id = self._sanitize_input(analysis_id)
        record = await self.surreal_db.select(f'{CordGuardTableMetadata.RESULTS_NAME}:{sanitized_analysis_id}')
        logging.info(f'Analysis results retrieved for ID: {sanitized_analysis_id}')
        return CordguardResult.from_dict(record['result_data']) if record else None
    
    async def create_waitlist_entry(self, feature: str, email: str) -> bool:
        """
        Create a waitlist entry in the database
        """
        record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.WAITLIST_NAME}:{feature}', 
            {'email': email}
        )
        logging.info(f'Waitlist entry created for feature: {feature}, email: {email}')
        return True if record else False
    
    async def save_ai_response(self, analysis_id: str, analyzed_text: str, ai_response: dict) -> bool:
        """
        Save the AI response to the database
        """
        record = await self.surreal_db.create(
            f'{CordGuardTableMetadata.AI_RESPONSES_NAME}:{analysis_id}', 
            {'analyzed_text': analyzed_text, 'ai_response': ai_response}
        )
        logging.info(f'AI response saved for analysis ID: {analysis_id}')
        return True if record else False
    
    async def get_ai_response_by_analysis_id(self, analysis_id: str) -> OpenAIResponse | None:
        """
        Get the AI response by analysis_id
        """
        record = await self.surreal_db.select(f'{CordGuardTableMetadata.AI_RESPONSES_NAME}:{analysis_id}')
        logging.info(f'AI response retrieved for analysis ID: {analysis_id}')
        openai_response = OpenAIResponse.from_dict(record['ai_response']) if record else None
        return openai_response if record else None