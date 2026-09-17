# Universal Extension Requirements (Refined)

**Extension Name:** AWS Object Storage  
**Original Generated:** 2026-09-17  
**Refined:** 2026-09-17  
**Agent_id:** (not specified in source documents)  
**Requirements Completeness:** Moderate Detail  
**Target Platform:** Linux  

---

# Table of Contents

1. [Overview](#overview)
2. [Actions](#actions)
   - 2.1 [Action 1: List Objects](#action-1-list-objects)
   - 2.2 [Action 2: Upload File](#action-2-upload-file)
3. [Input Requirements](#input-requirements)
   - 3.1 [Connection Parameters](#connection-parameters)
   - 3.2 [Action-Specific Fields](#action-specific-fields)
4. [Output Requirements](#output-requirements)
   - 4.1 [On Success](#on-success)
   - 4.2 [On Error](#on-error)
5. [Authentication Requirements](#authentication-requirements)
6. [Environment Variables](#environment-variables)
7. [Operational Behavior](#operational-behavior)
8. [Implementation Notes](#implementation-notes)
   - 8.1 [Python Compatibility](#python-compatibility)
   - 8.2 [Target Platform](#target-platform)
   - 8.3 [Third-Party Services and Tools](#third-party-services-and-tools)
   - 8.4 [Error Handling](#error-handling)
   - 8.5 [Resource Cleanup](#resource-cleanup)
9. [Requirements Summary](#requirements-summary)
10. [Document Change History](#document-change-history)
11. [References](#references)

---

# Overview

This document defines the requirements for the **AWS Object Storage** Universal Extension — a Stonebranch UAC integration that provides simple AWS S3 operations for MVP/demo purposes, demonstrating that AWS S3 integration can be implemented with Stonebranch Universal Automation Center.

**Integration Purpose:** The extension enables UAC tasks to interact with AWS S3 buckets via two actions: listing objects within a bucket and uploading a local file from the Universal Agent host to an S3 bucket. All required dependencies must be bundled with the extension; nothing needs to be installed separately on the Universal Agent.

---

# Actions

## Action 1: List Objects

**Functional Requirements:**

1. The extension must connect to the specified AWS S3 bucket using the provided credentials and region.
2. The extension must retrieve and display the objects contained in the specified bucket.
3. The list of objects must include three attributes per object: key (file/path name), size, and last modified date.
4. The number of objects returned must be capped by the environment variable `UE_MAX_OUTPUT_RECORDS` (default: 100).
5. When the total number of objects in the bucket exceeds the applied cap, a truncation notice must be included in the output indicating both the total object count and the applied limit.
6. The total object count for the bucket must always be reported, regardless of whether truncation occurred.
7. The output must be presented as a three-column ASCII table in STDOUT.
8. The task's `Object Count` output field must be populated with the total number of objects found in the bucket.

## Action 2: Upload File

**Functional Requirements:**

1. The extension must validate that the specified local file exists on the Universal Agent host before attempting any AWS operation. If the file does not exist, the task must exit immediately with return code 20.
2. The extension must upload the local file to the specified S3 bucket using the specified S3 object key.
3. Upon successful upload, the extension must report the resulting S3 URI in the format `s3://<bucket>/<key>`.
4. The task's `Uploaded S3 URI` output field must be populated with the S3 URI of the successfully uploaded object.
5. The extension must use the `boto3` SDK for the upload operation.

---

# Input Requirements

## Connection Parameters

These fields are shared across all actions.

- **AWS Credentials** (credential field, required): A UAC credential entity providing the AWS Access Key ID and AWS Secret Access Key. The credential's `user` attribute holds the AWS Access Key ID; the credential's `password` attribute holds the AWS Secret Access Key.
  - Example: A UAC credential named `aws-s3-demo-cred` with `user = AKIAIOSFODNN7EXAMPLE` and `password = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
  - Applicability: List Objects, Upload File

- **AWS Region** (text, required, no default): The AWS region identifier where the target S3 bucket resides. Must match the bucket's home region.
  - Example: `us-east-1`, `eu-west-1`, `ap-southeast-2`
  - Applicability: List Objects, Upload File
  - Default Value: None — always required

- **Bucket Name** (text, required): The name of the target AWS S3 bucket.
  - Example: `my-demo-bucket`
  - Applicability: List Objects, Upload File

- **Action** (choice field, required): Selects the operation to perform.
  - Available options:
    - `List Objects` — list objects in the specified S3 bucket
    - `Upload File` — upload a local file to the specified S3 bucket
  - Default presented option: `List Objects`
  - Applicability: All actions — determines which action-specific fields are shown

## Action-Specific Fields

These fields are shown or hidden based on the selected Action.

- **Local File** (text, shown when Action = Upload File, required when visible): The absolute path to the local file on the Universal Agent host to be uploaded.
  - Example: `/data/reports/output.csv`
  - Applicability: Upload File only

- **S3 Object Key** (text, shown when Action = Upload File, required when visible): The S3 object key (destination path within the bucket) for the uploaded file.
  - Example: `reports/2026/output.csv`
  - Applicability: Upload File only

---

# Output Requirements

## On Success

### List Objects

- **Return code:** 0
- **Status description:** `Successfully listed N objects in bucket 'X'` (where N is total object count and X is bucket name)
- **Output-only fields:**
  - `Object Count` (integer): Total number of objects found in the bucket
- **Extension output (JSON):**
  ```json
  {
    "object_count": 42,
    "objects": [
      { "key": "reports/2026/output.csv", "size": 10240, "last_modified": "2026-09-01T12:00:00Z" }
    ],
    "truncated": false
  }
  ```
  - `object_count`: Total number of objects in the bucket
  - `objects`: Array of objects returned (up to the record limit), each with `key`, `size` (in bytes), and `last_modified` (ISO 8601 timestamp)
  - `truncated`: Boolean indicating whether the result set was capped by the record limit
- **STDOUT output:** A three-column ASCII table (using `tabulate` with `rounded_outline` format) with columns Key, Size, and Last Modified. Followed by a summary line showing total object count. If truncated, a notice stating the total count and the applied limit.
- **Success Criteria:**
  1. AWS credentials are accepted
  2. Bucket exists and is accessible
  3. Object list is retrieved and formatted as an ASCII table in STDOUT
  4. `Object Count` output field is populated
  5. Extension output JSON is written with `object_count`, `objects` array, and `truncated` flag
  6. Return code is 0

### Upload File

- **Return code:** 0
- **Status description:** `Successfully uploaded '/local/path/file' to s3://bucket/key`
- **Output-only fields:**
  - `Uploaded S3 URI` (text): The S3 URI of the uploaded object in the format `s3://<bucket>/<key>`
- **Extension output (JSON):**
  ```json
  {
    "s3_uri": "s3://my-demo-bucket/reports/2026/output.csv",
    "etag": "\"abc123def456...\""
  }
  ```
  - `s3_uri`: Full S3 URI of the uploaded object
  - `etag`: The S3 ETag integrity hash returned on upload
- **STDOUT output:** A single confirmation line — `Successfully uploaded /local/path/file.csv → s3://bucket/key`
- **Success Criteria:**
  1. Local file exists on the agent host (pre-flight validation passes)
  2. AWS credentials are accepted
  3. Bucket exists and is accessible
  4. File is uploaded to the specified S3 object key
  5. `Uploaded S3 URI` output field is populated
  6. Extension output JSON is written with `s3_uri` and `etag`
  7. Return code is 0

## On Error

### Failure Scenarios

| Scenario | Description | Root Causes | Return Code | Status Description Pattern |
|---|---|---|---|---|
| Local file not found | Specified local file does not exist on agent host | Incorrect path, file moved or deleted | 20 | `Validation Error: Local file '/path/file' does not exist` |
| Invalid AWS credentials | AWS rejects the provided Access Key ID or Secret Access Key | Wrong credentials, key rotated, key deactivated | 1 | `Authentication Error: Invalid AWS credentials` |
| Bucket not found or inaccessible | The specified S3 bucket cannot be found or accessed | Bucket name typo, wrong region, bucket deleted, no read permission | 1 | `S3 Error: Bucket 'X' not found or access denied` |
| Insufficient S3 permissions | Credentials are valid but lack the required S3 operation permission | IAM policy does not grant `s3:ListObjectsV2` or `s3:PutObject` | 1 | `Authorization Error: Access denied for s3:PutObject on bucket X` |
| Network / connectivity failure | Cannot reach the AWS S3 endpoint | No outbound internet access, DNS failure, firewall blocking | 1 | `Connection Error: Could not reach AWS S3 endpoint` |

**Notes:**
- Return code 20 is reserved exclusively for pre-flight input validation failures (local file existence check for Upload File). It is raised before any AWS API call is made.
- Return code 1 is used for all AWS-side runtime failures (authentication, authorization, bucket access, network).
- All error status descriptions must follow the pattern `Error Category: Description`.

### Input Validation

- The local file existence check (Upload File only) must be performed as a pre-flight validation before any AWS operation. If the file does not exist, the task must exit with return code 20 and the status description `Validation Error: Local file '<path>' does not exist`.

---

# Authentication Requirements

The extension uses AWS Access Key ID / Secret Access Key authentication via the `boto3` SDK. Credentials are sourced exclusively from a UAC Credential field attached to the task:

- The credential's `user` attribute supplies the **AWS Access Key ID**.
- The credential's `password` attribute supplies the **AWS Secret Access Key**.

No other authentication methods (IAM roles, instance profiles, environment-based credential chain) are required for this MVP.

---

# Environment Variables

- **`UE_MAX_OUTPUT_RECORDS`** (integer, default: 100): Controls the maximum number of S3 objects returned and displayed by the List Objects action. Operators can override this value per-agent or per-task via the UAC "Environment Variables" task field. When the object count exceeds this limit, a truncation notice is included in STDOUT and the `truncated` flag in the Extension Output JSON is set to `true`.

---

# Operational Behavior

**Dynamic Choice Fields:**  
Not applicable for this extension.

**Cancel Action:**  
Not specified. Standard UAC task cancellation behavior applies.

**Re-run Capability:**  
Standard UAC task re-run behavior applies. Upload File may overwrite an existing S3 object at the same key on re-run; no special re-run handling is required.

**Progress Reporting:**  
Not specified. Standard task logging via STDOUT applies. No progress bar is required.

**Dynamic Commands:**  
Not applicable for this extension.

---

# Implementation Notes

## Python Compatibility

Not specified specifically. Targeting compatibility for 3.11.

## Target Platform

Linux only — confirmed from the environment. The UAC agent runs on Linux x86_64. C-extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules.

## Third-Party Services and Tools

**AWS S3 (Amazon Simple Storage Service)**
- Short Description: Cloud object storage service used for storing and retrieving files
- Version constraints: No specific API version constraint; standard S3 ListObjectsV2 and PutObject operations
- Integration approach: Access via `boto3` Python SDK using Access Key ID / Secret Access Key authentication

**boto3 (AWS SDK for Python)**
- Short Description: Official AWS SDK providing the S3 client for listing objects and uploading files. Includes `botocore` and `s3transfer` as transitive dependencies.
- Version: 1.43.96
- Type: Pure Python — no manylinux wheel concern
- All dependencies must be bundled with the extension

**tabulate**
- Short Description: ASCII table formatting library used to render the List Objects result as a readable table in STDOUT
- Version: 0.10.0
- Type: Pure Python
- Format used: `rounded_outline`

## Error Handling

**High-level error categories:**
- Validation errors (return code 20): Input configuration mistakes caught before AWS calls (local file existence)
- Authentication errors (return code 1): Invalid or rejected AWS credentials
- Authorization errors (return code 1): Valid credentials lacking required S3 permissions
- Resource errors (return code 1): Bucket not found or inaccessible
- Network errors (return code 1): Connectivity failures reaching the AWS S3 endpoint

**Error handling strategy:** Each error category must produce a descriptive status description following the `Error Category: Description` pattern. Errors must be caught and translated into the appropriate return code and status message. Unhandled exceptions must not propagate to the operator as raw tracebacks.

**Recovery mechanisms:** None required for this MVP. No retry logic is needed.

## Resource Cleanup

- No persistent connections or temporary files are created by the extension beyond the standard `boto3` S3 client lifecycle.
- No explicit cleanup steps are required.

---

# Requirements Summary

The **AWS Object Storage** Universal Extension provides two actions — **List Objects** and **Upload File** — integrating UAC with AWS S3 via the `boto3` SDK. The extension is MVP/demo scoped and must be kept simple. All dependencies are bundled; nothing is installed separately on the agent.

Key requirements:
- Two actions selectable via a choice field: List Objects and Upload File
- AWS credentials provided via a UAC Credential entity (`user` = Access Key ID, `password` = Secret Access Key)
- AWS Region is always required with no default
- List Objects returns a three-column ASCII table (key, size, last modified) capped by `UE_MAX_OUTPUT_RECORDS` (default 100), with total count and truncation notice
- Upload File performs a pre-flight local file existence check (exit code 20 if missing) before uploading
- Two output-only fields: `Object Count` (List Objects) and `Uploaded S3 URI` (Upload File)
- Extension output JSON is produced for both actions with defined structures
- All runtime AWS errors produce return code 1 with descriptive `Error Category: Description` status messages
- Target platform: Linux x86_64
- Python dependencies: `boto3` 1.43.96, `tabulate` 0.10.0 (both pure Python)

---

# Document Change History

- 2026-09-17: Initial requirements — Moderate Detail
- 2026-09-17: Comprehensive refinement based on 6 clarification questions and user feedback covering credential mapping, region configuration, list output design, output-only field selection, STDOUT/Extension Output format, and error handling strategy

---

# References

- Original Requirements Document: `memory/requirements.md`
- Original Requirements Q&A Document: `memory/agents-memory/requirements-QnA.md`
