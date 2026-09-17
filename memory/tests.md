# Test Plan

**Extension:** aws-object-storage
**Generated:** 2026-09-17

---

## Test: Test_AwsObjectStorage_ListObjects_Minimal

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains a three-column ASCII table with Key, Size, Last Modified columns
- STDOUT contains "Total objects in bucket: N" summary line
- object_count output field is populated with a numeric string

---

## Test: Test_AwsObjectStorage_ListObjects_Full

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Environment Variables:**
- UE_MAX_OUTPUT_RECORDS: 100
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains a three-column ASCII table with Key, Size, Last Modified columns
- STDOUT contains "Total objects in bucket: N" summary line
- object_count output field is populated with a numeric string
- At most 100 records are displayed in the table

---

## Test: Test_AwsObjectStorage_ListObjects_MaxRecords

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Environment Variables:**
- UE_MAX_OUTPUT_RECORDS: 2
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains a table with at most 2 rows
- If total object count exceeds 2, STDOUT contains truncation notice "Note: Output truncated to 2 records..."
- object_count output field reflects the true total count (not capped)

---

## Test: Test_AwsObjectStorage_ListObjects_SmallCap

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Environment Variables:**
- UE_MAX_OUTPUT_RECORDS: 1
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains a table with at most 1 row
- If bucket has more than 1 object, truncation notice is printed
- object_count output field reflects the true total count

---

## Test: Test_AwsObjectStorage_ListObjects_LargeCap

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Environment Variables:**
- UE_MAX_OUTPUT_RECORDS: 1000
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
**Expected Results:**
- Task completes with exit code 0
- All objects in the bucket are displayed (up to 1000)
- No truncation notice if bucket contains fewer than 1000 objects
- object_count output field is populated correctly

---

## Test: Test_AwsObjectStorage_UploadFile_Minimal

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
- local_file: /home/ubroker/uac-extension-tests/input/test-upload.csv
- s3_object_key: test/minimal/test-upload.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains "Successfully uploaded /home/ubroker/uac-extension-tests/input/test-upload.csv → s3://aws-object-storage-test-2026/test/minimal/test-upload.csv"
- uploaded_s3_uri output field is set to "s3://aws-object-storage-test-2026/test/minimal/test-upload.csv"
- Extension Output JSON contains s3_uri and etag fields

---

## Test: Test_AwsObjectStorage_UploadFile_Full

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
- local_file: /home/ubroker/uac-extension-tests/input/test-upload.csv
- s3_object_key: test/full/2026/Q3/test-upload.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains "Successfully uploaded ... → s3://aws-object-storage-test-2026/test/full/2026/Q3/test-upload.csv"
- uploaded_s3_uri output field is set to "s3://aws-object-storage-test-2026/test/full/2026/Q3/test-upload.csv"
- Extension Output JSON contains s3_uri and etag fields

---

## Test: Test_AwsObjectStorage_UploadFile_NestedKey

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
- local_file: /home/ubroker/uac-extension-tests/input/test-upload.csv
- s3_object_key: data/reports/2026/Q3/uploads/test-upload.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains successful upload confirmation with the nested S3 key path
- uploaded_s3_uri output field is set to "s3://aws-object-storage-test-2026/data/reports/2026/Q3/uploads/test-upload.csv"
- Extension Output JSON contains s3_uri and etag fields

---

## Test: Test_AwsObjectStorage_UploadFile_RootKey

**Template:** Aws Object Storage
**Agent:** AGT_LX_USERVERSE
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-cred
- aws_region: us-east-1
- bucket_name: aws-object-storage-test-2026
- local_file: /home/ubroker/uac-extension-tests/input/test-upload.csv
- s3_object_key: root-level-upload.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains successful upload confirmation with the root-level S3 key
- uploaded_s3_uri output field is set to "s3://aws-object-storage-test-2026/root-level-upload.csv"
- Extension Output JSON contains s3_uri and etag fields
