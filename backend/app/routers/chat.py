from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.schemas import ChatBot
from app.routers.auth import get_current_user

router = APIRouter()