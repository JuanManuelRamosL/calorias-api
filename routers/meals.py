from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import models
from schemas import meal as meal_schema

router = APIRouter(prefix="/meals", tags=["meals"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_meal(meal: meal_schema.MealCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == meal.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_meal = models.Meal(name=meal.name, user_id=meal.user_id)
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@router.get("/user/{user_id}")
def get_meals_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Meal).filter(models.Meal.user_id == user_id).all()
