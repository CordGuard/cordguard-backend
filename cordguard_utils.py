"""
CordGuard Utils Module

This module contains utility functions for the CordGuard system, including:
- Safe file reading with size limits and chunked processing
- Filename sanitization and validation
- Security-focused file handling utilities

The utilities in this module focus on secure file operations by implementing:
- Memory-safe file reading through chunked processing
- File size validation and limits
- Filename sanitization to prevent path traversal
- Secure file handling best practices

Key Functions:
    safe_read_file(): Read files safely with size limits
    safe_filename(): Sanitize filenames for secure storage

Dependencies:
    werkzeug.utils: For secure filename handling
    logging: For operation logging

Usage:
    from cordguard_utils import safe_read_file, safe_filename
    
    # Safely read an uploaded file
    content = safe_read_file(uploaded_file)
    if content is not None:
        # Process the file content
        
    # Sanitize a filename
    safe_name = safe_filename(original_name)

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""

import logging
from werkzeug.utils import secure_filename
from fastapi import Request

logging.basicConfig(level=logging.INFO)

def safe_read_file(file, max_size=25 * 1024 * 1024) -> bytes | None:
    """
    Safely read a file in chunks to prevent memory issues.
    
    This function reads a file in chunks and enforces a maximum file size limit.
    It's designed to handle potentially large file uploads securely by:
    - Reading the file in smaller chunks (20% of max_size)
    - Enforcing a total size limit
    - Returning None if file exceeds size limit
    
    Args:
        file: A file-like object supporting read() method
        max_size (int): Maximum allowed file size in bytes, defaults to 25MB
        
    Returns:
        bytearray: The complete file contents if within size limit
        None: If file exceeds max_size limit
        
    Example:
        >>> content = safe_read_file(uploaded_file)
        >>> if content is None:
        >>>     print("File too large")
    """
    content = bytearray()
    chunk_size = int(max_size * 0.2)  # 20% of the max size
    logging.info('Starting to read file in chunks.')
    size = 0
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            if size == 0:
                logging.error('File is empty')
                return None
            logging.info('Finished reading file.')
            break
        content.extend(chunk)
        logging.debug(f'Read chunk of size: {len(chunk)} bytes.')
        size += len(chunk)
        if size > max_size:
            logging.error('File too large uploaded')
            return None
    logging.info('File read successfully, total size: %d bytes.', size)
    return bytes(content)


def safe_filename(filename):
    """
    Safely sanitize a filename to prevent path traversal and other filename-based attacks.
    
    This function uses werkzeug's secure_filename to:
    - Remove path components and special characters
    - Convert spaces to underscores
    - Remove non-ASCII characters
    - Ensure the filename is safe for filesystem operations
    
    Args:
        filename (str): The original filename to sanitize
        
    Returns:
        str: A sanitized version of the filename that is safe to use
        
    Example:
        >>> safe_filename("../etc/passwd")
        'etc_passwd'
        >>> safe_filename("my file.txt")
        'my_file.txt'
    """
    sanitized_name = secure_filename(filename)
    logging.info('Sanitized filename: %s', sanitized_name)
    return sanitized_name


def extract_file_extension(filename):
    """
    Extract the full file extension from a filename.
    
    This function handles multiple extensions (e.g., 'file.tar.gz' or 'script.exe.py')
    by returning everything after the first dot.
    
    Args:
        filename (str): The filename to process
        
    Returns:
        str: The full file extension including all parts after the first dot
        
    Example:
        >>> extract_file_extension("main.exe.py")
        'exe.py'
        >>> extract_file_extension("archive.tar.gz")
        'tar.gz'
    """
    parts = filename.split('.', 1)
    if len(parts) > 1:
        logging.info('Extracted file extension: %s', parts[1])
        return '.' + parts[1]
    logging.error('No file extension found for filename: %s', filename)
    raise ValueError('No file extension found')

def does_file_have_extension(filename):
    has_extension = '.' in filename
    logging.debug('File %s has extension: %s', filename, has_extension)
    return has_extension

def is_sub_host(request: Request, sub_host: str = '') -> bool:
    host = request.headers.get('host', '')
    if not host:
        logging.warning('No host found in request headers.')
        return False
    if sub_host == '':
        logging.warning('No sub_host provided for comparison.')
        return False
    
    result = host.startswith(sub_host)
    logging.debug('Host %s starts with sub_host %s: %s', host, sub_host, result)
    return result
