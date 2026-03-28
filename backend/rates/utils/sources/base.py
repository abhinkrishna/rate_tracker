from dataclasses import dataclass
from typing import Literal


@dataclass
class Source:
    name: str
    type: Literal["parquet", "api", "scrap", "socket"]
    creds: dict  # API key or JWT token
    source: str  # File path or API endpoint
