"""
This module defines the data structures for our configuration.
Currently, the dataclasses are defined for potential future integration
with a configuration parsing/validation library.
"""

import pulumi
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AWSResource:
    name: str
    type: str
    args: Dict

@dataclass
class Config:
    team: str
    service: str
    environment: str
    region: str
    tags: Dict[str, str]
    aws_resources: List[AWSResource]
