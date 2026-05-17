from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Class, User, StudentTask
from app.schemas import TaskUpdate, CodeExecutionRequest
from .auth import get_current_user

router = APIRouter()