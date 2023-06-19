from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import pandas as pd
from datetime import timedelta


class CreateUpdateInput(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    begining_date: str
    time: str
    finish_date: str
    prediction: str
    prediction_time: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    client_ip: str
    


class InputUser(SQLModel):
    
    begining_date: str
    finish_date: str
    time: str 

    class Config:
        
        schema_extra = {
            "example": {
                "begining_date": "2023-01-07",
                "finish_date": "2023-01-12",
                "time": "05:00:00"
            }
        }
