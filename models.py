from dataclasses import dataclass
from typing import List

@dataclass
class BaseHost:
    name: str
    ip_template: str
    in_scope: bool
    services: List[str]

@dataclass
class ExpandedHost:
    name: str
    base_name: str
    ip: str
    team_id: int
    services: List[str]
    in_scope: bool = True
