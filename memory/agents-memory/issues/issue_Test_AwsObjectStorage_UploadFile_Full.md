## Issue: Test_AwsObjectStorage_UploadFile_Full

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains "Successfully uploaded ... → s3://aws-object-storage-test-2026/test/full/2026/Q3/test-upload.csv"
- uploaded_s3_uri output field is set to "s3://aws-object-storage-test-2026/test/full/2026/Q3/test-upload.csv"
- Extension Output JSON contains s3_uri and etag fields

### STDOUT:
[empty]

### STDERR:
2026-09-17 09:22:22,419 - extension.py[63] INFO: aws-object-storage v1.0.0 started
2026-09-17 09:22:22,419 - extension.py[70] INFO: Action requested: Upload File
2026-09-17 09:22:22,419 - extension.py[76] INFO: Executing action: Upload File
...
upload_file.py[66] ERROR: Local file not found: /home/ubroker/uac-extension-tests/input/test-upload.csv
extension.py[90] ERROR: Execution error: Validation Error: Local file '/home/ubroker/uac-extension-tests/input/test-upload.csv' does not exist

### Extension Output:
{
  "exit_code": 20,
  "status_description": "Validation Error: Local file '/home/ubroker/uac-extension-tests/input/test-upload.csv' does not exist",
  "metadata": {"version": "1.0.0", "extension": "aws-object-storage"},
  "input_fields": {
    "action": ["Upload File"],
    "aws_credentials": {"user": "PLACEHOLDER_USER", "password": "****"},
    "aws_region": "us-east-1",
    "bucket_name": "aws-object-storage-test-2026",
    "local_file": "/home/ubroker/uac-extension-tests/input/test-upload.csv",
    "s3_object_key": "test/full/2026/Q3/test-upload.csv"
  },
  "result": {},
  "errors": [{"type": "ValidationError", "message": "Validation Error: Local file '/home/ubroker/uac-extension-tests/input/test-upload.csv' does not exist", "exit_code": 20}]
}
