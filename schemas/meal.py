from pydantic import BaseModel

class MealCreate(BaseModel):
    name: str
    user_id: int

class MealResponse(MealCreate):
    id: int

    class Config:
        orm_mode = True
