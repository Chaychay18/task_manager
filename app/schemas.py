from pydantic import BaseModel

class TaskResponse(BaseModel):
    id: str
    name: str
    description: str
    result: str

    class Config:
        orm_mode = True
