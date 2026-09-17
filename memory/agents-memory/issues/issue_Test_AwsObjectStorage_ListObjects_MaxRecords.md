## Issue: Test_AwsObjectStorage_ListObjects_MaxRecords

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains a table with at most 2 rows
- If total object count exceeds 2, STDOUT contains truncation notice "Note: Output truncated to 2 records..."
- object_count output field reflects the true total count (not capped)

### STDOUT:
[empty]

### STDERR:
2026-09-17 09:21:46,740 - extension.py[63] INFO: aws-object-storage v1.0.0 started
2026-09-17 09:21:46,741 - extension.py[70] INFO: Action requested: List Objects
2026-09-17 09:21:46,741 - extension.py[76] INFO: Executing action: List Objects
2026-09-17 09:21:46,741 - list_objects.py[42] INFO: Starting list_objects action
...
s3_manager.py[211] ERROR: ClientError [InvalidAccessKeyId]: The AWS Access Key Id you provided does not exist in our records.
extension.py[90] ERROR: Execution error: Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.

### Extension Output:
{
  "exit_code": 1,
  "status_description": "Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.",
  "metadata": {"version": "1.0.0", "extension": "aws-object-storage"},
  "input_fields": {
    "action": ["List Objects"],
    "aws_credentials": {"user": "PLACEHOLDER_USER", "password": "****"},
    "aws_region": "us-east-1",
    "bucket_name": "aws-object-storage-test-2026"
  },
  "result": {},
  "errors": [{"type": "ResourceError", "message": "Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.", "exit_code": 1}]
}
