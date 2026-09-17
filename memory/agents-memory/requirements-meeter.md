# Requirements Meeter Output

## Zipsafe Decision
- **Result**: false
- **Reason**: Packages with data files — botocore (boto3 dependency) ships JSON service model data files (endpoints.json, cacert.pem, partitions.json, etc.) that must be extractable at runtime

## CLI Tools
- None required

## Python Dependencies
- boto3==1.43.96 — Has data files (botocore dependency contains JSON service definitions and PEM certificates)
- tabulate==0.10.0 — Pure Python (no data files)

## Setup.py Changes
- VENDOR_FOLDER added: no
- data_files updated: no
