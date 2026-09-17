# AWS Object Storage - Implementation Analysis

**Extension Name:** *AWS Object Storage (aws-object-storage)*
**Universal Template Name:** *Aws Object Storage*
**Target Platform:** Linux

---

## Extension Overview

The AWS Object Storage extension integrates Stonebranch UAC with Amazon S3 via the `boto3` SDK, enabling two operations from a UAC task: listing objects in a bucket (with tabulated STDOUT output and a capped record count) and uploading a local agent-side file to a specified S3 destination. Authentication is exclusively via AWS Access Key ID / Secret Access Key supplied through a UAC Credential entity. All dependencies are bundled with the extension; nothing is pre-installed on the agent.

---

# Template Fields

## 1. Input Fields

**action**
- **Type**: Choice Field (Single-select)
- **Visible When**: always
- **Required When**: always
- **Options**:
  - `List Objects` — List the objects contained in the specified S3 bucket
  - `Upload File` — Upload a local file from the agent host to the specified S3 bucket
- **Default Value**: `List Objects`
- **Validation**:
  - Must be one of the defined options
- **Purpose**: Selects the S3 operation to execute; controls which action-specific fields are displayed

---

**aws_credentials**
- **Type**: Credential Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must reference a valid UAC Credential entity
  - The `user` attribute must contain the AWS Access Key ID
  - The `password` attribute must contain the AWS Secret Access Key
- **Purpose**: Supplies the AWS authentication credentials for all S3 operations. `user` = Access Key ID; `password` = Secret Access Key

---

**aws_region**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must be a valid AWS region identifier (e.g. `us-east-1`, `eu-west-1`, `ap-southeast-2`)
- **Purpose**: Identifies the AWS region where the target S3 bucket resides; must match the bucket's home region
- **Example**: `us-east-1`

---

**bucket_name**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must be a non-empty string
- **Purpose**: Name of the target AWS S3 bucket for the selected operation
- **Example**: `my-demo-bucket`

---

**local_file**
- **Type**: Text Field
- **Visible When**: `action` value is equal to `Upload File`. It is required when it's visible
- **Required When**: `action` value is equal to `Upload File`
- **Validation**:
  - Must be a non-empty absolute path string
- **Purpose**: Absolute path on the Universal Agent host filesystem for the file to be uploaded to S3
- **Example**: `/data/reports/output.csv`

---

**s3_object_key**
- **Type**: Text Field
- **Visible When**: `action` value is equal to `Upload File`. It is required when it's visible
- **Required When**: `action` value is equal to `Upload File`
- **Validation**:
  - Must be a non-empty string; should not start with `/`
- **Purpose**: Destination S3 object key (path within the bucket) for the uploaded file
- **Example**: `reports/2026/output.csv`

---

## 2. Output Fields

**object_count**
- **Type**: Text Output
- **Visible When**: `action` is `List Objects`
- **Purpose**: Total number of objects found in the bucket for the List Objects action, regardless of any truncation applied to STDOUT or Extension Output
- **Examples**: `"42"`, `"0"`, `"1500"`

---

**uploaded_s3_uri**
- **Type**: Text Output
- **Visible When**: `action` is `Upload File`
- **Purpose**: The full S3 URI of the successfully uploaded object in the format `s3://<bucket>/<key>`, populated after a successful Upload File operation
- **Examples**: `"s3://my-demo-bucket/reports/2026/output.csv"`, `"s3://archive-bucket/backups/data.tar.gz"`

---

## 3. Field Ordering

The task form uses a **2-column grid layout**.

**Field Order (Visual Layout):**

```
┌─────────────────────────────────────────┐
│                  action                 │  ← Full-width (primary action selector)
├─────────────────────────────────────────┤
│              aws_credentials            │  ← Full-width (credential)
├─────────────────────────────────────────┤
│    aws_region       │   bucket_name     │  ← Half-width pair (always visible)
├─────────────────────┼───────────────────┤
│    local_file       │  s3_object_key    │  ← Half-width pair (Upload File only)
├─────────────────────┴───────────────────┤
│              object_count               │  ← Full-width output (List Objects only)
├─────────────────────────────────────────┤
│              uploaded_s3_uri            │  ← Full-width output (Upload File only)
└─────────────────────────────────────────┘
```

---

# Actions

## Action 1: List Objects

**Description**: Connects to the specified AWS S3 bucket and retrieves a paginated list of all objects. The result is printed as a three-column ASCII table (Key, Size, Last Modified) to STDOUT, capped by the `UE_MAX_OUTPUT_RECORDS` environment variable (default: 100). The total object count is always reported. If the result was truncated, a notice is appended to STDOUT. The `object_count` output field is populated with the total count.

### Input Requirements

- **action** — must be `List Objects`
- **aws_credentials** — provides AWS Access Key ID (`user`) and Secret Access Key (`password`)
- **aws_region** — target S3 bucket region
- **bucket_name** — target S3 bucket name
- Environment variable **`UE_MAX_OUTPUT_RECORDS`** — read at runtime (default: `100`)

### Execution Flow

**Step 1: Read inputs**
- Extract `aws_credentials.user` as `access_key_id` and `aws_credentials.password` as `secret_access_key`
- Extract `aws_region` and `bucket_name` from input fields
- Read `UE_MAX_OUTPUT_RECORDS` from environment; parse as integer; default to `100` if absent or non-integer

**Step 2: Initialize S3 client**
- Instantiate a boto3 S3 client using `access_key_id`, `secret_access_key`, and `aws_region`
- Any initialization error (invalid credentials format, unreachable endpoint) is caught and translated to the appropriate custom exception

**Step 3: Paginate and collect all objects**
- Call `list_objects_v2` with pagination; iterate all pages
- For each object record collect: `key` (string), `size` (integer, bytes), `last_modified` (ISO 8601 UTC string)
- Accumulate the full list and compute `total_count = len(all_objects)`

**Step 4: Apply truncation cap**
- `display_objects = all_objects[:max_records]`
- `truncated = total_count > max_records`

**Step 5: Format and print STDOUT**
- Render `display_objects` using `tabulate` with `tablefmt="rounded_outline"` and headers `["Key", "Size", "Last Modified"]`
- Print the table
- Print summary line: `Total objects in bucket: {total_count}`
- If `truncated` is true, print additional line: `Note: Output truncated to {max_records} records. Total objects in bucket: {total_count}`

**Step 6: Populate output field**
- Set `object_count` output field to string representation of `total_count`

**Step 7: Return Extension Output**
- Construct result with `object_count`, `objects` (array of display_objects with key/size/last_modified), and `truncated` flag
- Return exit code `0` and status description `Successfully listed {total_count} objects in bucket '{bucket_name}'`

### Output Examples

**STDOUT**:
```
╭─────────────────────────────────────┬──────────┬──────────────────────────╮
│ Key                                 │     Size │ Last Modified            │
├─────────────────────────────────────┼──────────┼──────────────────────────┤
│ reports/2026/output.csv             │    10240 │ 2026-09-01T12:00:00Z     │
│ backups/daily/2026-09-16.tar.gz     │ 52428800 │ 2026-09-16T03:00:00Z     │
╰─────────────────────────────────────┴──────────┴──────────────────────────╯
Total objects in bucket: 2
```

*(If truncated with 150 objects but max_records=100):*
```
... [table with 100 rows] ...
Total objects in bucket: 150
Note: Output truncated to 100 records. Total objects in bucket: 150
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "object_count": 2,
    "objects": [
      { "key": "reports/2026/output.csv", "size": 10240, "last_modified": "2026-09-01T12:00:00Z" },
      { "key": "backups/daily/2026-09-16.tar.gz", "size": 52428800, "last_modified": "2026-09-16T03:00:00Z" }
    ],
    "truncated": false
  }
}
```

*Note: The Extension Output also includes `exit_code`, `status_description`, and `invocation` elements added automatically during implementation time.*

### Success Criteria

1. AWS credentials are accepted by the S3 API
2. Bucket exists and is accessible with `s3:ListObjectsV2` permission
3. Object list is retrieved across all pages and formatted as a three-column ASCII table in STDOUT
4. `object_count` output field is populated with the total count
5. Extension Output JSON contains `object_count`, `objects` array (up to `max_records` entries), and `truncated` flag
6. Return code is `0`

---

## Action 2: Upload File

**Description**: Validates that the specified local file exists on the agent host (exit code 20 if not), then uploads it to the specified S3 bucket at the given object key using `boto3`. Upon success, prints a confirmation line to STDOUT, populates the `uploaded_s3_uri` output field, and returns the S3 URI and ETag in the Extension Output JSON.

### Input Requirements

- **action** — must be `Upload File`
- **aws_credentials** — provides AWS Access Key ID (`user`) and Secret Access Key (`password`)
- **aws_region** — target S3 bucket region
- **bucket_name** — target S3 bucket name
- **local_file** — absolute path to the file on the agent host
- **s3_object_key** — destination S3 object key within the bucket

### Execution Flow

**Step 1: Read inputs**
- Extract `aws_credentials.user` as `access_key_id` and `aws_credentials.password` as `secret_access_key`
- Extract `aws_region`, `bucket_name`, `local_file`, and `s3_object_key` from input fields

**Step 2: Pre-flight local file validation**
- Check whether the path `local_file` exists on the agent host filesystem
- If it does not exist: immediately exit with return code `20` and status description `Validation Error: Local file '{local_file}' does not exist`
- No S3 API calls are made before this check passes

**Step 3: Initialize S3 client**
- Instantiate a boto3 S3 client using `access_key_id`, `secret_access_key`, and `aws_region`

**Step 4: Upload file to S3**
- Call `upload_file` (boto3 S3 client method) with `local_file` path, `bucket_name`, and `s3_object_key`
- On completion, retrieve the ETag from the S3 response (ETag is returned by the underlying PutObject response; access via boto3 callback or head_object if needed)
- On any error, catch and translate to the appropriate custom exception

**Step 5: Compute S3 URI**
- `s3_uri = f"s3://{bucket_name}/{s3_object_key}"`

**Step 6: Print STDOUT**
- Print: `Successfully uploaded {local_file} → s3://{bucket_name}/{s3_object_key}`

**Step 7: Populate output field**
- Set `uploaded_s3_uri` output field to `s3_uri`

**Step 8: Return Extension Output**
- Construct result with `s3_uri` and `etag`
- Return exit code `0` and status description `Successfully uploaded '{local_file}' to s3://{bucket_name}/{s3_object_key}`

### Output Examples

**STDOUT**:
```
Successfully uploaded /data/reports/output.csv → s3://my-demo-bucket/reports/2026/output.csv
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "s3_uri": "s3://my-demo-bucket/reports/2026/output.csv",
    "etag": "\"abc123def456789012345678901234ab\""
  }
}
```

*Note: The Extension Output also includes `exit_code`, `status_description`, and `invocation` elements added automatically during implementation time.*

### Success Criteria

1. Local file exists on the agent host (pre-flight validation passes)
2. AWS credentials are accepted by the S3 API
3. Bucket exists and is accessible with `s3:PutObject` permission
4. File is uploaded to the specified S3 object key
5. `uploaded_s3_uri` output field is populated with the S3 URI
6. Extension Output JSON contains `s3_uri` and `etag`
7. Return code is `0`

---

# Progress Reporting

Progress Reporting (percentage of completion report) is not required.

---

# Dynamic Choice Field Population

No Dynamic choice fields should be implemented.

---

# Cancellation Behavior

Default cancellation logic is used (TERM signal). No custom cancellation code is required for this extension.

---

# Re-Run Behavior

Re-runs are treated as initial executions. No special re-run logic is required. For Upload File, re-running will overwrite an existing S3 object at the same key — this is acceptable and expected behavior.

---

# Dynamic Commands

No Dynamic commands should be implemented.

---

# Utility Modules

## Required Utility Modules

### 1. S3Manager

**Purpose:** Encapsulates all boto3 S3 interactions. Initializes the S3 client with the supplied credentials and region, exposes methods for listing and uploading, and translates all botocore/boto3 exceptions into extension-specific custom exceptions.

**Required Capabilities:**

**Client Initialization:**
- Accept `access_key_id` (str), `secret_access_key` (str), and `region` (str)
- Construct a boto3 S3 client configured with those explicit credentials and the given region
- No credential chain fallback — credentials are always passed explicitly

**Object Listing:**
- Accept `bucket_name` (str)
- Use paginated `list_objects_v2` API calls to retrieve all objects in the bucket across all pages
- For each object, extract and return: `key` (str), `size` (int, bytes), `last_modified` (ISO 8601 UTC string formatted as `YYYY-MM-DDTHH:MM:SSZ`)
- Return a tuple of `(all_objects: list[dict], total_count: int)`

**File Upload:**
- Accept `local_file_path` (str), `bucket_name` (str), `s3_object_key` (str)
- Call boto3 `upload_file` to transfer the local file to the specified S3 destination
- Return the ETag of the uploaded object (retrieved via the S3 head_object response after upload, or from the upload response if available)
- ETag is returned as a string (including surrounding quotes as returned by AWS)

**Exception Translation:**
- `botocore.exceptions.ClientError` with error code `InvalidClientTokenId` or `SignatureDoesNotMatch` → raise `AuthenticationError`
- `botocore.exceptions.ClientError` with error code `AccessDenied` → raise `AuthorizationError` including the operation name and bucket name in the message
- `botocore.exceptions.ClientError` with error code `NoSuchBucket` → raise `ResourceError` with bucket name in message
- `botocore.exceptions.EndpointResolutionError`, `botocore.exceptions.ConnectTimeoutError`, `botocore.exceptions.ReadTimeoutError`, or any `OSError`/`ConnectionError` during API call → raise `ConnectionError`
- Any other unrecognized `botocore.exceptions.BotoCoreError` or `botocore.exceptions.ClientError` → raise `ResourceError` with the original error detail in the message

**Used By:** `list_objects` action, `upload_file` action

---

### 2. OutputFormatter

**Purpose:** Produces human-readable STDOUT for the List Objects action using the `tabulate` library.

**Required Capabilities:**

**Table Rendering:**
- Accept a list of object dicts (each with `key`, `size`, `last_modified`)
- Render as a three-column table using `tabulate` with `tablefmt="rounded_outline"` and headers `["Key", "Size", "Last Modified"]`
- Return the formatted table string

**Summary Line:**
- Accept `total_count` (int)
- Return the string: `Total objects in bucket: {total_count}`

**Truncation Notice:**
- Accept `total_count` (int) and `max_records` (int)
- Return the string: `Note: Output truncated to {max_records} records. Total objects in bucket: {total_count}`
- This notice is appended to STDOUT only when `total_count > max_records`

**Used By:** `list_objects` action

---

## Exception Mapping Strategy

**Validation Errors:**
- Local file path does not exist on agent host → `ValidationError` (exit code 20, user input error — checked before any AWS call)

**Authentication Errors:**
- boto3 ClientError: `InvalidClientTokenId` or `SignatureDoesNotMatch` → `AuthenticationError` (exit code 1, non-transient — user must correct credentials)

**Authorization Errors:**
- boto3 ClientError: `AccessDenied` → `AuthorizationError` (exit code 1, user IAM policy configuration error)

**Resource Errors:**
- boto3 ClientError: `NoSuchBucket` → `ResourceError` (exit code 1, user configuration error — wrong bucket name or region)
- Any other unrecognized boto3/botocore ClientError → `ResourceError` (exit code 1, system/configuration error)

**Network / Connectivity Errors:**
- `EndpointResolutionError`, `ConnectTimeoutError`, `ReadTimeoutError`, `ConnectionError`, `OSError` during API call → `ConnectionError` (exit code 1, potentially transient — network or DNS issue)

**Exit Code Guide:**
- Exit code 0: Successful execution
- Exit code 1: AWS-side runtime failures (authentication, authorization, resource, network)
- Exit code 20: Pre-flight input validation failure (local file not found)

---

# Dependencies

## 1. External API Dependencies

**1. Amazon S3 (Simple Storage Service)**
- **Endpoint**: `https://s3.{region}.amazonaws.com` (resolved automatically by boto3 from the configured region)
- **Purpose**: Cloud object storage — used for listing bucket contents and uploading files
- **Protocol**: HTTPS
- **Method**: GET (ListObjectsV2), PUT (PutObject / upload_file)
- **Authentication**: AWS Access Key ID + Secret Access Key via boto3 credential injection (not environment-based chain)
- **Response Format**: XML (parsed transparently by boto3 into Python dicts)
- **Data Retrieved/Sent**:
  - List Objects: object key, size (bytes), last modified timestamp per object
  - Upload File: local file binary stream uploaded as S3 object; ETag returned on completion

**General API Requirements:**
- Valid AWS account with an IAM user or role holding `s3:ListObjectsV2` permission for List Objects and `s3:PutObject` permission for Upload File on the target bucket
- No API key setup beyond the UAC Credential entity — boto3 handles endpoint resolution

---

## 2. Python version dependency

Python >= 3.11 is required, as specified by the extension configuration (`extension.yml`).

---

## 3. Target Platform

Linux (x86_64). C-extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules. Both `boto3` and `tabulate` are pure-Python and compatible with all platforms.

---

## 4. Python Library Dependencies

**1. boto3**
- **Purpose**: Official AWS SDK for Python; provides the S3 client used for ListObjectsV2 and PutObject (upload_file) operations
- **Version**: `1.43.96`
- **Installation**: `pip install boto3==1.43.96`
- **Usage**: Instantiated as an S3 client in S3Manager; used for all AWS API calls
- **Features Used**: `boto3.client("s3", ...)`, `list_objects_v2` with pagination, `upload_file`, botocore exception classes

**2. tabulate**
- **Purpose**: Pure-Python library for rendering Python data as formatted ASCII tables in STDOUT
- **Version**: `0.10.0`
- **Installation**: `pip install tabulate==0.10.0`
- **Usage**: Called in OutputFormatter to produce the `rounded_outline` three-column table for the List Objects action
- **Features Used**: `tabulate(data, headers=..., tablefmt="rounded_outline")`

---

## 5. Python Standard Library Dependencies

**1. os**
- **Purpose**: Filesystem and environment variable access
- **Version**: Standard library (Python 3.11+)
- **Installation**: No installation required
- **Usage**: `os.path.exists()` for local file pre-flight validation in Upload File; `os.environ.get()` to read `UE_MAX_OUTPUT_RECORDS`
- **Features Used**: `os.path.exists`, `os.environ.get`

---

## 6. CLI Tool Dependencies

No Dependencies.

---

## 7. Environment Variables

**`UE_MAX_OUTPUT_RECORDS`** (integer, optional):
- **Purpose**: Caps the number of S3 objects returned and displayed in STDOUT and included in the Extension Output `objects` array for the List Objects action
- **Default**: `100` (applied when the variable is absent or cannot be parsed as an integer)
- **Usage**: Read in the List Objects execution flow before the truncation step; if the total object count exceeds this value, only the first `UE_MAX_OUTPUT_RECORDS` objects are displayed and the `truncated` flag is set to `true`
- **Examples**: `50`, `200`, `500`
