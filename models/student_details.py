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
    page_number: int
    source_pdf_path: str = ""
    card_id: str = ""
    first_name: str = ""
    last_name: str = ""
    college: str = ""
    session: str = ""
    status: RecordStatus = RecordStatus.ERROR
    error_message: str = ""
    scan_failed: bool = False
    scan_error_message: str = ""
    object_id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def source_location(self) -> str:
        return f"{self.source_file} (Page {self.page_number})"

    def validate(self):
        missing_fields: list[str] = []

        if not self.card_id.strip():
            missing_fields.append("Card ID")

        if not self.first_name.strip():
            missing_fields.append("First Name")

        if not self.last_name.strip():
            missing_fields.append("Last Name")

        if not self.college.strip():
            missing_fields.append("College")

        if not self.session.strip():
            missing_fields.append("Session")

        if not missing_fields:
            self.scan_failed = False
            self.status = RecordStatus.SUCCESS
            self.error_message = ""
        elif self.scan_failed:
            self.status = RecordStatus.ERROR
            scan_message = self.scan_error_message or "QR scan failed"
            missing_message = "Missing: " + ", ".join(missing_fields)
            self.error_message = f"Error: {scan_message} " + f"{missing_message}"
        else:
            self.status = RecordStatus.WARNING
            self.error_message = "Missing: " + ", ".join(missing_fields)
