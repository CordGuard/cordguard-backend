"""
CordGuard File Module

This module provides file handling and storage capabilities for the CordGuard system,
including file metadata management, unique ID generation, and S3 storage operations.

Key Components:
-------------
- CordGuardAnalysisFile: Main class for managing file analysis operations
- S3 Integration: Methods for uploading and retrieving files from S3 storage
- File Metadata: Tracking of file attributes like size, type, and content hashes

File Processing Flow:
------------------
1. File is received and CordGuardAnalysisFile instance is created
2. Unique IDs are generated for both the analysis job and file
3. File metadata is extracted and stored
4. File content is uploaded to S3 if configured
5. Analysis can then be performed using the stored file

ID Generation:
------------
- Analysis IDs: Generated using timestamp and random components
- File IDs: Generated as random hex strings
- File Hashes: SHA256 hashes of file content

Dependencies:
-----------
- hashlib: For file content hashing
- secrets: For secure ID generation
- boto3: For S3 operations
- cordguard_codes: For trackable ID generation

Usage:
-----
    # Create new file instance
    file = CordGuardAnalysisFile(
        file_name="test.exe",
        file_type="application/x-msdownload",
        file_content=binary_content
    )
    
    # Access file metadata
    analysis_id = file.analysis_id
    file_hash = file.file_hash

Author: security@cordguard.org
Version: 1.0.0
"""
import hashlib
import logging
import secrets
from datetime import datetime
import time
from cordguard_codes import create_trackable_id
from cordguard_utils import extract_file_extension
import boto3
import os
#from cordguard_globals import AWS_CONFIG

class CordGuardAnalysisFile:
    """
    A class to handle file analysis operations including S3 storage.

    This class manages file metadata and handles uploading files to S3 for analysis.
    It generates unique IDs for both the analysis and file, and provides methods
    for S3 interactions.

    Attributes:
        analysis_id (str): Unique ID for the analysis, combining timestamp and random number
        file_id (str): Unique hex ID for the file
        file_type (str): MIME type of the file
        file_size (int): Size of the file in bytes
        file_content (bytes): Raw content of the file
        s3_client: Boto3 S3 client for S3 operations
        bucket_name_s3 (str): Name of the S3 bucket for storage
    """

    def __init__(self, file_name: str = "", file_type: str = "", file_size: int = 0, file_content: bytes = b"", s3_client = None, bucket_name_s3: str = ""):
        """
        Initialize a new CordGuardAnalysisFile instance.

        Args:
            file_name (str): Name of the file
            file_type (str): MIME type of the file
            file_size (int): Size of the file in bytes
            file_content (bytes): Raw content of the file
            s3_client: Boto3 S3 client instance
            bucket_name_s3 (str): Name of the S3 bucket
        """
        self.current_timestamp = int(time.time())
        self.analysis_id = create_trackable_id(self.current_timestamp)
        self.file_id = secrets.token_hex(16)
        self.file_name: str = file_name
        self.file_extension: str = extract_file_extension(file_name)
        self.file_type: str = file_type
        self.file_size: int = file_size
        self.file_content: bytes = file_content
        if s3_client is None:
             # AWS Configuration
            AWS_CONFIG = { # TODO: Move to globals when you find a stable way to handle it
                'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'endpoint_url': os.getenv('AWS_ENDPOINT_URL_S3'),
                'region': os.getenv('AWS_REGION')
            }

            self.s3_client =  boto3.client(
            's3',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key'],
            endpoint_url=AWS_CONFIG['endpoint_url'],
            region_name=AWS_CONFIG['region']
            )
        else:
            self.s3_client = s3_client
        self.bucket_name_s3 = bucket_name_s3
        self.file_hash: str = hashlib.sha256(file_content).hexdigest()

    # @staticmethod
    # def from_dict(data: dict) -> 'CordGuardAnalysisFile':
    #     return CordGuardAnalysisFile(file_name=data['file_name'], file_type=data['file_type'], file_size=data['file_size'], file_content=data['file_content'], s3_client=data['s3_client'], bucket_name_s3=data['bucket_name_s3'])

    def __str__(self):
        """Return a string representation of the file object."""
        return f'File(analysis_id={self.analysis_id}, file_id={self.file_id}, file_name={self.file_name}, file_type={self.file_type}, file_size={self.file_size})'
    
    def __repr__(self):
        """Return a detailed string representation of the file object."""
        return self.__str__()
    
    def get_dict(self):
        """
        Convert the file object to a dictionary.

        Returns:
            dict: Dictionary containing file metadata
        """
        return {
            'analysis_id': self.analysis_id,
            'file_id': self.file_id,
            'file_name': self.file_name,
            'file_extension': self.file_extension,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            "file_full_url": self.get_full_url_to_file()
        }
    
    def upload_to_s3(self) -> bool:
        """
        Upload the file content to S3.

        Attempts to upload the file content to S3 using the generated key path.
        Logs the upload process and any errors that occur.

        Returns:
            bool: True if upload successful, False otherwise
        """
        if self.file_content is None or self.file_size == 0 or self.file_type is None or self.s3_client is None or self.bucket_name_s3 is None:
            logging.error(f'{self.file_id} File content is None')
            return False
        logging.info(f'Uploading {self.file_id} to S3 at key: {self.get_s3_key()} in bucket: {self.bucket_name_s3}')
        try:
            self.s3_client.put_object(Bucket=self.bucket_name_s3, Key=self.get_s3_key(), Body=self.file_content)
            logging.info(f'{self.file_id} uploaded to S3')
        except Exception as e:
            logging.error(f'Error uploading {self.file_id} to S3: {e}')
            return False
        return True
    
    def get_content(self):
        """
        Get the file content.
        """
        return self.file_content
    
    def get_analysis_id(self):
        """
        Get the analysis ID.
        """
        return self.analysis_id
    
    def get_file_id(self):
        """
        Get the file ID.
        """
        return self.file_id

    def get_s3_key(self):
        """
        Generate the S3 key path for the file.

        Returns:
            str: S3 key path in format 'analysis/{analysis_id}/{file_id}'
        """
        # For organization, we use date month and year to create the folder structure
        # YYYY-mm, then inside we put the day number and day name for more order
        date_time = datetime.fromtimestamp(self.current_timestamp)
        year_month = date_time.strftime('%Y-%m')
        day_number = date_time.strftime('%d')
        day_name = date_time.strftime('%A')
        return f'analysis/{year_month}/{day_number}_{day_name}/{self.analysis_id}-{self.file_id}/{self.file_name}'
    
    def get_full_url_to_file(self):
        """
        Get the full URL to the file in S3.
        """
        return f'{self.s3_client.meta.endpoint_url}/{self.bucket_name_s3}/{self.get_s3_key()}'