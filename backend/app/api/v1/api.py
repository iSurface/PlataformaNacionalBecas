# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.api.v1.endpoints import auth, catalogs, admin

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(catalogs.router)
api_router.include_router(admin.router)
