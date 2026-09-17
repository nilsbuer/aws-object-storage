"""
Exceptions module template for UAC Universal Extensions.

This module provides:
- Base ExecutionError class
- Standard exception types (DataValidationError, ConnectionError, etc.)
- ErrorManager singleton for error collection
- Exit code conventions

CUSTOMIZE:
- Add custom exception types for your extension
- Modify ErrorManager methods if needed
"""
from typing import Optional

class ExecutionError(Exception):
    """
    The default error raised by an extension.

    All extension errors must inherit from it.

    Attrs:
        exit_code: The exit code of the extension (for UAC)
        message: The error message for status description
    """

    exit_code: int = 1
    message: str = "Execution Failed"

    def __init__(self, message: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Optional message that will be appended to the default message.

        Note:
            To return result data with errors, use error_manager.set_result()
            before raising the exception.
        """
        if message:
            self.message = f"{self.message}: {message}"

        super().__init__(self.message)

class DataValidationError(ExecutionError):
    """Raised when an input field is invalid."""
    exit_code = 20
    message = "Data Validation Error"

class UnexpectedSystemError(ExecutionError):
    """Raised for unexpected system errors."""
    exit_code = 1
    message = "System Error"

class ValidationError(ExecutionError):
    """
    Raised when a pre-flight input validation check fails before any external
    API call is made.

    Use this for agent-side checks such as verifying that a required local file
    exists on the filesystem before attempting an upload.

    Exit code 20 signals a user-correctable input error.
    """
    exit_code = 20
    message = "Validation Error"

class AuthenticationError(ExecutionError):
    """
    Raised when AWS rejects the supplied credentials.

    Triggered by botocore ClientError codes ``InvalidClientTokenId`` and
    ``SignatureDoesNotMatch``.  The user must correct the AWS Access Key ID or
    Secret Access Key stored in the UAC Credential entity.

    Exit code 1 indicates a non-transient configuration error.
    """
    exit_code = 1
    message = "Authentication Error"

class AuthorizationError(ExecutionError):
    """
    Raised when the AWS IAM policy denies the requested operation.

    Triggered by botocore ClientError code ``AccessDenied``.  Include the
    operation name and bucket name in the message so the user knows which IAM
    permission is missing.

    Exit code 1 indicates a non-transient configuration error.
    """
    exit_code = 1
    message = "Authorization Error"

class ResourceError(ExecutionError):
    """
    Raised when the requested AWS resource does not exist or an unrecognized
    boto3/botocore error occurs.

    Triggered by botocore ClientError code ``NoSuchBucket`` (wrong bucket name
    or region mismatch) and by any other ClientError or BotoCoreError that does
    not map to a more specific exception.  Include the original error detail in
    the message to aid debugging.

    Exit code 1 indicates a user configuration error or unexpected AWS error.
    """
    exit_code = 1
    message = "Resource Error"

class ServiceConnectionError(ExecutionError):
    """
    Raised when network connectivity to the AWS S3 endpoint fails.

    Triggered by ``botocore.exceptions.EndpointResolutionError``,
    ``botocore.exceptions.ConnectTimeoutError``,
    ``botocore.exceptions.ReadTimeoutError``, ``OSError``, or
    ``ConnectionError`` raised during an API call.  Include the target endpoint
    and retry count in the message where available.

    This error may be transient; the user should check network connectivity and
    DNS resolution.  Exit code 1 is used for all connectivity failures.
    """
    exit_code = 1
    message = "Service Connection Error"
