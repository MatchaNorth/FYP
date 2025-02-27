# Flask + Vue 全栈应用

这是一个使用Flask作为后端、Vue作为前端的全栈应用项目。项目采用前后端分离的架构，后端使用Flask的蓝图实现路由分层，前端使用Vuex进行状态管理。

## 项目结构

```
.
├── backend/           # Flask后端项目
│   ├── app/          # 应用主目录
│   │   ├── api/      # API蓝图目录
│   │   ├── models/   # 数据模型
│   │   └── utils/    # 工具函数
│   ├── config.py     # 配置文件
│   └── run.py        # 应用入口
│
└── frontend/         # Vue前端项目
    ├── src/
    │   ├── assets/   # 静态资源
    │   ├── components/# Vue组件
    │   ├── store/    # Vuex状态管理
    │   ├── views/    # 页面视图
    │   └── App.vue   # 根组件
    └── package.json  # 项目依赖
```

## 启动说明

### 后端启动
1. 进入backend目录
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`python run.py`

### 前端启动
1. 进入frontend目录
2. 安装依赖：`npm install`
3. 开发模式启动：`npm run dev`
4. 构建生产版本：`npm run build`

## 技术栈

### 后端
- Flask
- Flask-CORS
- Python-dotenv

### 前端
- Vue 3
- Vuex 4
- Vue Router 4
- Axios
- Vite