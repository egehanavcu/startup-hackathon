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

@router.post("/class/join")
def join_class(request: JoinClassRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Öğretmenler öğrenci olarak derse katılamaz")

    class_to_join = db.query(Class).filter(Class.invite_code == request.invite_code).first()
    if not class_to_join:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Girilen davet kodu ile eşleşen sınıf bulunamadı")

    existing_user = db.query(User).filter(User.id == current_user.id).first()
    
    if existing_user in class_to_join.students:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Zaten bu sınıftasınız")

    class_to_join.students.append(existing_user)
    db.commit()

    new_task = StudentTask(
        user_id=current_user.id,
        class_id=class_to_join.id,
        code="",
        code_summary="",
        completion_percentage=0
    )

    db.add(new_task)
    db.commit()
    
    return {"message": "Sınıfa başarıyla katıldın ve görev oluşturuldu"}

@router.get("/class/all/teacher")
def get_classes_as_teacher(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_teacher:
        raise HTTPException(status_code=403, detail="Bu işlemi yapma yetkiniz yok")

    classes = db.query(Class).filter(Class.teacher_id == current_user.id).order_by(Class.id.desc()).all()
    
    result = []
    for cls in classes:
        student_count = len(cls.students)
        result.append({
            "class_id": cls.id,
            "class_name": cls.class_name,
            "university_name": cls.university_name,
            "invite_code": cls.invite_code,
            "student_count": student_count
        })
    
    return result

@router.get("/class/all/student")
def get_classes_as_student(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.is_teacher:
        raise HTTPException(status_code=403, detail="Bu işlemi yapma yetkiniz yok")

    classes = current_user.classes
    result = []
    for cls in classes:
        student_count = len(cls.students)
        teacher_name = f"{cls.teacher.first_name} {cls.teacher.last_name}"

        result.append({
            "class_id": cls.id,
            "class_name": cls.class_name,
            "university_name": cls.university_name,
            "teacher_name": teacher_name,
            "student_count": student_count
        })

    result.sort(key=lambda x: x['class_id'], reverse=True)
    return result