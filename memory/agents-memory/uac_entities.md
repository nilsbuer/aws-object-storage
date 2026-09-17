# UAC Entities

**Extension:** aws-object-storage

---

## Agent Selection

### Available Agents

| Agent Name | Host | IP | Type | Status | Queue | Version |
|------------|------|----|------|--------|-------|---------|
| AGT_LX_USERVERSE | EC1A-USERVERSE-POC-1 | 10.6.107.8 | Linux/Unix | Active | AGNT0009 | 8.0.2.1 |

### Selected Agent

| Field      | Value |
|------------|-------|
| Agent Name | AGT_LX_USERVERSE |
| Host Name  | EC1A-USERVERSE-POC-1 |
| IP Address | 10.6.107.8 |
| Type       | Linux/Unix |
| Status     | Active |
| Queue Name | AGNT0009 |
| Version    | 8.0.2.1 |
| SysID      | 8484b67c2d214e5aa3d1d44dd296cd45 |

**Required OS Type:** Linux
**Selection rationale:** Only active agent found on the UAC controller. Supports the aws-object-storage extension (confirmed in extAcceptList).

---

## Required Entities

[Populated by test-graph-builder based on planned test scenarios]

### Credentials

| Credential Name | Type | Field Name | Auth Method | Used In Scenarios |
|----------------|------|------------|-------------|-------------------|
| aws-s3-test-cred | Basic | aws_credentials | AWS Access Key ID / Secret Access Key | Test_AwsObjectStorage_ListObjects_Minimal, Test_AwsObjectStorage_ListObjects_Full, Test_AwsObjectStorage_ListObjects_MaxRecords, Test_AwsObjectStorage_ListObjects_SmallCap, Test_AwsObjectStorage_ListObjects_LargeCap, Test_AwsObjectStorage_UploadFile_Minimal, Test_AwsObjectStorage_UploadFile_Full, Test_AwsObjectStorage_UploadFile_NestedKey, Test_AwsObjectStorage_UploadFile_RootKey |

**Credential Values:**
- **User (Access Key ID):** `test-placeholder-key`
- **Password (Secret Access Key):** `test-placeholder-secret`

> Note: Placeholder values are used. Tests that fail due to invalid credentials are expected and will be logged as known failures.

### Scripts

None required. The extension has no Script-type fields.

---

## Created Entities

[Populated by main thread after creation on UAC]

### Credentials

| Credential Name | SysID | Status |
|----------------|-------|--------|
| | | |

### Scripts

| Script Name | SysID | Status |
|------------|-------|--------|
| | | |
