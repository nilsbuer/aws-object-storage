"""ActionOutput dataclass for action return values."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from utility import OutputFormatter

logger = logging.getLogger("UNV")


@dataclass
class ActionOutput:
    """Output from action functions for the AWS Object Storage extension.

    List Objects fields:
        object_count: Total number of objects found in the bucket.
        objects: List of object dicts (key, size, last_modified), truncated to max_records.
        truncated: True when total_count exceeds max_records.

    Upload File fields:
        s3_uri: Full S3 URI of the successfully uploaded object.
        etag: ETag of the uploaded object as returned by AWS.
        local_file: Absolute path of the local file that was uploaded (used for STDOUT).

    Control fields (no template control fields; always empty = print/include everything):
        stdout_options: Always empty — all output is printed.
        output_options: Always empty — all data is included in Extension Output.
    """

    # List Objects result fields
    object_count: Optional[int] = None
    objects: Optional[List[Dict[str, Any]]] = None
    truncated: Optional[bool] = None

    # Upload File result fields
    s3_uri: Optional[str] = None
    etag: Optional[str] = None
    local_file: Optional[str] = None

    # Control fields (no control fields in this template; empty = include all)
    stdout_options: List[str] = None
    output_options: List[str] = None

    def __post_init__(self) -> None:
        """Initialize control fields with defaults."""
        if self.stdout_options is None:
            self.stdout_options = []
        if self.output_options is None:
            self.output_options = []

    def print_output(self) -> None:
        """Print to STDOUT based on action result.

        List Objects: prints the formatted object table, summary line, and
        optional truncation notice when the result was capped.

        Upload File: prints a single confirmation line with the local file path
        and the destination S3 URI.
        """
        if self.objects is not None:
            # List Objects action output
            logger.debug("Printing List Objects output (%d display objects)", len(self.objects))
            table = OutputFormatter.format_table(self.objects)
            print(table)
            print(OutputFormatter.format_summary(self.object_count))
            if self.truncated:
                print(
                    OutputFormatter.format_truncation_notice(
                        total_count=self.object_count,
                        max_records=len(self.objects),
                    )
                )
        elif self.s3_uri is not None:
            # Upload File action output
            logger.debug("Printing Upload File output: %s", self.s3_uri)
            print(f"Successfully uploaded {self.local_file} → {self.s3_uri}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for Extension Output (unv_output).

        No template control fields exist, so all populated fields are always
        included in the Extension Output.

        Returns:
            Dict containing all non-None result fields.
        """
        output: Dict[str, Any] = {}

        # List Objects fields
        if self.object_count is not None:
            output["object_count"] = self.object_count
        if self.objects is not None:
            output["objects"] = self.objects
        if self.truncated is not None:
            output["truncated"] = self.truncated

        # Upload File fields
        if self.s3_uri is not None:
            output["s3_uri"] = self.s3_uri
        if self.etag is not None:
            output["etag"] = self.etag

        return output
