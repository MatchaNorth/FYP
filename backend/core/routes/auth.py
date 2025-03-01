from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from core.models.user import User
from app import db
from core.routes import api_bp

@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'code': 400,
            'message': '用户名和密码不能为空'
        }), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'code': 400,
            'message': '用户名已存在'
        }), 400

    # 创建新用户
    hashed_password = generate_password_hash(data['password'], method='scrypt')
    new_user = User(
        username=data['username'],
        nickname=data.get('nickname'),
        password=hashed_password
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': new_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f'Registration error: {str(e)}')
        return jsonify({
            'code': 500,
            'message': '注册失败，请稍后重试'
        }), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    # 验证请求数据
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'code': 400,
            'message': '用户名和密码不能为空'
        }), 400

    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证用户名和密码
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({
            'code': 401,
            'message': '用户名或密码错误'
        }), 401

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': user.to_dict()
    })