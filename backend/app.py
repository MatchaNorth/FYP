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
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # 小黑盒相关字段
    heybox_id = db.Column(db.String(20))  # 小黑盒ID
    heybox_nickname = db.Column(db.String(80))  # 小黑盒昵称
    heybox_avatar = db.Column(db.String(255))  # 小黑盒头像URL
    heybox_profile = db.Column(db.String(255))  # 小黑盒个人主页URL
    articles = db.relationship('Article', backref='author', lazy=True)
    avatar = db.Column(db.String(255))  # 用户头像URL

    def __init__(self, username, password, nickname=None):
        self.username = username
        self.password = password
        self.nickname = nickname

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'days_since_registration': (datetime.utcnow() - self.created_at).days,
            'heybox_id': self.heybox_id,
            'heybox_nickname': self.heybox_nickname,
            'heybox_avatar': self.heybox_avatar,
            'heybox_profile': self.heybox_profile,
            'avatar': self.avatar
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
            'likes': self.likes
        }

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