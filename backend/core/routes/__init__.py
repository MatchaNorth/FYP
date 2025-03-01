from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入路由处理函数
from core.routes import views, auth