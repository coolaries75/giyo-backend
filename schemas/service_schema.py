from pydantic import BaseModel

class ServiceResponse(BaseModel):
    id: int
    name: str
    code: str
    status: str
    cta_link: str

