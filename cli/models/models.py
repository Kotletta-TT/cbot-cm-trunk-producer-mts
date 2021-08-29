from typing import List

from pydantic import BaseModel, validator


class Config(BaseModel):
    address: str
    login: str
    password: str
    inner_id: str


class Trunk(BaseModel):
    phone: str
    login: str
    password: str
    sip_device: str
    sip_enabled: str
    identify_line: str


class CliData(BaseModel):
    login: str
    filename: str = None
    display: bool
    action: str = None
    view: List[str]
    nums: List[str] = None
    filter: str

    @validator('login')
    def valid_login(cls, login: str) -> str:
        if '+7-' != login[:3] or len(login) != 13:
            raise ValueError(f'Login: {login} incorrect, login must start '
                             f'+7- and length 13 digits')
        return login

    @validator('nums')
    def valid_nums(cls, nums: List[str]) -> List[str]:
        for num in nums:
            if '7' != num[1] or len(num) != 11:
                raise ValueError(f'Number: {num} incorrect, number must '
                                 f'start 7 and length 11 digits')
        return nums
