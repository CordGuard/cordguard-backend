"""
CordGuard Analysis Module

This module contains the logic for static analysis of files.

Author: security@cordguard.org
Version: 1.0.0
! DEPRECATED
"""

# from cordguard_file import CordGuardAnalysisFile
# import logging, subprocess,os
# from cordguard_temp import CordGuardTemp
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# # TODO: both is_upx_compressed and is_pyinstaller_packaged is lazy ways do a better check later
# def is_upx_compressed(data: bytes):
#     return data.startswith(b"UPX!") or b"UPX" in data
    
# def is_pyinstaller_packaged(data: bytes):
#     return b"MEIPASS" in data or b"pyi" in data



# class StaticAnalysisResult:
#     pass

# class DynamicAnalysisResult:
#     pass

# class AnalysisResult:
#     pass

# !Deprecated
# async def static_analysis(file: CordGuardAnalysisFile) -> StaticAnalysisResult | None:
#     # TODO: Implement AI logic from OpenAI or host one on fly.io.
#     # TODO: Implement static analysis logic, check cordguard_tools.
#     logger.info(f'Static analysis for file: {file.analysis_id}')

#     # Check if the fire is in .jar or pyinstaller format do the analysis with TaxMachine's grabbers_deobfuscator.
#     file_content = file.get_content()
#     if is_upx_compressed(file_content) or is_pyinstaller_packaged(file_content) or file.file_extension == '.jar':
#         # Dump file into a temporary directory
#         temp = CordGuardTemp(os.path.join(os.path.dirname(__file__), 'temp'), default_ttl=100)
#         temp_file = temp.create(file.file_name, file_content)
#         process = subprocess.Popen(['python3', os.path.join(os.path.dirname(__file__), 'cordguard_tools/grabbers_deobfuscator/deobf.py'), temp_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         # Wait for the process to finish
#         try:
#             process.wait(timeout=5000) # if it takes longer than 5 seconds, it's probably not a grabber or something else went wrong
#         except subprocess.TimeoutExpired:
#             logger.error(f'Static analysis for file: {file.analysis_id} timed out')
#             return None

#         # Get the output and error
#         stdout, stderr = process.communicate()
#         logger.info(f'Static analysis for file: {file.analysis_id} completed with output: {stdout} and error: {stderr}')