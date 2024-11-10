class CordguardWorkerStatus:
    """
    Enum for worker statuses

    NOT_ACQUIRED: Worker is not acquired by any mission
    ACQUIRED: Worker is acquired by a mission
    """
    NOT_ACQUIRED = 'not_acquired'
    ACQUIRED = 'acquired'

class CordguardWorker:
    """
    Class representing a VM worker JSON schema
    """
    def __init__(self, hwid: str, signed_hwid: str, public_ip: str, is_signed: bool, status: CordguardWorkerStatus):
        self.hwid = hwid
        self.public_ip = public_ip
        self.is_signed = is_signed
        self.signed_hwid = signed_hwid
        self.status = status
    
    # @staticmethod
    # def from_dict(data: dict) -> 'CordguardWorker':
    #     return CordguardWorker(hwid=data['hwid'], signed_hwid=data['signed_hwid'], public_ip=data['public_ip'], is_signed=data['is_signed'], status= CordguardWorkerStatus.ACQUIRED if data['is_acquired'] else CordguardWorkerStatus.NOT_ACQUIRED)
    
    def __str__(self):
        return f'CordguardWorker: {self.hwid} - {self.public_ip} - {self.is_signed} - {self.status}'
    
    def is_acquired(self):
        return self.status == CordguardWorkerStatus.ACQUIRED

    def set_acquired(self, status: bool):
        self.status = CordguardWorkerStatus.ACQUIRED if status else CordguardWorkerStatus.NOT_ACQUIRED

    def get_dict(self):
        """
        Get a dictionary representation of the worker

        Returns:
            dict: A dictionary representation of the worker
            {
                "hwid": str,
                "public_ip": str,
                "is_signed": bool,
                "signed_hwid": str,
                "is_acquired": bool
            }
        """
        return {
            "hwid": self.hwid,
            "public_ip": self.public_ip,
            "is_signed": self.is_signed,
            "signed_hwid": self.signed_hwid,
            "is_acquired": self.is_acquired(),
        }
