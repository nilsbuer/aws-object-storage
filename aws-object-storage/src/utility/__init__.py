"""
Utility package for the AWS Object Storage extension.

Exports:
    S3Manager: Encapsulates all boto3 S3 interactions (listing and uploading).
    OutputFormatter: Produces human-readable STDOUT for the List Objects action.
"""
from utility.s3_manager import S3Manager
from utility.formatter import OutputFormatter

__all__ = ["S3Manager", "OutputFormatter"]
