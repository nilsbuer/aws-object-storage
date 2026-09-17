"""List Objects action — lists all objects in the specified S3 bucket."""

import logging
import os

from actions.output import ActionOutput
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import S3Manager

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()

_DEFAULT_MAX_RECORDS: int = 100


def list_objects(input_data: InputFields) -> ActionOutput:
    """
    List all objects in the specified S3 bucket and return them as ActionOutput.

    Reads UE_MAX_OUTPUT_RECORDS from the environment to cap the number of
    objects included in STDOUT and Extension Output. The object_count output
    field is always set to the full total, regardless of the cap.

    Args:
        input_data: Validated input fields containing AWS credentials, region,
                    and bucket name.

    Returns:
        ActionOutput with:
            - object_count: total objects in the bucket.
            - objects: list of object dicts (key, size, last_modified), capped to max_records.
            - truncated: True when total_count exceeds max_records.

    Raises:
        AuthenticationError: If AWS rejects the supplied credentials.
        AuthorizationError: If the IAM policy denies s3:ListObjectsV2 on the bucket.
        ResourceError: If the bucket does not exist or an unrecognized error occurs.
        ServiceConnectionError: If a network or connectivity error occurs.
    """
    logger.info("Starting list_objects action")
    logger.debug(
        "Input: aws_region=%s, bucket_name=%s",
        input_data.aws_region.value if input_data.aws_region else None,
        input_data.bucket_name.value if input_data.bucket_name else None,
    )

    # Initialize output fields for real-time UI updates
    output_fields = OutputFields()

    # Read and parse UE_MAX_OUTPUT_RECORDS
    max_records_raw: str = os.environ.get("UE_MAX_OUTPUT_RECORDS", "")
    try:
        max_records: int = int(max_records_raw)
    except (ValueError, TypeError):
        max_records = _DEFAULT_MAX_RECORDS
    logger.debug("Max output records: %d", max_records)

    # Extract credentials and connection parameters
    access_key_id: str = input_data.aws_credentials.user
    secret_access_key: str = input_data.aws_credentials.password
    aws_region: str = input_data.aws_region.value
    bucket_name: str = input_data.bucket_name.value

    # Initialize S3 client with explicit credentials
    logger.info("Initializing S3 client for region: %s", aws_region)
    s3 = S3Manager(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=aws_region,
    )

    # Retrieve all objects from the bucket (paginated)
    logger.info("Retrieving all objects from bucket: %s", bucket_name)
    all_objects, total_count = s3.list_objects(bucket_name=bucket_name)
    logger.info("Retrieved %d total objects from bucket: %s", total_count, bucket_name)

    # Apply truncation cap
    display_objects = all_objects[:max_records]
    truncated: bool = total_count > max_records
    logger.debug(
        "Truncation check: total=%d, max=%d, truncated=%s",
        total_count,
        max_records,
        truncated,
    )

    # Update UI output field with the total object count
    output_fields.update(object_count=str(total_count))
    logger.debug("Updated object_count output field to: %d", total_count)

    logger.info("list_objects action completed successfully")

    return ActionOutput(
        object_count=total_count,
        objects=display_objects,
        truncated=truncated,
    )
