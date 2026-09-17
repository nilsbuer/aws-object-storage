"""
OutputFormatter — produces human-readable STDOUT for the List Objects action.

Uses the tabulate library to render S3 object lists as a three-column ASCII table
and provides helper methods for the summary and truncation notice lines.
"""
import logging

from tabulate import tabulate

logger = logging.getLogger("UNV")


class OutputFormatter:
    """Produces human-readable STDOUT output for the List Objects action."""

    @staticmethod
    def format_table(objects: list[dict]) -> str:
        """
        Render a list of S3 object dicts as a three-column ASCII table.

        Args:
            objects: List of dicts, each containing 'key' (str), 'size' (int),
                     and 'last_modified' (str ISO 8601 UTC).

        Returns:
            Formatted table string using tabulate 'rounded_outline' style with
            headers ['Key', 'Size', 'Last Modified'].
        """
        logger.debug("Formatting table for %d objects", len(objects))
        rows = [
            [obj["key"], obj["size"], obj["last_modified"]]
            for obj in objects
        ]
        return tabulate(rows, headers=["Key", "Size", "Last Modified"], tablefmt="rounded_outline")

    @staticmethod
    def format_summary(total_count: int) -> str:
        """
        Return the summary line reporting the total object count.

        Args:
            total_count: Total number of objects in the bucket.

        Returns:
            String in the form 'Total objects in bucket: {total_count}'.
        """
        return f"Total objects in bucket: {total_count}"

    @staticmethod
    def format_truncation_notice(total_count: int, max_records: int) -> str:
        """
        Return the truncation notice appended to STDOUT when output is capped.

        Should only be called when total_count > max_records.

        Args:
            total_count: Total number of objects in the bucket.
            max_records: The cap applied to the displayed output.

        Returns:
            String in the form:
            'Note: Output truncated to {max_records} records. Total objects in bucket: {total_count}'
        """
        return (
            f"Note: Output truncated to {max_records} records. "
            f"Total objects in bucket: {total_count}"
        )
