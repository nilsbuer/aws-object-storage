## Issue: Test_AwsObjectStorage_ListObjects_Minimal

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains a three-column ASCII table with Key, Size, Last Modified columns
- STDOUT contains "Total objects in bucket: N" summary line
- object_count output field is populated with a numeric string

### STDOUT:
[empty]

### STDERR:
2026-09-17 09:20:33,534 - 140282792228416 AsyEvent[EXTENSION_START] - extension.py[63] INFO: aws-object-storage v1.0.0 started
2026-09-17 09:20:33,534 - 140282792228416 AsyEvent[EXTENSION_START] - extension.py[70] INFO: Action requested: List Objects
2026-09-17 09:20:33,534 - 140282792228416 AsyEvent[EXTENSION_START] - extension.py[76] INFO: Executing action: List Objects
2026-09-17 09:20:33,534 - 140282792228416 AsyEvent[EXTENSION_START] - list_objects.py[42] INFO: Starting list_objects action
2026-09-17 09:20:33,534 - 140282792228416 AsyEvent[EXTENSION_START] - list_objects.py[67] INFO: Initializing S3 client for region: us-east-1
2026-09-17 09:20:33,534 - 140282792228416 AsyEvent[EXTENSION_START] - s3_manager.py[35] INFO: Initializing S3 client for region: us-east-1
2026-09-17 09:20:33,622 - 140282792228416 AsyEvent[EXTENSION_START] - s3_manager.py[43] INFO: S3 client initialized
2026-09-17 09:20:33,622 - 140282792228416 AsyEvent[EXTENSION_START] - list_objects.py[75] INFO: Retrieving all objects from bucket: aws-object-storage-test-2026
2026-09-17 09:20:33,622 - 140282792228416 AsyEvent[EXTENSION_START] - s3_manager.py[68] INFO: Listing all objects in bucket: aws-object-storage-test-2026
2026-09-17 09:20:33,929 - 140282792228416 AsyEvent[EXTENSION_START] - s3_manager.py[211] ERROR: ClientError [InvalidAccessKeyId]: The AWS Access Key Id you provided does not exist in our records.
2026-09-17 09:20:33,929 - 140282792228416 AsyEvent[EXTENSION_START] - extension.py[90] ERROR: Execution error: Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.
2026-09-17 09:20:33,956 - 140282792228416 AsyEvent[EXTENSION_START] - extension_start_result.py[221] ERROR: Error in extension: /var/opt/universal/uag/extensions/.aws-object-storage/extension.py:187 - Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.

### Extension Output:
{
  "exit_code": 1,
  "status_description": "Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.",
  "metadata": {
    "version": "1.0.0",
    "extension": "aws-object-storage"
  },
  "input_fields": {
    "action": ["List Objects"],
    "aws_credentials": {
      "user": "PLACEHOLDER_USER",
      "password": "****",
      "token": "",
      "passphrase": ""
    },
    "aws_region": "us-east-1",
    "bucket_name": "aws-object-storage-test-2026",
    "local_file": "",
    "s3_object_key": ""
  },
  "result": {},
  "errors": [
    {
      "type": "ResourceError",
      "message": "Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.",
      "exit_code": 1
    }
  ]
}
