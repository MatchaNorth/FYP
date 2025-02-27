from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt
from datetime import datetime, timedelta

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 配置
app.config.update(
    JWT_SECRET_KEY='fyp_2024_secure_jwt_key_!@#$%^&*()',
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=1),
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:5kuo4678K@localhost/fyp_db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(80))
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, password, nickname=None):
        self.username = username
        self.password = password
        self.nickname = nickname

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'created_at': self.created_at.isoformat()
        }

# 路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400

        # 密码加密
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # 创建新用户
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': '注册成功'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"注册错误: {str(e)}")
        return jsonify({'message': '注册失败', 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400

        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message': '用户名或密码错误'}), 401

        # 验证密码
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=username)
            return jsonify({
                'message': '登录成功',
                'token': access_token,
                'username': username
            }), 200
        
        return jsonify({'message': '用户名或密码错误'}), 401

    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({'message': '登录失败', 'error': str(e)}), 500

# 初始化数据库
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 