"""
CordGuard Result Module

This module provides the CordguardResult class for storing and managing analysis results
from CordGuard's malware analysis system. It handles details about Python malware characteristics
including PyInstaller usage, UPX packing, webhook validation, and more.

Key Components:
-------------
- Result Storage: Stores analysis and mission IDs
- Malware Details: Tracks malware type, webhook info, and build characteristics
- Serialization: Methods for dict conversion and reconstruction
- Property Management: Setters for all result attributes

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""
from pydantic import BaseModel

# For FastAPI
class CordguardResult(BaseModel):
    """
    Class for storing and managing malware analysis results.
    
    Stores details about analyzed malware including PyInstaller usage,
    UPX packing, webhook information, and Python version details.
    
    Attributes:
        analysis_id (str): Unique ID for the analysis run
        mission_id (str): Associated mission ID
        type (str): Type of malware stealer detected
        webhook (str): Extracted webhook URL
        is_valid_webhook (bool): Whether webhook is valid
        is_pyinstaller (bool): Whether built with PyInstaller
        pyinstaller_version (str): PyInstaller version if detected
        is_upx_packed (bool): Whether UPX packed
        python_version (str): Python version used
        status (str): Status of the result
    """

    analysis_id: str = ""
    mission_id: str = ""
    signed_hwid: str = ""
    status: str = ""
    type: str = "unknown"
    webhook: str = ""
    is_valid_webhook: bool = False
    is_pyinstaller: bool = False
    pyinstaller_version: str = ""
    is_upx_packed: bool = False
    python_version: str = ""

    def init(self, analysis_id: str, mission_id: str, signed_hwid: str):
        """
        Initialize a new CordguardResult instance.

        Args:
            analysis_id (str): Unique ID for the analysis run
            mission_id (str): Associated mission ID
            signed_hwid (str): Signed HWID
        """
        self.analysis_id = analysis_id
        self.mission_id = mission_id
        self.signed_hwid = signed_hwid
    
    @staticmethod
    def from_dict(data: dict):
        """
        Create a CordguardResult instance from a dictionary.

        Args:
            data (dict): Dictionary containing result data

        Returns:
            CordguardResult: New instance populated with dict data
        """
        result = CordguardResult()
        result.analysis_id = data['analysis_id']
        result.mission_id = data['mission_id']
        result.type = data['type']
        result.webhook = data['webhook']
        result.is_valid_webhook = data['is_valid_webhook']
        result.is_pyinstaller = data['is_pyinstaller']
        result.pyinstaller_version = data['pyinstaller_version']
        result.is_upx_packed = data['is_upx_packed']
        result.python_version = data['python_version']
        result.signed_hwid = data['signed_hwid']
        result.status = data['status']
        return result

    def set_type_of_stealer(self, type: str):
        """
        Set the type of malware stealer detected.

        Args:
            type (str): Type of stealer malware
        """
        self.type = type

    def set_webhook(self, webhook: str):
        """
        Set the detected webhook URL.

        Args:
            webhook (str): Webhook URL found in malware
        """
        self.webhook = webhook
    
    def set_is_valid_webhook(self, is_valid: bool):
        """
        Set whether the detected webhook is valid.

        Args:
            is_valid (bool): Webhook validity status
        """
        self.is_valid_webhook = is_valid
    
    def set_is_it_pyinstaller(self, is_pyinstaller: bool):
        """
        Set whether the malware was built with PyInstaller.

        Args:
            is_pyinstaller (bool): PyInstaller usage status
        """
        self.is_pyinstaller = is_pyinstaller

    def set_pyinstaller_version(self, version: str):
        """
        Set the detected PyInstaller version.

        Args:
            version (str): PyInstaller version string
        """
        self.pyinstaller_version = version
    
    def set_is_upx_packed(self, is_upx_packed: bool):
        """
        Set whether the malware is UPX packed.

        Args:
            is_upx_packed (bool): UPX packing status
        """
        self.is_upx_packed = is_upx_packed

    def set_python_version(self, version: str):
        """
        Set the Python version used to build the malware.

        Args:
            version (str): Python version string
        """
        self.python_version = version
    
    def set_is_valid_webhook(self, is_valid: bool):
        """
        Set whether the webhook is valid.

        Args:
            is_valid (bool): Webhook validity status
        """
        self.is_valid_webhook = is_valid

    def set_status(self, status: str):
        """
        Set the status of the result.

        Args:
            status (str): Status of the result
        """
        self.status = status

    def get_dict(self):
        """
        Convert the result object to a dictionary.

        Returns:
            dict: Dictionary containing all result attributes
        """
        return {
            "status": self.status,
            "mission_id": self.mission_id,
            "analysis_id": self.analysis_id,
            "type": self.type,
            "webhook": self.webhook,
            "is_valid_webhook": self.is_valid_webhook,
            "is_pyinstaller": self.is_pyinstaller,
            "pyinstaller_version": self.pyinstaller_version,
            "is_upx_packed": self.is_upx_packed,
            "python_version": self.python_version,
            "signed_hwid": self.signed_hwid
        }