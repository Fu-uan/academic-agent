"""Vercel 入口：暴露 FastAPI 应用给 Serverless 运行时"""
from app import app

# Vercel Python Runtime 需要 ASGI 应用命名为 app
# （app 已从 app.py 导入）
