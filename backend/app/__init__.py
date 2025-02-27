from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化CORS
    CORS(app)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.routes import api_bp
    app.register_blueprint(api_bp)

    return app