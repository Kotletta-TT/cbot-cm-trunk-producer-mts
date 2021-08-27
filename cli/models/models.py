from pydantic import BaseModel, validator
from typing import List


class Config(BaseModel):
    address: str
    login: str
    password: str
    inner_id: str


class CliData(BaseModel):
    login: str
    filename: str
    display: bool
    view: List[str]
    nums: List[str]
    filter: str
