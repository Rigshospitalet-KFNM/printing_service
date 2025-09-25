from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    id: int
    printer: str
    user: str
    status: str
    pages: Optional[int] = None

@dataclass
class Printer:
    name: str
    status: str
    enabled: bool = True
    current_job: str | None = None 
    since: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None


