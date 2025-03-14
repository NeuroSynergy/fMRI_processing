from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ConversionEntry:
    subject_id: str
    bids_id: str
    session_label: str
    dicom_path: str
    scan_folder: str
    bids_folder: str
    task_type: Optional[str] = None
    run_label: Optional[str] = None
    scan_datetime: Optional[datetime] = None
    nii_path: Optional[str] = None
    json_path: Optional[str] = None
    