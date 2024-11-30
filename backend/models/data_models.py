from pydantic import BaseModel
from typing import Optional 
class createDb(BaseModel):
    name:str

class addRepo(BaseModel):
    id: int
    name: str
    full_name: str
    is_active: str
    backend_path: Optional[str] = ""

class getDataRequest(BaseModel):
    dbName: str
    id: str

class getDataResponse(BaseModel):
    id: str
    name: str
    full_name: str
    is_active: str
    backend_path: str

class RemoveRepo(BaseModel):
    id: str

class ReadDocsRequest(BaseModel):
    full_name: str
    access_token: str