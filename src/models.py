from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class EmailData:
    """Explicit state management with dataclass"""
    sender: str
    subject: str
    content: str
    timestamp: datetime
    urgency: Optional[str] = None
    query_type: Optional[str] = None
    department: Optional[str] = None
    response: Optional[str] = None
    needs_followup: bool = False