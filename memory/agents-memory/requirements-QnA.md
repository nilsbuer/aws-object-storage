# Requirements Completeness Assessment

The requirements are **Moderate Detail**. The core integration is clearly established: the extension targets AWS S3 via the `boto3` SDK, two actions are precisely named (**List Objects** and **Upload File**), and the primary input fields (AWS Credentials, AWS Region, Bucket Name, Local File, S3 Object Key) are explicitly listed. The MVP/demo intent and the simplicity constraint are unambiguous.

To build this out, a few open decisions remain: how AWS credentials map to UAC's credential attributes, what information the list operation should display and at what scale, which output-only fields to expose in the UAC UI, and how specific error conditions should be signaled back to the operator.

---

# Platform Compatibility

The build environment is explicitly **Linux x86_64** (`environment.md`: `OS: Linux`, `Architecture: x86_64`). The UAC agent target is Linux. This classifies the platform as **Linux-only** — modules with confirmed `manylinux_2_17_x86_64` wheels are viable in addition to pure-Python modules.

**Platform Compatibility from Requirements**: Linux  
**Platform Compatibility Agreement**: Linux-only — confirmed from `environment.md`

---

# Python Modules and Versions

## Researched Modules

**boto3**
- **Module Purpose**: AWS SDK for Python — provides the S3 client used for listing objects and uploading files
- **Version**: 1.43.96
- **Type**: Pure Python

**botocore**
- **Module Purpose**: Core AWS SDK library — bundled automatically as a transitive dependency of boto3
- **Version**: 1.43.96
- **Type**: Pure Python

**s3transfer**
- **Module Purpose**: S3 multipart and managed file transfer — bundled automatically as a transitive dependency of boto3
- **Version**: 0.19.2
- **Type**: Pure Python

**tabulate**
- **Module Purpose**: ASCII table formatting for displaying S3 object listings in STDOUT
- **Version**: 0.10.0
- **Type**: Pure Python

## Agreed Python Modules and Versions

[Placeholder — to be confirmed once questions are answered]

| Module Name | Module Purpose | Version | Type |
|---|---|---|---|
| boto3 | AWS S3 SDK (includes botocore, s3transfer as transitive deps) | 1.43.96 | Pure Python |
| tabulate | ASCII table output for object listings | 0.10.0 | Pure Python |

---

# Question Rationale

The requirements provide solid scope definition — actions, SDK choice, and field names are all clear. The six questions below address four remaining open areas that must be resolved before analysis can produce a complete blueprint:

1. **Credential attribute mapping** — UAC credential entities use specific named attributes (`user`, `password`, etc.); mapping each AWS value to the right attribute is required to design the credential field correctly.
2. **List Objects output design** — what columns and record volume are appropriate for an MVP demo affects both STDOUT layout and template field design.
3. **Output-only field selection** — which task-level output fields to expose in the UAC UI determines what operators see in the task list view after execution.
4. **Error signaling** — which conditions to treat as validation errors (exit code 20) versus runtime failures (exit code 1) shapes how useful the error experience is for operators.

---

# Clarifying Questions for Requirements Refinement

## Authentication & Security

**Question 1**: How should AWS credentials map to the UAC Credential Field attributes?

UAC Credential entities are the secure mechanism for passing sensitive values to an extension. Each credential has named attribute slots: `user` (always required, intended as the account identifier — not for secrets), `password` (for secrets up to 255 characters), and `token` (for longer secrets).

For AWS S3 authentication via `boto3`, two values are needed:
- **AWS Access Key ID** — the non-sensitive account identifier (format: `AKIAIOSFODNN7EXAMPLE`)
- **AWS Secret Access Key** — the sensitive secret value (format: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)

Available options:

- **Option A (Recommended)**: `user` = AWS Access Key ID, `password` = AWS Secret Access Key — follows UAC best practice directly.
- **Option B**: Store both values in a single credential's `password` attribute as a combined string — not recommended; brittle to parse and non-standard.

- **Question Type**: Clarification on existing requirement
- **Context & Resources**: [boto3 Credentials Guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) — explains how Access Key ID and Secret Access Key are used together for programmatic access.
- **Question Dependencies**: None
- **Recommended Answer**: Option A — `user` = AWS Access Key ID, `password` = AWS Secret Access Key.
- **Rationale**: This is the canonical UAC pattern for API key-style credentials. The `user` slot holds the identifier (Access Key ID); the `password` slot holds the secret. No extra fields are needed, and the credential entity is self-documenting in the UAC UI.
- **Trade-offs**: No significant trade-offs. Option A is the only clean mapping for this credential shape.
- **Requirement Impact**: None — the single "AWS Credentials" credential field in the requirements maps directly to this approach.
- **User's Answer**: Option A — `user` = AWS Access Key ID, `password` = AWS Secret Access Key

---

## Core Business Logic

**Question 2**: Should the AWS Region field have a default value, or should it always be required with no default?

The `boto3` S3 client must be initialized with the region of the target bucket. If the region is wrong, operations either fail with a `PermanentRedirect` error or silently route to the wrong endpoint. The task field accepts values like `us-east-1`, `eu-west-1`, `ap-southeast-2`.

Options:
- **Option A (Recommended)**: No default value — field is always required. Operators must explicitly specify the region at task definition time.
- **Option B**: Default to `us-east-1` — convenient shortcut for demo environments where the test bucket is in US East.

- **Question Type**: New Discussion Topic
- **Context & Resources**: [boto3 Region Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#region-name) — region must match the bucket's home region for most S3 API operations.
- **Question Dependencies**: None
- **Recommended Answer**: Option A — no default, always required.
- **Rationale**: Explicit configuration avoids a common class of confusing errors. Since the operator will know which region their S3 bucket is in, requiring the field is minimal friction with meaningful benefit.
- **Trade-offs**: Option B saves one step at task setup time but can cause silent misconfiguration if the demo bucket is not in `us-east-1`. Option A makes the configuration intent unambiguous.
- **Requirement Impact**: AWS Region field becomes a required field with no default value in the template.
- **User's Answer**: Option A — no default, always required

---

**Question 3**: What information should the List Objects operation display, and how many objects should be shown?

**Output Content** — when listing S3 objects, two options:
- **Option A**: Object keys (file/path names) only — the most minimal output
- **Option B (Recommended)**: Object key + file size + last modified date — the same three columns shown by any S3 browser, visually compelling for a demo

**Record Limit** — S3 buckets can hold millions of objects; without a cap, listing a large bucket will be impractical:
- **Option X (Recommended)**: Use the environment variable `UE_MAX_OUTPUT_RECORDS` (default: 100 objects). No extra task field — operators can override it per-agent or per-task via the standard "Environment Variables" task field. When the cap is reached, a note indicates the total object count and the applied limit.
- **Option Y**: Add a "Max Objects" integer task field — gives per-task control at the cost of an extra UI field.

- **Question Type**: New Discussion Topic
- **Context & Resources**: [S3 ListObjectsV2 API](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_objects_v2.html) — supports server-side pagination; object count can be retrieved without fetching all content. | UE Large Output Safety Net Pattern (recommends `UE_MAX_OUTPUT_RECORDS`, default 100).
- **Question Dependencies**: Answer feeds into Q5 (STDOUT column layout).
- **Recommended Answer**: Option B (key + size + last modified) with Option X (`UE_MAX_OUTPUT_RECORDS` env var, default 100). Result: a three-column ASCII table in STDOUT, capped at 100 rows, with total object count always shown.
- **Rationale**: A three-column table is significantly more informative than a plain key list and requires minimal extra code. The environment variable cap keeps the task output database-friendly without cluttering the UI.
- **Trade-offs**: Option A is marginally simpler to implement. Option Y offers finer per-task control but adds a field for an MVP that explicitly requests simplicity.
- **Requirement Impact**: STDOUT for List Objects becomes an ASCII table. The environment variable `UE_MAX_OUTPUT_RECORDS` is the control point for the record cap.
- **User's Answer**: Option B (key + size + last modified) with Option X (UE_MAX_OUTPUT_RECORDS env var, default 100)

---

## Output Fields & Task Results

**Question 4**: Which output-only fields should the extension expose in the UAC task UI?

Output-only fields display specific values in the UAC task execution and list views — they give operators a quick result glance without opening the full log. The architecture recommends 2–3 fields maximum.

For this extension, each action produces a distinct meaningful result:
- **List Objects** → total number of objects found in the bucket
- **Upload File** → the complete S3 URI of the uploaded object (e.g., `s3://my-bucket/reports/2026/output.csv`)

Options:
- **Option A (Recommended)**: Two output-only fields — **Object Count** (populated after List Objects) and **Uploaded S3 URI** (populated after Upload File). The standard Status Description (automatically captured by UAC) covers overall success/failure.
- **Option B**: Single shared **Result** text field with a human-readable summary for both actions.
- **Option C**: No output-only fields — rely entirely on STDOUT and the status description.

- **Question Type**: New Discussion Topic
- **Context & Resources**: UE Multi-Channel Output Pattern | UE Resource Identifier Persistence Pattern — `Uploaded S3 URI` can be referenced by downstream tasks in a UAC workflow via the output field value.
- **Question Dependencies**: None
- **Recommended Answer**: Option A — Object Count + Uploaded S3 URI.
- **Rationale**: Two focused fields are more readable in the UAC task list view than a single combined field. The S3 URI is especially useful: it lets subsequent tasks in a workflow reference the exact uploaded object without parsing STDOUT.
- **Trade-offs**: Option A adds two template fields. Option C is minimal but provides no at-a-glance value in the task list. Option B is a reasonable middle ground but less precise.
- **Requirement Impact**: Two Output Only fields added to the template: `Object Count` (integer display, List Objects) and `Uploaded S3 URI` (text, Upload File).
- **User's Answer**: Option A — Object Count + Uploaded S3 URI output-only fields

---

**Question 5**: What should STDOUT display, and what should the Extension Output (JSON) contain for each action?

**STDOUT** is the human-readable output shown in the UAC task execution log during and after the run.  
**Extension Output** is a machine-readable JSON payload available once the task reaches a terminal state — used by downstream automation and for auditing.

**For List Objects:**

STDOUT options:
- **Option A**: Plain text list of object keys, one per line
- **Option B (Recommended)**: ASCII table with key, size, and last modified columns (using `tabulate` with `rounded_outline` format), followed by a count summary line and a truncation notice if the record limit was applied

Extension Output options:
- **Option X (Recommended)**: `{ "object_count": N, "objects": [ { "key": "...", "size": N, "last_modified": "..." }, ... ], "truncated": true/false }`
- **Option Y**: Minimal — just `{ "object_count": N }`

**For Upload File:**

STDOUT (Recommended): Single confirmation line — `Successfully uploaded /local/path/file.csv → s3://bucket/key`

Extension Output (Recommended): `{ "s3_uri": "s3://bucket/key", "etag": "\"abc123...\"" }` — the ETag is the S3 integrity hash returned on upload, useful for verification in downstream automation.

- **Question Type**: New Discussion Topic
- **Context & Resources**: UE Multi-Channel Output Pattern | UE Output Verbosity Selection Pattern | [tabulate library](https://pypi.org/project/tabulate/) — `rounded_outline` format produces clean bordered tables in monospace terminal output.
- **Question Dependencies**: Q3 answer determines the columns present in the ASCII table.
- **Recommended Answer**: Option B (ASCII table) for List STDOUT; single confirmation line for Upload STDOUT. Option X (full object list JSON) for List Extension Output; S3 URI + ETag for Upload Extension Output.
- **Rationale**: An ASCII table is professional and visually impactful in a demo context. The full Extension Output JSON enables programmatic downstream consumption — a key value for a Stonebranch demo since it shows orchestration potential.
- **Trade-offs**: Option A (plain list) is simpler but less compelling visually. Option Y (count only) in Extension Output is minimal but limits what downstream tasks can do with the results.
- **Requirement Impact**: `tabulate` is added to `requirements.txt` (already in the agreed modules list). Extension Output structure is defined for both actions.
- **User's Answer**: ASCII table on STDOUT for List Objects; simple confirmation line for Upload File; full object list JSON in Extension Output for List; S3 URI + ETag for Upload

---

## Functional Behavior

**Question 6**: How should the extension handle specific error conditions?

For an MVP, clear error messages are critical — operators need to know exactly what went wrong and what to fix. The following scenarios are anticipated:

| Error Scenario | Proposed Exit Code | Proposed Status Description |
|---|---|---|
| Invalid AWS credentials | 1 (runtime failure) | `Authentication Error: Invalid AWS credentials` |
| Bucket does not exist or is inaccessible | 1 (runtime failure) | `S3 Error: Bucket 'X' not found or access denied` |
| Local file not found (Upload only) | 20 (validation error) | `Validation Error: Local file '/path/file' does not exist` |
| Insufficient S3 permissions | 1 (runtime failure) | `Authorization Error: Access denied for s3:PutObject on bucket X` |
| Network / connectivity failure | 1 (runtime failure) | `Connection Error: Could not reach AWS S3 endpoint` |

The key decision is whether the **local file existence check** for Upload File should be treated as a pre-flight validation (exit code 20, before any AWS call is made) or as a runtime failure (exit code 1):

- **Option A (Recommended)**: Validate local file existence before attempting the upload — exit code 20. This gives the operator an immediate, actionable error without consuming any AWS API calls.
- **Option B**: Attempt the upload and let the file-not-found OS exception propagate as a runtime failure (exit code 1). Slightly simpler code path.

- **Question Type**: New Discussion Topic
- **Context & Resources**: UE Return Code conventions — `0` = success, `1` = runtime failure, `20` = validation error (input/configuration problem the operator can fix without re-running infrastructure).
- **Question Dependencies**: None
- **Recommended Answer**: Option A — validate local file existence as a pre-flight check (exit code 20). All AWS-side errors (auth, bucket, permissions, network) are runtime failures (exit code 1) with a descriptive status message following the `Error Category: Description` format.
- **Rationale**: A missing local file is a configuration mistake that the operator can correct immediately — exiting with code 20 signals "fix your input" rather than "something broke at runtime." The distinction also allows UAC workflow engineers to set up different failure-handling paths for validation versus runtime errors.
- **Trade-offs**: Option A adds a brief pre-check but produces a measurably better operator experience for one of the most common mistakes. Option B is one fewer code branch but blurs the error category.
- **Requirement Impact**: None — aligns with the MVP simplicity goal while maintaining clear operator feedback.
- **User's Answer**: Option A — validate local file existence before upload (exit 20); all AWS/network errors as runtime failure (exit 1)
