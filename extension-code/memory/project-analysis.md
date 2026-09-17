<!-- generated: 2026-09-17 09:42 -->

# Project Analysis — Universal Extension v1.0.0

## Purpose

Integrates with Amazon S3 to either list all objects in a bucket or upload a local agent-host file to S3, returning counts, URIs, and ETags as structured extension output.

---

## Execution Modes / Actions

| Mode | Trigger | Description |
|------|---------|-------------|
| List Objects | `action == "List Objects"` (default) | Calls `s3:ListObjectsV2` (paginated) on the target bucket; returns total object count and a capped list of object details (key, size, last_modified). Cap is controlled by the `UE_MAX_OUTPUT_RECORDS` env var (default 100). Updates the `object_count` output field in real-time. |
| Upload File | `action == "Upload File"` | Performs a pre-flight filesystem check that the local file exists before any AWS call, then calls `s3:PutObject`. Returns the full S3 URI and the ETag. Updates the `uploaded_s3_uri` output field in real-time. |

---

## Complete Field Table

| # | Name | Label | Type | Mapping | Required | Default | Visibility | Description |
|---|------|-------|------|---------|----------|---------|------------|-------------|
| 0 | `action` | Action | Choice | Choice Field 1 | No | `List Objects` | Always | S3 operation to perform: `List Objects` or `Upload File` |
| 1 | `aws_credentials` | AWS Credentials | Credential | Credential Field 1 | Yes | — | Always | AWS credentials — user = Access Key ID, password = Secret Access Key |
| 2 | `aws_region` | AWS Region | Text | Text Field 1 | Yes | — | Always | AWS region where the target S3 bucket resides (e.g. `us-east-1`) |
| 3 | `bucket_name` | Bucket Name | Text | Text Field 2 | Yes | — | Always | Name of the target S3 bucket |
| 4 | `local_file` | Local File Path | Text | Text Field 3 | When visible | — | Only when `action == "Upload File"` | Absolute path on the agent host for the file to upload |
| 5 | `s3_object_key` | S3 Object Key | Text | Text Field 4 | When visible | — | Only when `action == "Upload File"` | Destination object key (path within the bucket) for the uploaded file; must not start with `/` |
| 6 | `object_count` | Object Count | Text (Output Only) | Text Field 5 | — | — | Only when `action == "List Objects"` | Total objects found in the bucket (populated by extension); shown in list view; persisted on re-run |
| 7 | `uploaded_s3_uri` | Uploaded S3 URI | Text (Output Only) | Text Field 6 | — | — | Only when `action == "Upload File"` | Full S3 URI of the successfully uploaded object (populated by extension); persisted on re-run |

---

## Cross-References

### Always-Required Fields
- `aws_credentials` — required for every action
- `aws_region` — required for every action
- `bucket_name` — required for every action

### Conditionally-Required Fields (when visible)
- `local_file` — required when `action == "Upload File"` (`requireIfVisible: true`)
- `s3_object_key` — required when `action == "Upload File"` (`requireIfVisible: true`)

### Visibility Dependencies
- `local_file` → shown only when `Choice Field 1 == "Upload File"`
- `s3_object_key` → shown only when `Choice Field 1 == "Upload File"`
- `object_count` → shown only when `Choice Field 1 == "List Objects"`
- `uploaded_s3_uri` → shown only when `Choice Field 1 == "Upload File"`

### Mutually Exclusive Options
- `object_count` (output) is exclusive to the **List Objects** action
- `uploaded_s3_uri` (output) is exclusive to the **Upload File** action
- `local_file` and `s3_object_key` (inputs) are exclusive to the **Upload File** action

---

## Error Handling

| Scope | Error | Handling |
|-------|-------|----------|
| Input validation | `action` not in `["List Objects", "Upload File"]` | `DataValidationError` (exit 20) collected via `extension_manager`; raised after all field checks complete |
| Input validation | `aws_region` is blank/whitespace | `DataValidationError` (exit 20) collected; raised after all field checks |
| Input validation | `bucket_name` is blank/whitespace | `DataValidationError` (exit 20) collected; raised after all field checks |
| Input validation | `local_file` empty/None when action is Upload File | `DataValidationError` (exit 20) collected; raised after all field checks |
| Input validation | `s3_object_key` empty/None when action is Upload File | `DataValidationError` (exit 20) collected; raised after all field checks |
| Input validation | `s3_object_key` starts with `/` | `DataValidationError` (exit 20) collected; raised after all field checks |
| Upload File pre-flight | Local file path does not exist on agent host | `ValidationError` (exit 20) raised immediately before any AWS API call |
| AWS API | Credentials rejected by AWS (`InvalidClientTokenId`, `SignatureDoesNotMatch`, `InvalidAccessKeyId`) | `AuthenticationError` (exit 1) — non-transient; user must fix UAC Credential entity |
| AWS API | IAM policy denies requested operation (`AccessDenied`) | `AuthorizationError` (exit 1) — message includes operation and bucket name |
| AWS API | Bucket not found (`NoSuchBucket`) or unrecognized `ClientError`/`BotoCoreError` | `ResourceError` (exit 1) — original error detail included in message |
| Network | `EndpointResolutionError`, `ConnectTimeoutError`, `ReadTimeoutError`, `OSError`, `ConnectionError` | `ServiceConnectionError` (exit 1) — may be transient; includes endpoint and retry info where available |
| Unexpected | Any uncaught `Exception` | `UnexpectedSystemError` (exit 1) — captures `str(e)` or `type(e).__name__`; always logged |
| All errors | `ExecutionError` subclasses | Caught in `extension_start()`; `InputFields` re-created with `_skip_validation=True` for safe reporting; `build_result()` returns structured `unv_output` with errors array |
