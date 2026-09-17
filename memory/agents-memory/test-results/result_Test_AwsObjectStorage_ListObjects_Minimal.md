## Test: Test_AwsObjectStorage_ListObjects_Minimal

**Status**: ⚠ Error

### Output:
```
STDERR:
2026-09-17 09:20:33,929 - s3_manager.py[211] ERROR: ClientError [InvalidAccessKeyId]: The AWS Access Key Id you provided does not exist in our records.
2026-09-17 09:20:33,929 - extension.py[90] ERROR: Execution error: Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.

Extension Output:
exit_code: 1
status_description: Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.
```

### Notes:
- Task failed due to invalid AWS credentials (placeholder used: PLACEHOLDER_USER)
- Extension loaded and dispatched correctly to List Objects action
- S3 client initialized but rejected at API call due to invalid access key
- Known failure: credential aws-s3-test-cred contains placeholder values
