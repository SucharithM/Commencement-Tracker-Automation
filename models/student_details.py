from dataclasses import dataclass, field
from enum import Enum
from configs import constants
from uuid import uuid4


class RecordStatus(Enum):
    SUCCESS = constants.SUCCESS
    WARNING = constants.WARNING
    ERROR = constants.ERROR


@dataclass
class StudentRecord:
    source_file: str
    page_number: str
    student_id: str = ""
    first_name: str = ""
    last_name: str = ""
    status: RecordStatus = RecordStatus.ERROR
    error_message: str = ""
    object_id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def source_location(self) -> str:
        return f"{self.source_file} (Page {self.page_number})"

    def validate(self):
        missing_fields: list[str] = []

        if not self.student_id.strip():
            missing_fields.append("Student ID")

        if not self.first_name.strip():
            missing_fields.append("First Name")

        if not self.last_name.strip():
            missing_fields.append("Last Name")

        if not missing_fields:
            self.status = RecordStatus.SUCCESS
            self.error_message = ""
        else:
            self.status = RecordStatus.WARNING
            self.error_message = "Missing: " + ", ".join(missing_fields)
