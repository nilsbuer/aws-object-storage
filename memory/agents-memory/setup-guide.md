# Environment Setup Guide — AWS Object Storage Extension

Before running acceptance tests, prepare the following external service entities and agent host resources.

---

## 🌐 EXTERNAL SERVICE SETUP: AWS S3

The extension connects to Amazon S3 to list objects and upload files. The following must be created on AWS before tests can run:

### 1. AWS S3 Bucket
   - **What**: An Amazon S3 bucket that will serve as the test target for List Objects and Upload File operations
   - **Why**: Both test actions require a valid, accessible bucket. The extension's test suite will perform list and upload operations against this bucket
   - **How**: 
     1. Log in to the AWS Management Console
     2. Navigate to Amazon S3
     3. Click "Create Bucket"
     4. Choose a globally unique bucket name (e.g., `aws-object-storage-test-2026`)
     5. Select the region where you want the bucket (e.g., `us-east-1`)
     6. Leave default settings and click "Create Bucket"
   - **Example**: Bucket name: `aws-object-storage-test-2026`, Region: `us-east-1`

### 2. AWS IAM User with S3 Permissions
   - **What**: An IAM user with programmatic access (Access Key ID and Secret Access Key) and permissions to perform `s3:ListObjectsV2` and `s3:PutObject` operations on the test bucket
   - **Why**: The extension authenticates to AWS using explicit Access Key credentials (not environment-based credential chain). Tests require valid credentials with appropriate S3 permissions
   - **How**:
     1. Log in to the AWS Management Console
     2. Navigate to IAM → Users
     3. Click "Create User"
     4. Enter a username (e.g., `uac-extension-test`)
     5. Click "Next", then "Create User"
     6. On the user details page, click "Create Access Key"
     7. Select "Application running outside AWS"
     8. Click "Next" and "Create Access Key"
     9. Copy the Access Key ID and Secret Access Key to a secure location
     10. Attach an inline policy to grant S3 permissions:
         - Click "Add Permissions" → "Create Inline Policy"
         - Use this JSON policy (replace `BUCKET_NAME` with your test bucket name):
         ```json
         {
           "Version": "2012-10-17",
           "Statement": [
             {
               "Effect": "Allow",
               "Action": [
                 "s3:ListObjectsV2",
                 "s3:GetObject",
                 "s3:PutObject"
               ],
               "Resource": [
                 "arn:aws:s3:::BUCKET_NAME",
                 "arn:aws:s3:::BUCKET_NAME/*"
               ]
             }
           ]
         }
         ```
         - Click "Review Policy", then "Create Policy"
   - **Example**: User: `uac-extension-test`, Access Key ID: `AKIAIOSFODNN7EXAMPLE`, Secret Access Key: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

### 3. Test Objects in the S3 Bucket (for List Objects Action)
   - **What**: A set of test objects (files) uploaded to the test bucket so that the List Objects action can retrieve and display them
   - **Why**: The List Objects action retrieves object metadata from the bucket. Without test objects, the action returns an empty list; tests expect to find objects
   - **How**:
     1. Use the AWS Management Console or AWS CLI to upload test files to the bucket
     2. Upload at least 2–3 test files with different sizes and paths to validate table formatting
     3. Example using AWS CLI:
        ```bash
        # First, create test files locally
        echo "Sample report data" > report.csv
        dd if=/dev/zero of=largefile.bin bs=1M count=10  # 10 MB file
        echo "Backup archive" > backup.tar.gz
        
        # Upload to bucket (replace BUCKET_NAME and region)
        aws s3 cp report.csv s3://BUCKET_NAME/reports/2026/report.csv --region us-east-1
        aws s3 cp largefile.bin s3://BUCKET_NAME/backups/2026/largefile.bin --region us-east-1
        aws s3 cp backup.tar.gz s3://BUCKET_NAME/archives/backup.tar.gz --region us-east-1
        ```
   - **Example Objects**:
     - `reports/2026/report.csv` (18 bytes)
     - `backups/2026/largefile.bin` (10,485,760 bytes)
     - `archives/backup.tar.gz` (14 bytes)

---

## 🖥️ AGENT HOST SETUP

The UAC Agent machine must have the following resources prepared before tests execute.

### 1. Test File for Upload File Action
   - **What**: A local file on the agent host that will be uploaded to S3 during the Upload File test
   - **Why**: The Upload File action validates that the specified local file exists before uploading. Tests require a valid file at the specified path
   - **How**:
     1. Create a directory for test data in your home directory:
        ```bash
        mkdir -p ~/uac-extension-tests/input
        ```
     2. Create a test file:
        ```bash
        echo "Sample test data for upload" > ~/uac-extension-tests/input/test-upload.csv
        ```
     3. Verify the file exists and is readable:
        ```bash
        ls -la ~/uac-extension-tests/input/test-upload.csv
        cat ~/uac-extension-tests/input/test-upload.csv
        ```
   - **Example**: File path: `~/uac-extension-tests/input/test-upload.csv`, Content: `Sample test data for upload`

### 2. Output Directory for Test Results
   - **What**: A directory where test output and logs can be stored during extension execution
   - **Why**: Tests may generate output files, logs, or artifacts that need to be captured for validation and debugging
   - **How**:
     1. Create an output directory:
        ```bash
        mkdir -p ~/uac-extension-tests/output
        ```
     2. Ensure the directory is writable:
        ```bash
        ls -ld ~/uac-extension-tests/output
        chmod 755 ~/uac-extension-tests/output
        ```
   - **Example**: Directory: `~/uac-extension-tests/output`

---

## 📋 CHECKLIST

Before starting tests, verify all items are complete:

  ☐ AWS S3 bucket created (e.g., `aws-object-storage-test-2026` in `us-east-1`)
  ☐ IAM user created with Access Key ID and Secret Access Key
  ☐ IAM user has inline policy granting `s3:ListObjectsV2`, `s3:GetObject`, and `s3:PutObject` on the test bucket
  ☐ At least 2–3 test objects uploaded to the bucket (e.g., `reports/2026/report.csv`, `backups/2026/largefile.bin`)
  ☐ Test file created on agent host at `~/uac-extension-tests/input/test-upload.csv`
  ☐ Output directory created at `~/uac-extension-tests/output` and is writable
  ☐ Verified: Access Key ID and Secret Access Key are valid and accessible for UAC Credential creation
  ☐ Verified: S3 bucket name and region match the values that will be used in test task JSON
  ☐ Verified: Agent host has sufficient disk space for test uploads and outputs (~100 MB minimum recommended)
