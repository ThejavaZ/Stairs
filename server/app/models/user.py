from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    password: str
    status: bool = True
    timestamp: datetime = datetime.now()
    
    def __str__(self):
        return self.email