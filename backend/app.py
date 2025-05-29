from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import bcrypt
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse, parse_qs
import pytz
import requests
from bs4 import BeautifulSoup
import os
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from routes.proxy import proxy_bp

# 创建Flask应用
app = Flask(__name__)

# 配置CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }
})

# 设置中国时区
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')

def get_cn_datetime():
    return datetime.now(CN_TIMEZONE)

# 配置
app.config.update(
    JWT_SECRET_KEY='fyp_2024_secure_jwt_key_!@#$%^&*()',
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=1),
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:5kuo4678K@localhost/fyp_db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER='uploads/avatars'
)

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# 用户活动模型
class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 活动类型：登录、注册、修改密码等
    description = db.Column(db.String(255), nullable=False)   # 活动描述
    created_at = db.Column(db.DateTime, default=get_cn_datetime())
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(80))
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # 添加role字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # 小黑盒相关字段
    heybox_id = db.Column(db.String(20))  # 小黑盒ID
    heybox_nickname = db.Column(db.String(80))  # 小黑盒昵称
    heybox_avatar = db.Column(db.String(255))  # 小黑盒头像URL
    heybox_profile = db.Column(db.String(255))  # 小黑盒个人主页URL
    articles = db.relationship('Article', backref='author', lazy=True)
    avatar = db.Column(db.String(255))  # 用户头像URL
    is_banned = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, nickname=None):
        self.username = username
        self.password = password
        self.nickname = nickname

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'role': self.role,  # 添加role到返回数据中
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'days_since_registration': (datetime.utcnow() - self.created_at).days,
            'heybox_id': self.heybox_id,
            'heybox_nickname': self.heybox_nickname,
            'heybox_avatar': self.heybox_avatar,
            'heybox_profile': self.heybox_profile,
            'avatar': self.avatar,
            'is_banned': self.is_banned
        }

# 用户点赞记录模型
class ArticleLike(db.Model):
    __tablename__ = 'article_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 添加唯一约束，确保用户不能重复点赞同一篇文章
    __table_args__ = (db.UniqueConstraint('user_id', 'article_id', name='unique_user_article_like'),)

# 文章浏览记录模型
class ArticleView(db.Model):
    __tablename__ = 'article_views'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)  # 访问者IP
    user_agent = db.Column(db.String(200))  # 浏览器标识
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 添加索引以加快查询速度
    __table_args__ = (
        db.Index('idx_article_view_ip_time', 'article_id', 'ip_address', 'created_at'),
    )

# 文章模型
class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(200))
    status = db.Column(db.String(20), default='draft')  # draft or published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    is_hidden = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        author = User.query.get(self.author_id)
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author_id': self.author_id,
            'author': author.username,
            'author_nickname': author.nickname,
            'author_avatar': author.avatar,
            'views': self.views,
            'likes': self.likes,
            'is_hidden': self.is_hidden,
            'is_pinned': self.is_pinned
        }

# 评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    floor = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=get_cn_datetime)
    updated_at = db.Column(db.DateTime, default=get_cn_datetime, onupdate=get_cn_datetime)

    def to_dict(self):
        user = User.query.get(self.user_id)
        return {
            'id': self.id,
            'content': self.content,
            'user_id': self.user_id,
            'nickname': user.nickname if user else '',
            'avatar': user.avatar if user else '',
            'article_id': self.article_id,
            'parent_id': self.parent_id,
            'floor': self.floor,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'updated_at': self.updated_at.isoformat() if self.updated_at else ''
        }

# 评论点赞记录模型
class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 路由
@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user.to_dict()
        })
    except Exception as e:
        print(f"获取用户信息错误: {str(e)}")
        return jsonify({'message': '获取用户信息失败'}), 500

@app.route('/api/user/activities', methods=['GET'])
@jwt_required()
def get_user_activities():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        # 获取用户最近的20条活动记录
        activities = UserActivity.query.filter_by(user_id=user.id)\
            .order_by(UserActivity.created_at.desc())\
            .limit(20)\
            .all()
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [activity.to_dict() for activity in activities]
        })
    except Exception as e:
        print(f"获取用户活动记录错误: {str(e)}")
        return jsonify({'message': '获取用户活动记录失败'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')

        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空'}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400

        # 密码加密
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # 创建新用户
        new_user = User(
            username=username,
            password=hashed_password.decode('utf-8'),
            nickname=nickname
        )
        db.session.add(new_user)
        db.session.commit()
        
        # 记录注册活动
        activity = UserActivity(
            user_id=new_user.id,
            activity_type='register',
            description='注册成功'
        )
        db.session.add(activity)
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
            # 更新最后登录时间
            user.last_login = get_cn_datetime()
            
            # 记录登录活动
            activity = UserActivity(
                user_id=user.id,
                activity_type='login',
                description='登录系统',
                created_at=get_cn_datetime()
            )
            db.session.add(activity)
            db.session.commit()
            
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

@app.route('/api/user/bind-heybox', methods=['POST'])
@jwt_required()
def bind_heybox():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        data = request.get_json()
        profile_url = data.get('profile_url')
        
        if not profile_url:
            return jsonify({'message': '请提供小黑盒个人主页链接'}), 400
            
        # 解析小黑盒链接
        heybox_id = None
        if 'xiaoheihe.cn/app/user/profile/' in profile_url:
            heybox_id = profile_url.split('profile/')[-1]
        elif 'web.xiaoheihe.cn/bbs/user_profile_share' in profile_url:
            parsed_url = urlparse(profile_url)
            query_params = parse_qs(parsed_url.query)
            heybox_id = query_params.get('user_id', [None])[0]
            
        if not heybox_id:
            return jsonify({'message': '无效的小黑盒个人主页链接'}), 400
            
        # 获取小黑盒用户信息
        try:
            # 使用小黑盒的API获取用户信息
            api_url = f'https://api.xiaoheihe.cn/bbs/app/profile/user/info?userid={heybox_id}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.xiaoheihe.cn'
            }
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # 如果请求失败会抛出异常
            
            data = response.json()
            if data.get('status') == 'ok':
                user_info = data.get('result', {})
                heybox_nickname = user_info.get('username', f'黑盒玩家{heybox_id}')
                heybox_avatar = user_info.get('avatar', f'https://api.xiaoheihe.cn/account/avatar/{heybox_id}')
            else:
                raise Exception('API返回数据格式错误')
                
        except Exception as e:
            print(f"获取小黑盒用户信息失败: {str(e)}")
            # 尝试使用备用API
            try:
                api_url = f'https://api.xiaoheihe.cn/account/basic_info/{heybox_id}'
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'ok':
                    user_info = data.get('result', {})
                    heybox_nickname = user_info.get('nickname', f'黑盒玩家{heybox_id}')
                    heybox_avatar = user_info.get('avatar', f'https://api.xiaoheihe.cn/account/avatar/{heybox_id}')
                else:
                    raise Exception('备用API返回数据格式错误')
            except Exception as e2:
                print(f"备用API也失败: {str(e2)}")
                heybox_nickname = f'黑盒玩家{heybox_id}'
                heybox_avatar = f'https://api.xiaoheihe.cn/account/avatar/{heybox_id}'
            
        print(f"获取到的昵称: {heybox_nickname}")
        print(f"获取到的头像: {heybox_avatar}")
            
        # 设置小黑盒信息
        user.heybox_id = heybox_id
        user.heybox_profile = profile_url
        user.heybox_avatar = heybox_avatar
        user.nickname = heybox_nickname
        user.heybox_nickname = heybox_nickname
        
        # 记录绑定活动
        activity = UserActivity(
            user_id=user.id,
            activity_type='profile',
            description='绑定小黑盒账号',
            created_at=get_cn_datetime()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '绑定成功',
            'data': user.to_dict()
        })
        
    except Exception as e:
        print(f"绑定小黑盒账号错误: {str(e)}")
        return jsonify({'message': '绑定失败'}), 500

@app.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        data = request.get_json()
        nickname = data.get('nickname')
        
        if nickname:
            user.nickname = nickname
            
            # 记录修改资料活动
            activity = UserActivity(
                user_id=user.id,
                activity_type='profile',
                description='修改个人资料',
                created_at=get_cn_datetime()
            )
            db.session.add(activity)
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user.to_dict()
        })
        
    except Exception as e:
        print(f"更新用户资料错误: {str(e)}")
        return jsonify({'message': '更新失败'}), 500

@app.route('/api/user/activities/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def delete_user_activity(activity_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        activity = UserActivity.query.filter_by(id=activity_id, user_id=user.id).first()
        
        if not activity:
            return jsonify({'message': '活动记录不存在'}), 404
            
        # 检查是否为不可删除的活动类型
        if activity.activity_type in ['register', 'login']:
            return jsonify({'message': '该活动记录不可删除'}), 403
            
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
        
    except Exception as e:
        print(f"删除活动记录错误: {str(e)}")
        return jsonify({'message': '删除失败'}), 500

@app.route('/api/user/unbind-heybox', methods=['POST'])
@jwt_required()
def unbind_heybox():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        # 清除小黑盒相关信息
        user.heybox_id = None
        user.heybox_nickname = None
        user.heybox_avatar = None
        user.heybox_profile = None
        
        # 记录解绑活动
        activity = UserActivity(
            user_id=user.id,
            activity_type='profile',
            description='解绑小黑盒账号',
            created_at=get_cn_datetime()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '解绑成功',
            'data': user.to_dict()
        })
        
    except Exception as e:
        print(f"解绑小黑盒账号错误: {str(e)}")
        return jsonify({'message': '解绑失败'}), 500

@app.route('/api/articles', methods=['GET'])
@jwt_required()
def get_articles():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        articles = Article.query.filter_by(author_id=user.id)\
            .order_by(Article.updated_at.desc())\
            .all()
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [article.to_dict() for article in articles]
        })
        
    except Exception as e:
        print(f"获取文章列表错误: {str(e)}")
        return jsonify({'message': '获取文章列表失败'}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    try:
        article = Article.query.get_or_404(article_id)
        
        # 增加浏览量
        article.views = (article.views or 0) + 1
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '获取文章详情成功',
            'data': article.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/articles', methods=['POST'])
@jwt_required()
def create_article():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        status = data.get('status', 'draft')
        
        if not title or not content:
            return jsonify({'message': '标题和内容不能为空'}), 400
            
        # 创建新文章
        article = Article(
            title=title,
            content=content,
            author_id=user.id,
            status=status
        )
        
        # 生成摘要（取前100个字符）
        article.summary = content[:100] if len(content) > 100 else content
        
        # 将Markdown转换为HTML
        import markdown2
        article.content_html = markdown2.markdown(content)
        
        db.session.add(article)
        
        # 记录活动
        activity = UserActivity(
            user_id=user.id,
            activity_type='article',
            description=f'{"发布" if status == "published" else "保存"}文章《{title}》',
            created_at=get_cn_datetime()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': article.to_dict()
        })
        
    except Exception as e:
        print(f"创建文章错误: {str(e)}")
        return jsonify({'message': '创建文章失败'}), 500

@app.route('/api/articles/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_article(article_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        article = Article.query.filter_by(id=article_id, author_id=user.id).first()
        
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        status = data.get('status')
        
        old_status = article.status
        
        if title:
            article.title = title
        if content:
            article.content = content
            article.summary = content[:100] if len(content) > 100 else content
            import markdown2
            article.content_html = markdown2.markdown(content)
        if status:
            article.status = status
            
        # 记录活动（仅在状态改变时）
        if status and status != old_status:
            activity = UserActivity(
                user_id=user.id,
                activity_type='article',
                description=f'{"发布" if status == "published" else "保存"}文章《{article.title}》',
                created_at=get_cn_datetime()
            )
            db.session.add(activity)
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': article.to_dict()
        })
        
    except Exception as e:
        print(f"更新文章错误: {str(e)}")
        return jsonify({'message': '更新文章失败'}), 500

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    try:
        current_user_id = get_jwt_identity()
        article = Article.query.get_or_404(article_id)
        # 检查是否为作者
        if article.author_id != current_user_id:
            return jsonify({
                'code': 403,
                'message': '没有权限删除该文章'
            }), 403
        
        # 删除相关的点赞记录
        ArticleLike.query.filter_by(article_id=article_id).delete()
        
        # 删除文章
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除文章成功'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/user/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有文件'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '没有选择文件'}), 400
        
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加时间戳避免文件名重复
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{get_jwt_identity()}_{timestamp}.{ext}"
        
        # 保存文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        # 生成访问URL（修改为完整的URL）
        avatar_url = f"http://localhost:5000/uploads/avatars/{new_filename}"
        
        # 更新数据库
        try:
            user = User.query.filter_by(username=get_jwt_identity()).first()
            if user:
                # 删除旧头像
                if user.avatar and os.path.exists(os.path.join(os.getcwd(), 'uploads/avatars', os.path.basename(user.avatar))):
                    os.remove(os.path.join(os.getcwd(), 'uploads/avatars', os.path.basename(user.avatar)))
                
                user.avatar = avatar_url
                db.session.commit()
                
                return jsonify({
                    'code': 200,
                    'message': '上传成功',
                    'data': {
                        'avatar_url': avatar_url
                    }
                })
        except Exception as e:
            db.session.rollback()
            # 删除已上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'code': 500, 'message': '服务器错误'}), 500
            
    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400

# 添加静态文件路由
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/api/articles/stats', methods=['GET'])
@jwt_required()
def get_article_stats():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        # 获取文章统计信息
        total_articles = Article.query.filter_by(author_id=user.id).count()
        published_articles = Article.query.filter_by(author_id=user.id, status='published').count()
        draft_articles = Article.query.filter_by(author_id=user.id, status='draft').count()
        
        # 获取总阅读量
        articles = Article.query.filter_by(author_id=user.id).all()
        total_views = sum(article.views or 0 for article in articles)
        
        # 获取今日阅读量
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_views = ArticleView.query.join(Article).filter(
            Article.author_id == user.id,
            ArticleView.created_at >= today_start
        ).count()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': total_articles,
                'published': published_articles,
                'draft': draft_articles,
                'views': total_views,
                'todayViews': today_views
            }
        })
        
    except Exception as e:
        print(f"获取文章统计信息错误: {str(e)}")
        return jsonify({'message': '获取文章统计信息失败'}), 500

@app.route('/api/articles/public', methods=['GET'])
def get_public_articles():
    try:
        # 获取所有已发布的文章
        articles = Article.query.filter_by(status='published')\
            .order_by(Article.created_at.desc())\
            .all()
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [article.to_dict() for article in articles]
        })
        
    except Exception as e:
        print(f"获取公开文章列表错误: {str(e)}")
        return jsonify({'message': '获取文章列表失败'}), 500

@app.route('/api/articles/public/<int:article_id>', methods=['GET'])
def get_public_article(article_id):
    try:
        article = Article.query.get(article_id)
        
        if not article:
            return jsonify({
                'code': 404,
                'message': '文章不存在'
            }), 404
            
        # 只允许获取已发布的文章
        if article.status != 'published':
            return jsonify({
                'code': 404,
                'message': '文章不存在或未发布'
            }), 404
        
        # 记录浏览量
        try:
            # 获取访问者信息
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            # 检查是否在短时间内重复访问（1小时内同一IP只记录一次浏览）
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_view = ArticleView.query.filter(
                ArticleView.article_id == article_id,
                ArticleView.ip_address == ip_address,
                ArticleView.created_at > one_hour_ago
            ).first()
            
            if not recent_view:
                # 记录新的浏览
                view = ArticleView(
                    article_id=article_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                db.session.add(view)
                
                # 更新文章浏览量
                article.views += 1
                db.session.commit()
        except Exception as e:
            print(f"记录浏览量失败: {str(e)}")
            # 继续处理，不影响文章获取
            pass
        
        return jsonify({
            'code': 200,
            'message': '获取文章详情成功',
            'data': article.to_dict()
        })
    except Exception as e:
        print(f"获取公开文章详情错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/articles/<int:article_id>/view', methods=['POST'])
def increment_article_views(article_id):
    try:
        article = Article.query.get(article_id)
        
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        # 获取访问者信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        # 检查是否在短时间内重复访问（1小时内同一IP只记录一次浏览）
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_view = ArticleView.query.filter(
            ArticleView.article_id == article_id,
            ArticleView.ip_address == ip_address,
            ArticleView.created_at > one_hour_ago
        ).first()
        
        if not recent_view:
            # 记录新的浏览
            view = ArticleView(
                article_id=article_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(view)
            
            # 更新文章浏览量
            article.views += 1
            db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '浏览量更新成功',
            'data': {
                'views': article.views
            }
        })
        
    except Exception as e:
        print(f"更新文章浏览量错误: {str(e)}")
        return jsonify({'message': '更新浏览量失败'}), 500

@app.route('/api/articles/<int:article_id>/like', methods=['POST'])
@jwt_required()
def toggle_article_like(article_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        article = Article.query.get(article_id)
        
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        # 检查是否已经点赞
        existing_like = ArticleLike.query.filter_by(
            user_id=user.id,
            article_id=article_id
        ).first()
        
        if existing_like:
            # 如果已经点赞，则取消点赞
            db.session.delete(existing_like)
            article.likes = (article.likes or 1) - 1
            message = '取消点赞成功'
            is_liked = False
        else:
            # 如果未点赞，则添加点赞
            like = ArticleLike(user_id=user.id, article_id=article_id)
            db.session.add(like)
            article.likes = (article.likes or 0) + 1
            message = '点赞成功'
            is_liked = True
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': message,
            'data': {
                'likes': article.likes,
                'liked': is_liked
            }
        })
        
    except Exception as e:
        print(f"文章点赞错误: {str(e)}")
        db.session.rollback()
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    try:
        user = User.query.get_or_404(user_id)
        articles = Article.query.filter_by(author_id=user_id).all()
        
        total_views = sum(article.views or 0 for article in articles)
        total_likes = sum(article.likes or 0 for article in articles)
        
        return jsonify({
            'code': 200,
            'message': '获取作者统计信息成功',
            'data': {
                'articles': len(articles),
                'total_views': total_views,
                'total_likes': total_likes
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/articles/<int:article_id>/like', methods=['GET'])
@jwt_required()
def get_like_status(article_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        like = ArticleLike.query.filter_by(
            user_id=user.id,
            article_id=article_id
        ).first()
        
        return jsonify({
            'code': 200,
            'message': '获取点赞状态成功',
            'data': {
                'liked': like is not None
            }
        })
    except Exception as e:
        print(f"获取点赞状态错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/articles/analytics', methods=['GET'])
@jwt_required()
def get_article_analytics():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        # 获取过去30天的数据
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 获取每日阅读量统计
        daily_views = db.session.query(
            func.date(ArticleView.created_at).label('date'),
            func.count(ArticleView.id).label('views')
        ).join(Article).filter(
            Article.author_id == user.id,
            ArticleView.created_at >= thirty_days_ago
        ).group_by(
            func.date(ArticleView.created_at)
        ).all()
        
        # 获取每日点赞数统计
        daily_likes = db.session.query(
            func.date(ArticleLike.created_at).label('date'),
            func.count(ArticleLike.id).label('likes')
        ).join(Article).filter(
            Article.author_id == user.id,
            ArticleLike.created_at >= thirty_days_ago
        ).group_by(
            func.date(ArticleLike.created_at)
        ).all()
        
        # 获取文章分类统计（按状态分类）
        article_status = db.session.query(
            Article.status,
            func.count(Article.id).label('count')
        ).filter(
            Article.author_id == user.id
        ).group_by(Article.status).all()
        
        # 获取最受欢迎的文章（按阅读量排序）
        popular_articles = Article.query.filter_by(
            author_id=user.id
        ).order_by(
            Article.views.desc()
        ).limit(5).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'daily_views': [{'date': str(dv.date), 'views': dv.views} for dv in daily_views],
                'daily_likes': [{'date': str(dl.date), 'likes': dl.likes} for dl in daily_likes],
                'article_status': [{'status': status, 'count': count} for status, count in article_status],
                'popular_articles': [
                    {
                        'title': article.title,
                        'views': article.views,
                        'likes': article.likes,
                        'created_at': article.created_at.strftime('%Y-%m-%d')
                    } for article in popular_articles
                ]
            }
        })
        
    except Exception as e:
        print(f"获取文章统计分析错误: {str(e)}")
        return jsonify({'message': '获取统计分析失败'}), 500

@app.route('/api/users/<int:user_id>/profile', methods=['GET'])
def get_user_public_profile(user_id):
    try:
        user = User.query.get_or_404(user_id)
        stats = get_user_stats(user_id).get_json()['data']
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'id': user.id,
                'nickname': user.nickname or user.username,
                'avatar': user.avatar or user.heybox_avatar,
                'bio': '',  # 待添加字段
                'isOnline': False,  # 待实现在线状态
                'articleCount': stats['articles'],
                'totalViews': stats['total_views'],
                'likeCount': stats['total_likes'],
                'joinDate': user.created_at.isoformat(),
                'level': 1,  # 待实现等级系统
                'achievementPoints': 0,  # 待实现成就系统
                'badges': [],  # 待实现徽章系统
                'gameTags': [],  # 待实现游戏标签系统
                'recentArticles': [article.to_dict() for article in 
                    Article.query.filter_by(author_id=user_id, status='published')
                    .order_by(Article.created_at.desc()).limit(6).all()
                ],
                'activityData': []  # 待实现活跃度数据
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/users/<int:user_id>/activity', methods=['GET'])
def get_user_activity_data(user_id):
    try:
        # 获取过去一年的文章发布记录
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        articles = Article.query.filter(
            Article.author_id == user_id,
            Article.status == 'published',
            Article.created_at >= one_year_ago
        ).all()
        
        # 按日期统计活动
        activity_data = {}
        for article in articles:
            date_str = article.created_at.strftime('%Y-%m-%d')
            activity_data[date_str] = activity_data.get(date_str, 0) + 1
        
        # 转换为前端需要的格式 [日期, 活动次数]
        formatted_data = [[date_str, count] for date_str, count in activity_data.items()]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': formatted_data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@app.route('/api/articles/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    try:
        print("开始获取推荐文章...")
        current_user = get_jwt_identity()
        print(f"当前用户: {current_user}")
        
        user = User.query.filter_by(username=current_user).first()
        if not user:
            print(f"用户不存在: {current_user}")
            return jsonify({'message': '用户不存在'}), 404
            
        print(f"找到用户: {user.username}, ID: {user.id}")
            
        # 获取用户最近30天的活动数据
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        print(f"查询时间范围: {thirty_days_ago} 至今")
        
        try:
            # 1. 获取用户浏览记录
            viewed_articles = ArticleView.query.filter(
                ArticleView.ip_address == request.remote_addr,  # 使用IP地址而不是user_id
                ArticleView.created_at >= thirty_days_ago
            ).all()
            print(f"找到 {len(viewed_articles)} 条浏览记录")
        except Exception as e:
            print(f"获取浏览记录时出错: {str(e)}")
            viewed_articles = []
        
        try:
            # 2. 获取用户点赞记录
            liked_articles = ArticleLike.query.filter(
                ArticleLike.user_id == user.id,  # 使用正确的user_id
                ArticleLike.created_at >= thirty_days_ago
            ).all()
            print(f"找到 {len(liked_articles)} 条点赞记录")
        except Exception as e:
            print(f"获取点赞记录时出错: {str(e)}")
            liked_articles = []
        
        try:
            # 3. 获取用户发布的文章
            user_articles = Article.query.filter(
                Article.author_id == user.id,
                Article.created_at >= thirty_days_ago
            ).all()
            print(f"找到 {len(user_articles)} 篇用户文章")
        except Exception as e:
            print(f"获取用户文章时出错: {str(e)}")
            user_articles = []
        
        try:
            # 4. 获取所有可推荐的文章（排除用户自己的文章）
            all_articles = Article.query.filter(
                Article.status == 'published',
                Article.author_id != user.id
            ).order_by(Article.created_at.desc()).all()  # 添加时间排序
            print(f"找到 {len(all_articles)} 篇可推荐文章")
        except Exception as e:
            print(f"获取可推荐文章时出错: {str(e)}")
            all_articles = []
        
        # 计算每篇文章的推荐权重
        recommendations = []
        print("开始计算推荐权重...")
        
        for article in all_articles:
            try:
                weight = 0
                reasons = []
                
                # 1. 基础权重：文章热度
                views_weight = (article.views or 0) * 0.3
                likes_weight = (article.likes or 0) * 0.7
                base_weight = views_weight + likes_weight
                weight += base_weight
                
                if article.views > 100:
                    reasons.append({
                        'type': 'hot',
                        'text': f'热门文章，已有 {article.views} 次阅读'
                    })
                if article.likes > 10:
                    reasons.append({
                        'type': 'popular',
                        'text': f'广受欢迎，获得 {article.likes} 个赞'
                    })
                
                # 2. 时间衰减因子
                days_old = (datetime.utcnow() - article.created_at).days
                time_factor = 1 / (1 + days_old * 0.1)
                weight *= time_factor
                
                if days_old <= 1:
                    reasons.append({
                        'type': 'new',
                        'text': '新鲜出炉'
                    })
                elif days_old <= 3:
                    reasons.append({
                        'type': 'recent',
                        'text': '最近发布'
                    })
                
                # 3. 用户行为权重
                # 3.1 浏览记录
                for viewed in viewed_articles:
                    if viewed.article_id != article.id:
                        weight += 5
                        reasons.append({
                            'type': 'interest',
                            'text': '根据您的浏览历史推荐'
                        })
                        break
                
                # 3.2 点赞记录
                for liked in liked_articles:
                    if liked.article_id != article.id:
                        weight += 10
                        reasons.append({
                            'type': 'preference',
                            'text': '根据您的点赞偏好推荐'
                        })
                        break
                
                # 3.3 发布记录
                for user_article in user_articles:
                    if user_article.id != article.id:
                        weight += 15
                        reasons.append({
                            'type': 'similar',
                            'text': '与您发布的内容相关'
                        })
                        break
                
                # 4. 作者权重
                author = User.query.get(article.author_id)
                if author:
                    author_articles_count = Article.query.filter_by(author_id=author.id).count()
                    if author_articles_count > 10:
                        weight *= 1.2
                        reasons.append({
                            'type': 'author',
                            'text': '来自高产作者'
                        })
                
                # 计算最终推荐百分比（归一化到0-100）
                if weight > 0:
                    recommendations.append({
                        'article_id': article.id,
                        'title': article.title,
                        'author': author.username if author else '未知作者',
                        'author_nickname': author.nickname if author else None,
                        'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'views': article.views or 0,
                        'likes': article.likes or 0,
                        'weight': min(100, weight),
                        'reasons': reasons
                    })
            except Exception as e:
                print(f"处理文章 {article.id} 时出错: {str(e)}")
                continue
        
        # 按权重排序
        recommendations.sort(key=lambda x: x['weight'], reverse=True)
        print(f"生成 {len(recommendations)} 条推荐")
        
        # 只返回前10个推荐
        top_recommendations = recommendations[:10]
        print(f"返回前 {len(top_recommendations)} 条推荐")
        
        return jsonify({
            'code': 200,
            'message': '获取推荐成功',
            'data': top_recommendations
        })
        
    except Exception as e:
        print(f"获取文章推荐错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'message': '获取推荐失败'}), 500

@app.route('/api/user/role', methods=['GET'])
@jwt_required()
def get_user_role():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'role': user.role
            }
        })
    except Exception as e:
        print(f"获取用户角色错误: {str(e)}")
        return jsonify({'message': '获取用户角色失败'}), 500

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': '没有权限访问'}), 403
            
        # 获取统计数据
        total_users = User.query.count()
        total_articles = Article.query.count()
        total_views = db.session.query(func.sum(Article.views)).scalar() or 0
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'totalUsers': total_users,
                'totalArticles': total_articles,
                'totalViews': total_views
            }
        })
    except Exception as e:
        print(f"获取管理员统计数据错误: {str(e)}")
        return jsonify({'message': '获取统计数据失败'}), 500

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_admin_users():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': '没有权限访问'}), 403
            
        # 获取所有用户信息
        users = User.query.all()
        user_list = []
        
        for user in users:
            # 获取用户的文章统计
            articles = Article.query.filter_by(author_id=user.id).all()
            total_likes = sum(article.likes or 0 for article in articles)
            total_views = sum(article.views or 0 for article in articles)
            
            user_list.append({
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname or user.username,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录',
                'article_count': len(articles),
                'total_likes': total_likes,
                'total_views': total_views,
                'role': user.role,
                'is_banned': user.is_banned if hasattr(user, 'is_banned') else False
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user_list
        })
    except Exception as e:
        print(f"获取用户列表错误: {str(e)}")
        return jsonify({'message': '获取用户列表失败'}), 500

@app.route('/api/admin/articles', methods=['GET'])
@jwt_required()
def get_admin_articles():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        if not user or user.role != 'admin':
            return jsonify({'message': '没有权限访问'}), 403
            
        # 获取所有文章信息
        articles = Article.query.all()
        article_list = []
        
        for article in articles:
            author = User.query.get(article.author_id)
            # 获取评论数（如果有评论表的话）
            comment_count = 0  # TODO: 实现评论统计
            
            article_list.append({
                'id': article.id,
                'title': article.title,
                'author': author.username if author else '未知作者',
                'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': article.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'likes': article.likes or 0,
                'views': article.views or 0,
                'comments': comment_count,
                'is_hidden': article.is_hidden if hasattr(article, 'is_hidden') else False,
                'is_pinned': article.is_pinned if hasattr(article, 'is_pinned') else False
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': article_list
        })
    except Exception as e:
        print(f"获取文章列表错误: {str(e)}")
        return jsonify({'message': '获取文章列表失败'}), 500

@app.route('/api/admin/user/<int:user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(user_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        if user.role == 'admin':
            return jsonify({'message': '不能封禁管理员账号'}), 400
            
        user.is_banned = True
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '封禁成功'
        })
    except Exception as e:
        print(f"封禁用户错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/user/<int:user_id>/unban', methods=['POST'])
@jwt_required()
def unban_user(user_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        user.is_banned = False
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '解封成功'
        })
    except Exception as e:
        print(f"解封用户错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/user/<int:user_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        if user.role == 'admin':
            return jsonify({'message': '不能删除管理员账号'}), 400
            
        # 删除用户的所有文章
        Article.query.filter_by(author_id=user.id).delete()
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        print(f"删除用户错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/user/<int:user_id>/promote', methods=['POST'])
@jwt_required()
def promote_user(user_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
            
        if user.role == 'admin':
            return jsonify({'message': '该用户已经是管理员'}), 400
            
        user.role = 'admin'
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '提升成功'
        })
    except Exception as e:
        print(f"提升用户错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/article/<int:article_id>/hide', methods=['POST'])
@jwt_required()
def hide_article(article_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        article = Article.query.get(article_id)
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        article.is_hidden = True
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '隐藏成功'
        })
    except Exception as e:
        print(f"隐藏文章错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/article/<int:article_id>/show', methods=['POST'])
@jwt_required()
def show_article(article_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        article = Article.query.get(article_id)
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        article.is_hidden = False
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '显示成功'
        })
    except Exception as e:
        print(f"显示文章错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/article/<int:article_id>/delete', methods=['DELETE'])
@jwt_required()
def admin_delete_article(article_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({
            'code': 403,
            'message': '权限不足'
        }), 403
    
    article = Article.query.get(article_id)
    if not article:
        return jsonify({
            'code': 404,
            'message': '文章不存在'
        }), 404
    
    try:
        db.session.delete(article)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '文章删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '删除文章失败'
        }), 500

@app.route('/api/admin/article/<int:article_id>/pin', methods=['POST'])
@jwt_required()
def pin_article(article_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        article = Article.query.get(article_id)
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        article.is_pinned = True
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '置顶成功'
        })
    except Exception as e:
        print(f"置顶文章错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/admin/article/<int:article_id>/unpin', methods=['POST'])
@jwt_required()
def unpin_article(article_id):
    try:
        current_user = get_jwt_identity()
        admin = User.query.filter_by(username=current_user).first()
        
        if not admin or admin.role != 'admin':
            return jsonify({'message': '没有权限执行此操作'}), 403
            
        article = Article.query.get(article_id)
        if not article:
            return jsonify({'message': '文章不存在'}), 404
            
        article.is_pinned = False
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '取消置顶成功'
        })
    except Exception as e:
        print(f"取消置顶文章错误: {str(e)}")
        return jsonify({'message': '操作失败'}), 500

@app.route('/api/articles/<int:article_id>/comments', methods=['GET'])
def get_article_comments(article_id):
    try:
        def build_comment_tree(comments, parent_id=None):
            tree = []
            for comment in comments:
                if comment.parent_id == parent_id:
                    item = comment.to_dict()
                    # 新增：如果是回复，查找被回复的用户昵称
                    if comment.parent_id:
                        parent_comment = next((c for c in comments if c.id == comment.parent_id), None)
                        if parent_comment:
                            user = User.query.get(parent_comment.user_id)
                            item['reply_nickname'] = user.nickname if user else ''
                        else:
                            item['reply_nickname'] = ''
                    else:
                        item['reply_nickname'] = ''
                    # 获取当前用户的点赞状态
                    try:
                        current_user = get_jwt_identity()
                        if current_user:
                            user = User.query.filter_by(username=current_user).first()
                            if user:
                                like = CommentLike.query.filter_by(user_id=user.id, comment_id=comment.id).first()
                                item['liked'] = bool(like)
                        else:
                            item['liked'] = False
                    except:
                        item['liked'] = False
                    item['children'] = build_comment_tree(comments, comment.id)
                    tree.append(item)
            return tree

        comments = Comment.query.filter_by(article_id=article_id).order_by(Comment.floor.asc()).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': build_comment_tree(comments)
        })
    except Exception as e:
        print(f"获取评论错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '获取评论失败'
        }), 500

@app.route('/api/articles/<int:article_id>/comments', methods=['POST'])
@jwt_required()
def post_article_comment(article_id):
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    data = request.get_json()
    content = data.get('content')
    parent_id = data.get('parent_id')
    if not content:
        return jsonify({'message': '评论内容不能为空'}), 400
    
    # 获取当前文章最新的楼层号（包括子评论）
    latest_floor = db.session.query(db.func.max(Comment.floor)).filter_by(article_id=article_id).scalar() or 0
    # 新评论的楼层号 = 最新楼层号 + 1
    floor = latest_floor + 1
    
    comment = Comment(
        content=content,
        user_id=user.id,
        article_id=article_id,
        parent_id=parent_id,
        floor=floor
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'code': 200, 'message': '评论成功', 'data': comment.to_dict()})

@app.route('/api/comments/<int:comment_id>/like', methods=['POST'])
@jwt_required()
def like_comment(comment_id):
    try:
        user = User.query.filter_by(username=get_jwt_identity()).first()
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 检查用户是否被封禁
        if user.is_banned:
            return jsonify({
                'code': 403,
                'message': '您的账号已被封禁，无法进行此操作'
            }), 403
            
        like = CommentLike.query.filter_by(user_id=user.id, comment_id=comment_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({'code': 200, 'message': '取消点赞', 'liked': False})
        else:
            new_like = CommentLike(user_id=user.id, comment_id=comment_id)
            db.session.add(new_like)
            db.session.commit()
            return jsonify({'code': 200, 'message': '点赞成功', 'liked': True})
    except Exception as e:
        print(f"评论点赞错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '操作失败'
        }), 500

@app.route('/api/comments/<int:comment_id>/like', methods=['GET'])
@jwt_required()
def get_comment_like_status(comment_id):
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    like = CommentLike.query.filter_by(user_id=user.id, comment_id=comment_id).first()
    return jsonify({'code': 200, 'liked': bool(like)})

# 全局错误处理器
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'code': 404,
        'message': '资源不存在'
    }), 404

# 注册代理路由
app.register_blueprint(proxy_bp, url_prefix='/api/proxy')

# 初始化数据库
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 