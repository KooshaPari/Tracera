"""Encryption service for secure credential storage using AES-256-GCM.

Functional Requirements: FR-INFRA-010
"""

import base64
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AES256_KEY_BYTES = 32  # 256 bits


class EncryptionService:
    """AES-256-GCM encryption for credentials.

    Uses a master key from environment variables to encrypt/decrypt
    sensitive tokens and credentials with authenticated encryption.
    """

    # IV size recommended for GCM mode
    IV_SIZE = 12  # 96 bits

    def __init__(self, master_key: str | None = None) -> None:
        """Initialize encryption service.

        Args:
            master_key: Base64-encoded 256-bit master key.
                       If not provided, reads from ENCRYPTION_MASTER_KEY env var.
        """
        key_source = master_key or os.getenv("ENCRYPTION_MASTER_KEY")
        if not key_source:
            msg = (
                "Encryption master key not set. "
                "Set ENCRYPTION_MASTER_KEY environment variable or pass key to constructor."
            )
            raise ValueError(
                msg,
            )

        # Decode the base64 key
        try:
            self._key = base64.b64decode(key_source)
        except Exception as e:
            msg = f"Invalid master key format (must be base64): {e}"
            raise ValueError(msg) from e

        # Validate key size (must be 256 bits = 32 bytes)
        if len(self._key) != AES256_KEY_BYTES:
            msg = f"Master key must be 256 bits ({AES256_KEY_BYTES} bytes), got {len(self._key)} bytes"
            raise ValueError(msg)

        self._cipher = AESGCM(self._key)

    @staticmethod
    def generate_key() -> str:
        """Generate a new 256-bit encryption key.

        Returns:
            Base64-encoded 256-bit key suitable for use as master key.
        """
        key_bytes = secrets.token_bytes(AES256_KEY_BYTES)
        return base64.b64encode(key_bytes).decode("utf-8")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext token.

        Uses AES-256-GCM which provides both confidentiality and
        authenticity. A random IV is generated for each encryption
        and prepended to the ciphertext.

        Args:
            plaintext: The token or credential to encrypt.

        Returns:
            Base64-encoded string containing IV + ciphertext + auth tag.
        """
        if not plaintext:
            msg = "Cannot encrypt empty plaintext"
            raise ValueError(msg)

        # Generate random IV for each encryption
        iv = os.urandom(self.IV_SIZE)

        # Encrypt with authentication
        ciphertext = self._cipher.encrypt(
            nonce=iv,
            data=plaintext.encode("utf-8"),
            associated_data=None,  # No additional authenticated data
        )

        # Combine IV and ciphertext, then base64 encode
        encrypted_data = iv + ciphertext
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted token.

        Extracts the IV from the encrypted data and decrypts
        using AES-256-GCM with authentication verification.

        Args:
            encrypted: Base64-encoded encrypted data (IV + ciphertext + tag).

        Returns:
            Original plaintext token.

        Raises:
            ValueError: If decryption fails (invalid data or tampered).
        """
        if not encrypted:
            msg = "Cannot decrypt empty data"
            raise ValueError(msg)

        try:
            # Decode base64
            encrypted_data = base64.b64decode(encrypted)

            # Extract IV and ciphertext
            iv = encrypted_data[: self.IV_SIZE]
            ciphertext = encrypted_data[self.IV_SIZE :]

            # Decrypt and verify authenticity
            plaintext = self._cipher.decrypt(
                nonce=iv,
                data=ciphertext,
                associated_data=None,
            )

            return plaintext.decode("utf-8")

        except Exception as e:
            msg = f"Decryption failed: {e}"
            raise ValueError(msg) from e

    def rotate_encryption(self, encrypted: str, new_service: "EncryptionService") -> str:
        """Re-encrypt data with a new key.

        Useful for key rotation - decrypts with current key and
        re-encrypts with a new key.

        Args:
            encrypted: Data encrypted with current key.
            new_service: EncryptionService instance with new key.

        Returns:
            Data encrypted with new key.
        """
        plaintext = self.decrypt(encrypted)
        return new_service.encrypt(plaintext)


# Singleton instance for application use
_encryption_service: EncryptionService | None = None


def get_encryption_service() -> EncryptionService:
    """Get or create the singleton encryption service instance.

    Returns:
        Configured EncryptionService instance.
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def reset_encryption_service() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _encryption_service
    _encryption_service = None
