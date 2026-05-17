import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Class, User, StudentTask
from app.schemas import ClassBase, JoinClassRequest
from app.routers.auth import get_current_user

router = APIRouter()

def generate_invite_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

@router.post("/class/create")
def create_class(class_data: ClassBase, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not current_user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece öğretmenler sınıf oluşturabilir")
    
    invite_code = generate_invite_code()

    new_class = Class(
        teacher_id=current_user.id,
        class_name=class_data.class_name,
        university_name=class_data.university_name,
        invite_code=invite_code
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return {"message": "Sınıf başarıyla oluşturuldu", "class_id": new_class.id, "invite_code": invite_code}
