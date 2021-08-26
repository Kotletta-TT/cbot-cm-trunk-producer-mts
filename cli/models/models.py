from pydantic import BaseModel


class Config(BaseModel):
    address: str
    login: str
    password: str
    inner_id: str
