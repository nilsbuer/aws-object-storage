"""
S3Manager — encapsulates all boto3 S3 interactions for the AWS Object Storage extension.

Initializes the S3 client with explicit credentials (no credential-chain fallback),
exposes methods for listing bucket objects and uploading local files, and translates
all botocore/boto3 exceptions into extension-specific custom exceptions.
"""
import logging

import boto3
import botocore.exceptions

from exceptions import (
    AuthenticationError,
    AuthorizationError,
    ResourceError,
    ServiceConnectionError,
)

logger = logging.getLogger("UNV")


class S3Manager:
    """Encapsulates all boto3 S3 interactions for the AWS Object Storage extension."""

    def __init__(self, access_key_id: str, secret_access_key: str, region: str) -> None:
        """
        Initialize the S3 client with explicit credentials.

        Args:
            access_key_id: AWS Access Key ID from the UAC Credential user field.
            secret_access_key: AWS Secret Access Key from the UAC Credential password field.
            region: AWS region where the target S3 bucket resides.
        """
        logger.info("Initializing S3 client for region: %s", region)
        self._client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )
        self._region = region
        logger.info("S3 client initialized")

    def list_objects(self, bucket_name: str) -> tuple[list[dict], int]:
        """
        Retrieve all objects from the specified S3 bucket across all pages.

        Uses paginated list_objects_v2 to handle buckets with more than 1000 objects.

        Args:
            bucket_name: Name of the S3 bucket to list.

        Returns:
            A tuple of (all_objects, total_count) where all_objects is a list of dicts,
            each containing:
                - key (str): S3 object key.
                - size (int): Object size in bytes.
                - last_modified (str): ISO 8601 UTC timestamp (YYYY-MM-DDTHH:MM:SSZ).
            total_count is the total number of objects returned across all pages.

        Raises:
            AuthenticationError: If AWS rejects the supplied credentials.
            AuthorizationError: If the IAM policy denies s3:ListObjectsV2 on the bucket.
            ResourceError: If the bucket does not exist or an unrecognized error occurs.
            ServiceConnectionError: If a network or connectivity error occurs.
        """
        logger.info("Listing all objects in bucket: %s", bucket_name)
        all_objects: list[dict] = []

        try:
            paginator = self._client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket_name)

            for page_num, page in enumerate(page_iterator, start=1):
                contents = page.get("Contents", [])
                logger.debug("Page %d: %d objects", page_num, len(contents))
                for obj in contents:
                    all_objects.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    })

        except botocore.exceptions.ClientError as exc:
            self._translate_client_error(
                exc, operation="s3:ListObjectsV2", bucket_name=bucket_name
            )
        except (
            botocore.exceptions.EndpointResolutionError,
            botocore.exceptions.ConnectTimeoutError,
            botocore.exceptions.ReadTimeoutError,
        ) as exc:
            logger.error(
                "Network error listing objects in bucket %s: %s", bucket_name, str(exc)
            )
            raise ServiceConnectionError(str(exc))
        except (OSError, ConnectionError) as exc:
            logger.error(
                "Connectivity error listing objects in bucket %s: %s", bucket_name, str(exc)
            )
            raise ServiceConnectionError(str(exc))
        except botocore.exceptions.BotoCoreError as exc:
            logger.error(
                "Unrecognized botocore error listing objects in bucket %s: %s",
                bucket_name,
                str(exc),
            )
            raise ResourceError(str(exc))

        total_count = len(all_objects)
        logger.info("Retrieved %d objects from bucket: %s", total_count, bucket_name)
        return all_objects, total_count

    def upload_file(
        self, local_file_path: str, bucket_name: str, s3_object_key: str
    ) -> str:
        """
        Upload a local file to the specified S3 bucket at the given object key.

        After the upload completes, retrieves the ETag via head_object.

        Args:
            local_file_path: Absolute path to the file on the agent host filesystem.
            bucket_name: Name of the destination S3 bucket.
            s3_object_key: Destination S3 object key (path within the bucket).

        Returns:
            ETag of the uploaded object as returned by AWS, including surrounding quotes.

        Raises:
            AuthenticationError: If AWS rejects the supplied credentials.
            AuthorizationError: If the IAM policy denies s3:PutObject on the bucket.
            ResourceError: If the bucket does not exist or an unrecognized error occurs.
            ServiceConnectionError: If a network or connectivity error occurs.
        """
        logger.info("Uploading file to s3://%s/%s", bucket_name, s3_object_key)
        logger.debug("Local file path: %s", local_file_path)

        try:
            self._client.upload_file(local_file_path, bucket_name, s3_object_key)
            logger.info(
                "Upload complete; retrieving ETag for s3://%s/%s", bucket_name, s3_object_key
            )
            head_response = self._client.head_object(Bucket=bucket_name, Key=s3_object_key)
            etag: str = head_response["ETag"]
            logger.debug("ETag: %s", etag)
            return etag

        except botocore.exceptions.ClientError as exc:
            self._translate_client_error(
                exc, operation="s3:PutObject", bucket_name=bucket_name
            )
        except (
            botocore.exceptions.EndpointResolutionError,
            botocore.exceptions.ConnectTimeoutError,
            botocore.exceptions.ReadTimeoutError,
        ) as exc:
            logger.error(
                "Network error uploading to s3://%s/%s: %s",
                bucket_name,
                s3_object_key,
                str(exc),
            )
            raise ServiceConnectionError(str(exc))
        except (OSError, ConnectionError) as exc:
            logger.error(
                "Connectivity error uploading to s3://%s/%s: %s",
                bucket_name,
                s3_object_key,
                str(exc),
            )
            raise ServiceConnectionError(str(exc))
        except botocore.exceptions.BotoCoreError as exc:
            logger.error(
                "Unrecognized botocore error uploading to s3://%s/%s: %s",
                bucket_name,
                s3_object_key,
                str(exc),
            )
            raise ResourceError(str(exc))

        # _translate_client_error always raises; this line is unreachable.
        raise ResourceError("Upload failed with an unhandled error")  # pragma: no cover

    def _translate_client_error(
        self,
        exc: botocore.exceptions.ClientError,
        operation: str = "",
        bucket_name: str = "",
    ) -> None:
        """
        Translate a botocore ClientError into an extension-specific exception.

        This method always raises; it never returns normally.

        Args:
            exc: The ClientError to translate.
            operation: The AWS operation name (e.g. 's3:ListObjectsV2').
            bucket_name: The S3 bucket name involved in the operation.

        Raises:
            AuthenticationError: For error codes InvalidClientTokenId or SignatureDoesNotMatch.
            AuthorizationError: For error code AccessDenied.
            ResourceError: For error code NoSuchBucket or any other unrecognized code.
        """
        error_info = exc.response.get("Error", {})
        error_code: str = error_info.get("Code", "")
        error_message: str = error_info.get("Message", str(exc))

        logger.error("ClientError [%s]: %s", error_code, error_message)

        if error_code in ("InvalidClientTokenId", "SignatureDoesNotMatch"):
            raise AuthenticationError(error_message)

        if error_code == "AccessDenied":
            raise AuthorizationError(
                f"Operation '{operation}' denied on bucket '{bucket_name}': {error_message}"
            )

        if error_code == "NoSuchBucket":
            raise ResourceError(f"Bucket '{bucket_name}' does not exist: {error_message}")

        raise ResourceError(f"[{error_code}] {error_message}")
