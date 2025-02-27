from flask import Blueprint

api_bp = Blueprint('api', __name__)

# 导入路由处理函数
from app.routes import views