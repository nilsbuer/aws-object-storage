## Test: Test_AwsObjectStorage_ListObjects_Full

**Status**: ⚠ Error

### Output:
```
STDERR:
s3_manager.py[211] ERROR: ClientError [InvalidAccessKeyId]: The AWS Access Key Id you provided does not exist in our records.
extension.py[90] ERROR: Execution error: Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.

Extension Output:
exit_code: 1
status_description: Resource Error: [InvalidAccessKeyId] The AWS Access Key Id you provided does not exist in our records.
```

### Notes:
- Task failed due to invalid AWS credentials (placeholder used: PLACEHOLDER_USER)
- Extension loaded and dispatched correctly to List Objects action
- Environment variable UE_MAX_OUTPUT_RECORDS=100 was set but not reached
- Known failure: credential aws-s3-test-cred contains placeholder values
