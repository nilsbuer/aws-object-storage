## Test: Test_AwsObjectStorage_UploadFile_Full

**Status**: ⚠ Error

### Output:
```
STDERR:
upload_file.py[66] ERROR: Local file not found: /home/ubroker/uac-extension-tests/input/test-upload.csv
extension.py[90] ERROR: Execution error: Validation Error: Local file '/home/ubroker/uac-extension-tests/input/test-upload.csv' does not exist

Extension Output:
exit_code: 20
status_description: Validation Error: Local file '/home/ubroker/uac-extension-tests/input/test-upload.csv' does not exist
```

### Notes:
- Task failed at file validation before attempting AWS operations
- Extension loaded and dispatched correctly to Upload File action
- Test input file /home/ubroker/uac-extension-tests/input/test-upload.csv does not exist on the agent host
- Additional known failure: credential aws-s3-test-cred contains placeholder values
