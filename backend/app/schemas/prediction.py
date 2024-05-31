from pydantic import BaseModel

class PredictionRequest(BaseModel):
    content: str

class PredictionResponse(BaseModel):
    probability: float
    classification: float
