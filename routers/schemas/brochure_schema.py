from pydantic import BaseModel

class BrochureResponse(BaseModel):
    id: int
    title: str
    code: str
    status: str
    cta_link: str
