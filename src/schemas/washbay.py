import re
import uuid
from pydantic import BaseModel, Field, ConfigDict 
from typing import Optional

from src.models.washbay import WashBay



class SWashBayCreate(BaseModel):
    bay_number: int = Field(...)
    bay_type: str = Field(...)


    model_config = ConfigDict(from_attributes=True)



class SWashBayResponse(BaseModel):
    id: uuid.UUID = Field(...)
    bay_number: int
    bay_type: str

    model_config = ConfigDict(from_attributes=True)