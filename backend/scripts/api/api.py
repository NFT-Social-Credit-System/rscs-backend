from fastapi import APIRouter, HTTPException
from ..scripts.Scrape.user import get_user_information
from ..database import get_database

router = APIRouter()

@router.post("/scrape-user/{username}")
async def scrape_user(username: str):
    db = get_database()
    try:
        user_info = get_user_information([username])
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_info[username]
        db.users.update_one(
            {"username": username},
            {"$set": user_data},
            upsert=True
        )
        return {"message": "User scraped and saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
