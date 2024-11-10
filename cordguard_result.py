class CordguardResult:
    def init(self, analysis_id: str, mission_id: str):
        self.analysis_id = analysis_id
        self.mission_id = mission_id
    
    @staticmethod
    def from_dict(data: dict):
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
        return result

    def set_type_of_stealer(self, type: str):
        self.type = type

    def set_webhook(self, webhook: str):
        self.webhook = webhook
    
    def set_is_valid_webhook(self, is_valid: bool):
        self.is_valid_webhook = is_valid
    
    def set_is_it_pyinstaller(self, is_pyinstaller: bool):
        self.is_pyinstaller = is_pyinstaller

    def set_pyinstaller_version(self, version: str):
        self.pyinstaller_version = version
    
    def set_is_upx_packed(self, is_upx_packed: bool):
        self.is_upx_packed = is_upx_packed

    def set_python_version(self, version: str):
        self.python_version = version
    
    def set_is_valid_webhook(self, is_valid: bool):
        self.is_valid_webhook = is_valid

    def get_dict(self):
        return {
            "mission_id": self.mission_id,
            "analysis_id": self.analysis_id,
            "type": self.type,
            "webhook": self.webhook,
            "is_valid_webhook": self.is_valid_webhook,
            "is_pyinstaller": self.is_pyinstaller,
            "pyinstaller_version": self.pyinstaller_version,
            "is_upx_packed": self.is_upx_packed,
            "python_version": self.python_version,
        }