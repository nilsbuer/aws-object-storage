"""Actions module — business logic implementations for the AWS Object Storage extension."""

from actions.list_objects import list_objects
from actions.output import ActionOutput
from actions.upload_file import upload_file

# Maps UAC action choice values to their handler functions.
ACTION_MAPPER = {
    "List Objects": list_objects,
    "Upload File": upload_file,
}
