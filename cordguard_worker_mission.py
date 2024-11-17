"""
CordGuard Worker Mission Module

This module defines the data model for worker missions, including statuses and mission details.

Classes:
    CordguardWorkerMission: Represents a mission assigned to a VM worker

Dependencies:
    cordguard_worker: Worker management models
    cordguard_file: File handling models 
    cordguard_codes: ID generation utilities

Usage:
    mission = CordguardWorkerMission(worker, analysis)
    mission_dict = mission.get_dict()
    response = mission.get_mission_response()

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""
import logging
from cordguard_worker import CordguardWorker
from cordguard_file import CordGuardAnalysisFile 

from cordguard_codes import create_trackable_id

# from cordguard_database import CordGuardAnalysisRecord, CordGuardFileRecord
#TODO: Lazy solution to avoid circular import issues, fix later by moving types of records to a separate file
class CordGuardAnalysisRecord:
    pass
class CordGuardFileRecord:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CordguardWorkerMission:
    """
    Class representing a mission for a VM worker.
    
    A mission links a worker to an analysis task and tracks the execution status.

    Attributes:
        mission_id (str): Unique identifier for this mission
        worker (CordguardWorker): The worker assigned to this mission
        analysis (CordGuardAnalysisFile): The analysis task to be performed

    Args:
        worker (CordguardWorker): Worker to assign the mission to
        analysis (CordGuardAnalysisFile): Analysis task for the mission
    """
    
    def __init__(self, worker: CordguardWorker, analysis: CordGuardAnalysisRecord, file: CordGuardFileRecord, mission_id: str = create_trackable_id()):
        self.mission_id = mission_id
        self.worker = worker
        self.analysis = analysis
        self.file = file
        logger.info(f'Initialized CordguardWorkerMission with mission_id: {self.mission_id}')

    def __str__(self) -> str:
        return f'CordguardWorkerMission(mission_id={self.mission_id}, worker={self.worker}, analysis={self.analysis})'

    # @staticmethod
    # def from_dict(data: dict) -> 'CordguardWorkerMission':
    #     return CordguardWorkerMission(worker=CordguardWorker.from_dict(data['worker']), analysis=CordGuardAnalysisFile.from_dict(data['analysis']))

    def get_dict(self) -> dict:
        """
        Convert mission to dictionary format for database storage.

        Returns:
            dict: Mission data dictionary containing:
                - mission_id: Unique mission identifier
                - worker: Worker details dictionary
                - analysis: Analysis details dictionary

        Example:
            >>> mission_dict = mission.get_dict()
            >>> print(mission_dict['mission_id'])
            'mission_abc123'
        """
        mission_dict = {
            'mission_id': self.mission_id,
            'worker': self.worker.get_dict(),
            'analysis': self.analysis.get_dict(),
            'file': self.file.get_dict()
        }
        logger.info(f'Converted mission to dictionary: {mission_dict}')
        return mission_dict

    def get_mission_response(self):
        """
        Get mission details formatted for API responses.

        Returns:
            dict: Mission response containing:
                - mission_id: Unique mission identifier
                - file_full_url: URL to download analysis file
                - analysis_id: ID of associated analysis task

        Example:
            >>> response = mission.get_mission_response()
            >>> print(response['file_full_url'])
            'https://storage.cordguard.com/files/abc123.exe'
        """
        response = {
                'mission_id': self.mission_id,
                'file_full_url': self.file.file_full_url,
                'analysis_id': self.analysis.analysis_id
            }
        logger.info(f'Generated mission response: {response}')
        return response