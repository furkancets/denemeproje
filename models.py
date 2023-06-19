from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, Field
from datetime import timedelta

#def adding_neccesarry_time():
#    pass
#
#def str_converter_to_datetime(x):
#    y = datetime.strptime(x,"%Y-%m-%d").date()
#    return y


class CreateUpdateInput(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    begining_date: datetime
    time: datetime
    finish_date: datetime
    prediction: str
    prediction_time: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    #client_ip: str
    


class InputUser(BaseModel):
    
    begining_date: str
    time: str 

    class Config:
        
        schema_extra = {
            "example": {
                "begining_date": "2023-01-07",
                "time": "05:00"
            }
        }
        
        
        def to_create_update_input(self) -> CreateUpdateInput:
            
            beginning_date = datetime.strptime(self.beginning_date, "%Y-%m-%d").date()
            time = datetime.strptime(self.time, "%H:%M").time()
            finish_date = beginning_date + timedelta(days=5)
            prediction = ""
            prediction_time = ""

            
            return CreateUpdateInput(begining_date=beginning_date, time=time, finish_date=finish_date, prediction=prediction,prediction_time=prediction_time )