"""Upload File action — uploads a local file from the agent host to the specified S3 bucket."""

import logging
import os

from actions.output import ActionOutput
from exceptions import ValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import S3Manager

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()


def upload_file(input_data: InputFields) -> ActionOutput:
    """
    Validate that a local file exists on the agent host, then upload it to S3.

    Performs a pre-flight filesystem check before making any AWS API calls. If the
    local file is missing the action raises ValidationError (exit code 20) immediately.
    On success, the uploaded_s3_uri output field is populated and ActionOutput is
    returned with the S3 URI and ETag.

    Args:
        input_data: Validated input fields containing AWS credentials, region,
                    bucket name, local file path, and S3 object key.

    Returns:
        ActionOutput with:
            - s3_uri: Full S3 URI of the uploaded object.
            - etag: ETag of the uploaded object as returned by AWS.
            - local_file: Absolute path of the uploaded local file (used for STDOUT).

    Raises:
        ValidationError: If the local file does not exist on the agent host (exit code 20).
        AuthenticationError: If AWS rejects the supplied credentials.
        AuthorizationError: If the IAM policy denies s3:PutObject on the bucket.
        ResourceError: If the bucket does not exist or an unrecognized error occurs.
        ServiceConnectionError: If a network or connectivity error occurs.
    """
    logger.info("Starting upload_file action")
    logger.debug(
        "Input: aws_region=%s, bucket_name=%s, local_file=%s, s3_object_key=%s",
        input_data.aws_region.value if input_data.aws_region else None,
        input_data.bucket_name.value if input_data.bucket_name else None,
        input_data.local_file.value if input_data.local_file else None,
        input_data.s3_object_key.value if input_data.s3_object_key else None,
    )

    # Initialize output fields for real-time UI updates
    output_fields = OutputFields()

    # Extract credentials and operation parameters
    access_key_id: str = input_data.aws_credentials.user
    secret_access_key: str = input_data.aws_credentials.password
    aws_region: str = input_data.aws_region.value
    bucket_name: str = input_data.bucket_name.value
    local_file: str = input_data.local_file.value
    s3_object_key: str = input_data.s3_object_key.value

    # Pre-flight: verify local file exists before making any AWS API calls
    logger.info("Validating local file exists: %s", local_file)
    if not os.path.exists(local_file):
        logger.error("Local file not found: %s", local_file)
        raise ValidationError(f"Local file '{local_file}' does not exist")
    logger.info("Local file validation passed: %s", local_file)

    # Initialize S3 client with explicit credentials
    logger.info("Initializing S3 client for region: %s", aws_region)
    s3 = S3Manager(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=aws_region,
    )

    # Upload file to S3 and retrieve ETag
    logger.info("Uploading %s to s3://%s/%s", local_file, bucket_name, s3_object_key)
    etag: str = s3.upload_file(
        local_file_path=local_file,
        bucket_name=bucket_name,
        s3_object_key=s3_object_key,
    )
    logger.info("Upload successful: s3://%s/%s", bucket_name, s3_object_key)
    logger.debug("ETag: %s", etag)

    # Compute S3 URI
    s3_uri: str = f"s3://{bucket_name}/{s3_object_key}"

    # Update UI output field with the S3 URI
    output_fields.update(uploaded_s3_uri=s3_uri)
    logger.debug("Updated uploaded_s3_uri output field: %s", s3_uri)

    logger.info("upload_file action completed successfully")

    return ActionOutput(
        s3_uri=s3_uri,
        etag=etag,
        local_file=local_file,
    )
