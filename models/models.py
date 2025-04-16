from pydantic import BaseModel
from typing import Literal, List, Optional
from pydantic import BaseModel, Field

# -------------------------------
# Pydantic Output Schema
# -------------------------------
class TrainInfo(BaseModel):
    train_number: str
    train_name: str
    departure: str
    arrival: str
    duration: str
    availability: str
    fare: Optional[int] = 0

class TrainAvailability(BaseModel):
    source: str
    destination: str
    date: str
    class_type: str = Field(..., alias="class")
    trains: List[TrainInfo]

class FlightQueryRequest(BaseModel):
    source: str
    destination: str
    date: str  # Format: YYYY-MM-DD
    cabin_class: Literal["economy", "business", "first"] = "economy"

from pydantic import BaseModel
from typing import List

class FlightInfo(BaseModel):
    flight_number: str
    departure: str
    arrival: str
    duration: str
    availability: str
    fare: int

class FlightAvailability(BaseModel):
    source: str
    destination: str
    date: str
    cabin_class: str
    flights: List[FlightInfo]