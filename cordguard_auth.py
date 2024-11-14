"""
CordGuard Authentication Module

This module provides cryptographic services for CordGuard, including key management,
message signing, and signature verification.

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""
import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes, PrivateKeyTypes
from cryptography.exceptions import InvalidSignature

class AsymmetricKeysTypes:
    """Supported asymmetric key types"""
    ED25519 = "ed25519"

class CordguardAuth:
    """
    Cordguard Authentication Class
    
    This class handles cryptographic operations for Cordguard, including loading keys,
    signing messages, and verifying signatures.
    
    Attributes:
        key_type (AsymmetricKeysTypes): Type of asymmetric key being used
        private_key_path (str): Path to the private key file
        public_key_path (str): Path to the public key file
        public_key (Ed25519PublicKey): Loaded public key instance
        private_key (Ed25519PrivateKey): Loaded private key instance
    """
    
    def __init__(self, key_type: AsymmetricKeysTypes = AsymmetricKeysTypes.ED25519, private_key_path: str = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/server/ed25519_private_key.pem')}", public_key_path: str = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/server/ed25519_public_key.pem')}"):
        """
        Initialize CordguardAuth with key paths and type
        
        Args:
            key_type (AsymmetricKeysTypes): Type of asymmetric key to use
            private_key_path (str): Path to private key file, defaults to keys/server/ed25519_private_key.pem
            public_key_path (str): Path to public key file, defaults to keys/server/ed25519_public_key.pem
        """
        self.key_type: AsymmetricKeysTypes = key_type
        self.private_key_path: str = private_key_path
        self.public_key_path: str = public_key_path
        self.public_key: ed25519.Ed25519PublicKey | None = None
        self.private_key: ed25519.Ed25519PrivateKey | None = None
        self._load_keys()
    
    def _load_keys(self):
        """
        Load public and private keys from files into memory
        
        Reads the key files, deserializes them from PEM format, and creates
        Ed25519 key instances for use in cryptographic operations.
        """
        public_key: PublicKeyTypes | None = None
        private_key: PrivateKeyTypes | None = None
        
        # Load public key from PEM file
        with open(self.public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        # Load private key from PEM file
        with open(self.private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        # Convert loaded keys to Ed25519 instances if using ED25519
        if self.key_type == AsymmetricKeysTypes.ED25519:
            # Convert public key to raw format and create Ed25519PublicKey instance
            self.public_key = ed25519.Ed25519PublicKey.from_public_bytes(
                public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            )

            # Convert private key to raw format and create Ed25519PrivateKey instance
            self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
                private_key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )


    def sign(self, message: bytes) -> bytes:
        """
        Sign a message using the private key
        
        Args:
            message (bytes): The message to sign
            
        Returns:
            bytes: The signature for the message
        """
        return self.private_key.sign(message)


    def verify(self, message: bytes, signature: bytes) -> bool:
        """
        Verify a message signature using the public key
        
        Args:
            message (bytes): The original message
            signature (bytes): The signature to verify
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Attempt to verify the signature - will raise InvalidSignature if invalid
            self.public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False