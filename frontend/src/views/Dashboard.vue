<template>
  <div class="dashboard-container" :class="{ 'dark': isDark }">
    <!-- 侧边栏 -->
    <div class="sidebar glass-card" :class="{ 'collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span v-show="!isSidebarCollapsed">管理系统</span>
        </div>
        <button class="collapse-btn" @click="isSidebarCollapsed = !isSidebarCollapsed">
          <i :class="isSidebarCollapsed ? 'el-icon-d-arrow-right' : 'el-icon-d-arrow-left'"></i>
        </button>
      </div>
      
      <div class="sidebar-content">
        <div class="user-profile-mini">
          <el-avatar :size="40" :src="avatarUrl">
            {{ nickname?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="user-info" v-show="!isSidebarCollapsed">
            <h3>{{ nickname }}</h3>
            <p>{{ userRole === 'admin' ? '管理员' : '普通用户' }}</p>
          </div>
        </div>
        
        <nav class="nav-menu">
          <div 
            class="nav-item" 
            :class="{ 'active': currentView === 'overview', 'collapsed': isSidebarCollapsed }"
            @click="switchView('overview')"
          >
            <i class="el-icon-menu"></i>
            <span v-show="!isSidebarCollapsed">总览</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ 'active': currentView === 'articles', 'collapsed': isSidebarCollapsed }"
            @click="switchView('articles')"
          >
            <i class="el-icon-document"></i>
            <span v-show="!isSidebarCollapsed">文章管理</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ 'active': currentView === 'profile', 'collapsed': isSidebarCollapsed }"
            @click="switchView('profile')"
          >
            <i class="el-icon-user"></i>
            <span v-show="!isSidebarCollapsed">个人资料</span>
          </div>
          <div 
            v-if="userRole === 'admin' || isSuperAdmin"
            class="nav-item" 
            :class="{ 'active': currentView === 'admin', 'collapsed': isSidebarCollapsed }"
            @click="switchView('admin')"
          >
            <i class="el-icon-setting"></i>
            <span v-show="!isSidebarCollapsed">管理系统</span>
          </div>
          <div 
            v-if="userRole === 'admin' || isSuperAdmin"
            class="nav-item" 
            :class="{ 'active': currentView === 'report', 'collapsed': isSidebarCollapsed }"
            @click="switchView('report')"
          >
            <i class="el-icon-warning"></i>
            <span v-show="!isSidebarCollapsed">举报管理</span>
          </div>
        </nav>
      </div>
      
      <div class="sidebar-footer" @click="handleLogout">
        <i class="el-icon-switch-button"></i>
        <span v-show="!isSidebarCollapsed">退出登录</span>
      </div>
      <button class="theme-toggle" @click="toggleTheme">
        <i :class="isDark ? 'el-icon-sunny' : 'el-icon-moon'"></i>
      </button>
    </div>

    <!-- 主内容区 -->
    <div class="main-content" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="main-header glass-card">
        <div class="breadcrumb">
          <h2>{{ viewTitles[currentView] }}</h2>
          <p>{{ new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
        </div>
        <div class="header-actions">
          <button class="back-home-btn" @click="router.push('/')">
            <i class="el-icon-back"></i>
            <span>返回首页</span>
          </button>
        </div>
      </div>

      <div class="view-container">
        <!-- 总览页面 -->
        <div v-if="currentView === 'overview'" class="overview-view" :class="{ 'fade-enter': viewTransition }">
          <div class="stats-grid">
            <div 
              class="stat-card glass-card" 
              :class="{ 'highlight': articleStats.total > 0 }"
              @mouseenter="e => handleCardHover(e, true)"
              @mouseleave="e => handleCardHover(e, false)"
            >
              <div class="stat-icon article-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="stat-info">
                <h3>文章总数</h3>
                <p>{{ articleStats.total || 0 }}</p>
                <div class="stat-trend" v-if="articleStats.total > 0">
                  <i class="el-icon-top"></i>
                  <span>较上月增长 {{ articleStats.growth || 0 }}%</span>
                </div>
              </div>
            </div>
            <div 
              class="stat-card glass-card" 
              :class="{ 'highlight': articleStats.views > 0 }"
              @mouseenter="e => handleCardHover(e, true)"
              @mouseleave="e => handleCardHover(e, false)"
            >
              <div class="stat-icon view-icon">
                <i class="el-icon-view"></i>
              </div>
              <div class="stat-info">
                <h3>总阅读量</h3>
                <p>{{ articleStats.views || 0 }}</p>
                <div class="stat-trend positive" v-if="articleStats.views > 0">
                  <i class="el-icon-top"></i>
                  <span>今日 +{{ articleStats.todayViews || 0 }}</span>
                </div>
              </div>
            </div>
            <div 
              class="stat-card glass-card" 
              :class="{ 'highlight': daysSinceRegistration > 0 }"
              @mouseenter="e => handleCardHover(e, true)"
              @mouseleave="e => handleCardHover(e, false)"
            >
              <div class="stat-icon time-icon">
                <i class="el-icon-time"></i>
              </div>
              <div class="stat-info">
                <h3>注册天数</h3>
                <p>{{ daysSinceRegistration }}天</p>
                <div class="stat-badge" v-if="daysSinceRegistration >= 30">
                  <i class="el-icon-medal"></i>
                  <span>活跃用户</span>
                </div>
              </div>
            </div>
          </div>

          <div class="recent-activities glass-card">
            <div class="section-header">
              <h3>最近活动</h3>
            </div>
            <div class="activity-timeline">
              <el-timeline>
                <el-timeline-item
                  v-for="(activity, index) in recentActivities"
                  :key="index"
                  :timestamp="activity.time"
                  :type="activity.type"
                >
                  <div class="activity-item">
                    <span>{{ activity.content }}</span>
                    <el-button
                      v-if="activity.type !== 'primary' && activity.type !== 'success'"
                      type="danger"
                      size="small"
                      circle
                      @click="handleDeleteActivity(activity.id)"
                    >
                      <i class="el-icon-delete"></i>
                    </el-button>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </div>

        <!-- 文章管理页面 -->
        <article-manager 
          v-else-if="currentView === 'articles'" 
          :class="{ 'fade-enter': viewTransition }"
        />

        <!-- 个人资料页面 -->
        <div v-else-if="currentView === 'profile'" class="profile-view" :class="{ 'fade-enter': viewTransition }">
          <div class="profile-card">
            <div class="profile-header">
              <div class="avatar-container">
                <el-avatar :size="100" :src="avatarUrl">
                  {{ nickname?.charAt(0)?.toUpperCase() }}
                </el-avatar>
                <button class="change-avatar-btn" @click="avatarDialogVisible = true">
                  <i class="el-icon-camera"></i>
                  <span>更换头像</span>
                </button>
              </div>
              <div class="profile-info">
                <h2>{{ nickname }}</h2>
                <p>{{ username }}</p>
              </div>
              <el-button type="primary" @click="editProfileDialogVisible = true">
                编辑资料
              </el-button>
            </div>
            
            <div class="profile-details">
              <div class="info-group">
                <label>注册时间</label>
                <span>{{ registrationDate }}</span>
              </div>
              <div class="info-group">
                <label>上次登录</label>
                <span>{{ lastLoginTime }}</span>
              </div>
              <div class="info-group">
                <label>账号状态</label>
                <el-tag 
                  size="small" 
                  :type="isBanned ? 'danger' : 'success'"
                >
                  <i :class="isBanned ? 'el-icon-warning' : 'el-icon-check'"></i>
                  <span>{{ isBanned ? '已封禁' : '正常使用中' }}</span>
                </el-tag>
              </div>
            </div>
          </div>

          <div class="security-section">
            <div class="section-header">
              <h3>账号安全</h3>
            </div>
            <div class="security-cards">
              <div class="security-card">
                <i class="el-icon-lock"></i>
                <div class="security-info">
                  <h4>修改密码</h4>
                  <p>定期更换密码以保护账号安全</p>
                </div>
                <el-button type="text">修改</el-button>
              </div>
              <div class="security-card">
                <i class="el-icon-mobile-phone"></i>
                <div class="security-info">
                  <h4>绑定手机</h4>
                  <p>绑定手机号获得额外安全保障</p>
                </div>
                <el-button type="text">绑定</el-button>
              </div>
              <div class="security-card">
                <i class="el-icon-message"></i>
                <div class="security-info">
                  <h4>绑定邮箱</h4>
                  <p>绑定邮箱接收重要通知</p>
                </div>
                <el-button type="text">绑定</el-button>
              </div>
            </div>
          </div>

          <div class="connect-section">
            <div class="section-header">
              <h3>第三方账号</h3>
              <p>绑定第三方账号，享受更多功能</p>
            </div>
            <div class="connect-cards">
              <div class="connect-card" :class="{ 'is-bound': isHeyboxBound }">
                <div class="connect-icon">
                  <i class="icon-gamepad"></i>
                </div>
                <div class="connect-info">
                  <h4>小黑盒</h4>
                  <p v-if="isHeyboxBound">已绑定 - ID: {{ heyboxId }}</p>
                  <p v-else>导入游戏数据，同步游戏记录</p>
                </div>
                <button 
                  class="connect-btn"
                  :class="{ 'is-bound': isHeyboxBound }"
                  @click="handleHeyboxAction"
                  @mouseenter="showUnbindText = true"
                  @mouseleave="showUnbindText = false"
                >
                  <i :class="isHeyboxBound ? 'icon-close' : 'icon-link'"></i>
                  <span>{{ isHeyboxBound ? (showUnbindText ? '解绑' : '已绑定') : '绑定' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 管理系统页面 -->
        <div v-else-if="currentView === 'admin'" class="admin-view" :class="{ 'fade-enter': viewTransition }">
          <div class="admin-stats">
            <div class="stat-card">
              <h3>总用户数</h3>
              <p>{{ adminStats.totalUsers }}</p>
            </div>
            <div class="stat-card">
              <h3>总文章数</h3>
              <p>{{ adminStats.totalArticles }}</p>
            </div>
          </div>

          <div class="admin-section">
            <h2>用户管理</h2>
            <table class="admin-table">
              <thead>
                <tr>
                  <th>用户名</th>
                  <th>昵称</th>
                  <th>注册时间</th>
                  <th>最后登录</th>
                  <th>文章数</th>
                  <th>获赞数</th>
                  <th>总浏览量</th>
                  <th>角色</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.nickname }}</td>
                  <td>{{ user.created_at }}</td>
                  <td>{{ user.last_login }}</td>
                  <td>{{ user.article_count }}</td>
                  <td>{{ user.total_likes }}</td>
                  <td>{{ user.total_views }}</td>
                  <td>{{ user.role === 'admin' ? '管理员' : '普通用户' }}</td>
                  <td>{{ user.is_banned ? '已封禁' : '正常' }}</td>
                  <td>
                    <template v-if="user.username === 'administrator'">
                      <!-- 超级管理员无操作 -->
                    </template>
                    <template v-else-if="user.role === 'admin'">
                      <button v-if="isSuperAdmin" @click="handleUserAction(user.id, 'demote')" class="btn-info">降级为普通用户</button>
                    </template>
                    <template v-else>
                      <button v-if="!user.is_banned" @click="handleUserAction(user.id, 'ban')" class="btn-warning">封禁</button>
                      <button v-else @click="handleUserAction(user.id, 'unban')" class="btn-success">解封</button>
                      <button v-if="userRole === 'admin' || isSuperAdmin" @click="handleUserAction(user.id, 'promote')" class="btn-primary">提升为管理员</button>
                      <button @click="handleUserAction(user.id, 'delete')" class="btn-danger">删除</button>
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="admin-section">
            <h2>文章管理</h2>
            <table class="admin-table">
              <thead>
                <tr>
                  <th>标题</th>
                  <th>作者</th>
                  <th>发布时间</th>
                  <th>最后修改</th>
                  <th>获赞数</th>
                  <th>浏览量</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="article in articles" :key="article.id">
                  <td>{{ article.title }}</td>
                  <td>{{ article.author }}</td>
                  <td>{{ article.created_at }}</td>
                  <td>{{ article.updated_at }}</td>
                  <td>{{ article.likes }}</td>
                  <td>{{ article.views }}</td>
                  <td>
                    <span v-if="article.is_hidden">已隐藏</span>
                    <span v-else-if="article.is_pinned">已置顶</span>
                    <span v-else>正常</span>
                  </td>
                  <td>
                    <button v-if="!article.is_hidden" @click="handleArticleAction(article.id, 'hide')" class="btn-warning">隐藏</button>
                    <button v-else @click="handleArticleAction(article.id, 'show')" class="btn-success">显示</button>
                    <button v-if="!article.is_pinned" @click="handleArticleAction(article.id, 'pin')" class="btn-primary">置顶</button>
                    <button v-else @click="handleArticleAction(article.id, 'unpin')" class="btn-info">取消置顶</button>
                    <button @click="handleArticleAction(article.id, 'delete')" class="btn-danger">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 举报管理页面 -->
        <div v-else-if="currentView === 'report'" class="report-view" :class="{ 'fade-enter': viewTransition }">
          <div class="report-tabs">
            <button :class="{active: reportTab === 'user'}" @click="reportTab = 'user'">用户举报</button>
            <button :class="{active: reportTab === 'article'}" @click="reportTab = 'article'">文章举报</button>
            <button :class="{active: reportTab === 'comment'}" @click="reportTab = 'comment'">评论举报</button>
          </div>
          <div class="report-table-container">
            <table class="report-table">
              <thead>
                <tr>
                  <th v-if="reportTab === 'user'">用户名</th>
                  <th v-if="reportTab === 'article'">文章标题</th>
                  <th v-if="reportTab === 'comment'">评论内容</th>
                  <th>被举报次数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in reportData[reportTab]" :key="item.id"
                    :style="getReportRowStyle(item.count)"
                    @click="showReportDetail(reportTab, item)">
                  <td v-if="reportTab === 'user'">{{ item.username }}</td>
                  <td v-if="reportTab === 'article'">{{ item.title }}</td>
                  <td v-if="reportTab === 'comment'">{{ item.content }}</td>
                  <td><span :style="getReportTextStyle(item.count)">{{ item.count }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <el-dialog v-model="reportDetailDialogVisible" title="举报详情" width="400px">
            <el-table :data="reportDetail" style="width: 100%">
              <el-table-column prop="reporter_username" label="举报人" width="120" />
              <el-table-column prop="report_time" label="举报时间" />
            </el-table>
            <div class="report-actions" v-if="reportTab === 'comment' || reportTab === 'article' || reportTab === 'user'">
              <el-button 
                v-if="reportTab === 'comment'"
                type="danger" 
                @click="handleReportAction('delete_comment')"
              >
                删除评论
              </el-button>
              <template v-if="reportTab === 'article'">
                <el-button 
                  type="danger" 
                  @click="handleReportAction('delete_article')"
                >
                  删除文章
                </el-button>
                <el-button 
                  type="warning" 
                  @click="handleReportAction('hide_article')"
                >
                  隐藏文章
                </el-button>
              </template>
              <el-button 
                v-if="reportTab === 'user'"
                type="danger"
                @click="handleReportAction('ban_user')"
              >
                封禁用户
              </el-button>
              <el-button 
                type="primary" 
                @click="handleReportAction('view')"
              >
                查看{{ reportTab === 'comment' ? '评论' : reportTab === 'article' ? '文章' : '用户' }}
              </el-button>
            </div>
          </el-dialog>
        </div>
      </div>
    </div>
  </div>

  <div v-if="!isHeyboxBound" class="bind-dialog" v-show="heyboxDialogVisible">
    <div class="dialog-content">
      <h3>绑定小黑盒账号</h3>
      <p>请输入您的小黑盒个人主页链接：</p>
      <input 
        type="text" 
        v-model="heyboxProfileUrl" 
        placeholder="例如：https://xiaoheihe.cn/user/profile/12345678"
        class="input-field"
      >
      <div class="dialog-footer">
        <button class="btn-cancel" @click="heyboxDialogVisible = false">取消</button>
        <button class="btn-confirm" @click="handleBindHeybox">确认</button>
      </div>
    </div>
  </div>

  <div v-if="editProfileDialogVisible" class="bind-dialog">
    <div class="dialog-content">
      <h3>编辑个人资料</h3>
      <div class="form-group">
        <label>昵称</label>
        <input 
          type="text" 
          v-model="editingNickname" 
          placeholder="请输入昵称"
          class="input-field"
        >
      </div>
      <div class="dialog-footer">
        <button class="btn-cancel" @click="editProfileDialogVisible = false">取消</button>
        <button class="btn-confirm" @click="handleUpdateProfile">确认</button>
      </div>
    </div>
  </div>

  <!-- 添加头像上传对话框 -->
  <div v-if="avatarDialogVisible" class="bind-dialog">
    <div class="dialog-content">
      <h3>更换头像</h3>
      <div class="avatar-upload">
        <input 
          type="file" 
          ref="avatarInput"
          @change="handleAvatarChange" 
          accept="image/jpeg,image/png"
          class="file-input"
        >
        <div class="upload-preview" v-if="avatarPreview">
          <img :src="avatarPreview" alt="Avatar preview" class="preview-image">
        </div>
        <button class="btn-upload" @click="triggerFileInput">
          <i class="icon-upload"></i>
          <span>点击上传</span>
        </button>
        <p class="upload-tip">支持 jpg、png 格式的图片</p>
      </div>
      <div class="dialog-footer">
        <button class="btn-cancel" @click="closeAvatarDialog">取消</button>
        <button 
          class="btn-confirm" 
          @click="handleAvatarUpload"
          :disabled="!avatarFile"
        >
          确认上传
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ArticleManager from './ArticleManager.vue'
import gsap from 'gsap'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'

// 注册 GSAP 插件
gsap.registerPlugin(ScrollToPlugin)

const router = useRouter()
const username = ref('')
const nickname = ref('')
const userRole = ref('user')
const registrationDate = ref('')
const lastLoginTime = ref('首次登录')
const avatarUrl = ref('')
const daysSinceRegistration = ref(0)
const heyboxDialogVisible = ref(false)
const heyboxProfileUrl = ref('')
const isBinding = ref(false)
const editProfileDialogVisible = ref(false)
const editingNickname = ref('')
const isUpdating = ref(false)
const heyboxId = ref('')
const isHeyboxBound = ref(false)
const showUnbindText = ref(false)
const isBanned = ref(false)

const recentActivities = ref([])

// 新增的响应式数据
const isSidebarCollapsed = ref(false)
const currentView = ref('overview')
const viewTransition = ref(false)
const articleStats = ref({
  total: 0,
  published: 0,
  draft: 0,
  views: 0,
  todayViews: 0
})

const adminStats = ref({
  totalUsers: 0,
  totalArticles: 0
})

const users = ref([])
const articles = ref([])

const viewTitles = {
  overview: '总览',
  articles: '文章管理',
  profile: '个人资料',
  admin: '管理系统',
  report: '举报管理'
}

// 主题切换
const isDark = ref(false)
const toggleTheme = () => {
  isDark.value = !isDark.value
  gsap.to(document.documentElement, {
    '--bg-color': isDark.value ? '#1a1b1e' : '#ffffff',
    '--text-color': isDark.value ? '#f8f9fa' : '#2D3436',
    '--card-bg': isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.8)',
    duration: 0.8,
    ease: 'sine.inOut'
  })
}

// 数值动画
const animateNumber = (target, value, duration = 1.5) => {
  gsap.to(target, {
    duration,
    value,
    roundProps: 'value',
    ease: 'power3.out',
    onUpdate: () => {
      // 确保值被正确更新
      if (typeof target === 'object' && target !== null) {
        target.value = Math.round(target.value)
      }
    }
  })
}

// 卡片悬浮动画
const handleCardHover = (event, enter) => {
  gsap.to(event.currentTarget, {
    y: enter ? -10 : 0,
    scale: enter ? 1.02 : 1,
    duration: 0.3,
    ease: 'power2.out'
  })
}

// 监听数据变化
watch(() => articleStats.value, (newVal) => {
  if (newVal) {
    animateNumber(articleStats.value, 'total')
    animateNumber(articleStats.value, 'views')
  }
}, { deep: true })

// 获取用户活动记录
const fetchUserActivities = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/user/activities', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      recentActivities.value = response.data.data.map(activity => ({
        id: activity.id,
        content: activity.description,
        time: new Date(activity.created_at).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }),
        type: getActivityType(activity.activity_type)
      }))
    }
  } catch (error) {
    console.error('获取用户活动记录失败:', error)
  }
}

// 根据活动类型返回对应的样式
const getActivityType = (type) => {
  const typeMap = {
    'login': 'primary',    // 登录活动
    'register': 'success', // 注册活动
    'profile': 'info',     // 个人信息相关
    'security': 'warning', // 安全相关
    'article': 'success'   // 文章相关
  }
  return typeMap[type] || 'info'
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    
    ElMessage({
      message: '已安全退出登录',
      type: 'success',
      duration: 2000,
      showClose: true,
      offset: 80
    })
    
    router.push('/login')
  } catch {
    // 用户取消退出
  }
}

// 处理小黑盒按钮点击
const handleHeyboxAction = () => {
  if (isHeyboxBound.value) {
    handleUnbindHeybox()
  } else {
    heyboxDialogVisible.value = true
    heyboxProfileUrl.value = '' // 重置输入框
  }
}

// 绑定小黑盒账号
const handleBindHeybox = async () => {
  if (!heyboxProfileUrl.value) {
    ElMessage.warning('请输入小黑盒个人主页链接')
    return
  }
  
  try {
    isBinding.value = true
    const token = localStorage.getItem('token')
    const response = await axios.post(
      'http://localhost:5000/api/user/bind-heybox',
      { profile_url: heyboxProfileUrl.value },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    if (response.data.code === 200) {
      ElMessage.success('绑定成功')
      heyboxDialogVisible.value = false
      // 更新用户信息
      const userData = response.data.data
      nickname.value = userData.nickname || userData.username
      avatarUrl.value = userData.heybox_avatar || ''
      heyboxId.value = userData.heybox_id
      isHeyboxBound.value = true
      // 清空输入框
      heyboxProfileUrl.value = ''
      // 刷新活动记录
      fetchUserActivities()
    }
  } catch (error) {
    console.error('绑定小黑盒账号失败:', error)
    ElMessage.error(error.response?.data?.message || '绑定失败')
  } finally {
    isBinding.value = false
  }
}

// 解绑小黑盒账号
const handleUnbindHeybox = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要解绑小黑盒账号吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('token')
    const response = await axios.post(
      'http://localhost:5000/api/user/unbind-heybox',
      {},
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    if (response.data.code === 200) {
      ElMessage.success('解绑成功')
      // 更新用户信息
      const userData = response.data.data
      avatarUrl.value = ''
      nickname.value = userData.username
      heyboxId.value = ''
      isHeyboxBound.value = false
      // 刷新活动记录
      fetchUserActivities()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解绑小黑盒账号失败:', error)
      ElMessage.error(error.response?.data?.message || '解绑失败')
    }
  }
}

// 获取文章统计信息
const fetchArticleStats = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/articles/stats', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.data.code === 200) {
      articleStats.value = response.data.data
      // 触发数值动画
      animateNumber(articleStats.value, 'total')
      animateNumber(articleStats.value, 'views')
    }
  } catch (error) {
    console.error('获取文章统计信息失败:', error)
  }
}

// 获取管理员统计数据
const fetchAdminStats = async () => {
  try {
    const [statsRes, usersRes, articlesRes] = await Promise.all([
      fetch('http://localhost:5000/api/admin/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }),
      fetch('http://localhost:5000/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }),
      fetch('http://localhost:5000/api/admin/articles', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
    ])

    const statsData = await statsRes.json()
    const usersData = await usersRes.json()
    const articlesData = await articlesRes.json()

    if (statsData.code === 200) {
      adminStats.value = statsData.data
    }
    if (usersData.code === 200) {
      users.value = usersData.data
    }
    if (articlesData.code === 200) {
      articles.value = articlesData.data
    }
  } catch (error) {
    console.error('获取管理数据失败:', error)
  }
}

// 用户操作处理函数
const handleUserAction = async (userId, action) => {
  let actionText = ''
  switch (action) {
    case 'ban': actionText = '封禁'; break;
    case 'unban': actionText = '解封'; break;
    case 'delete': actionText = '删除'; break;
    case 'promote': actionText = '提升为管理员'; break;
    case 'demote': actionText = '降级为普通用户'; break;
  }
  if (!confirm(`确定要${actionText}该用户吗？`)) {
    return
  }

  try {
    let url = ''
    let method = 'POST'
    switch (action) {
      case 'ban':
        url = `http://localhost:5000/api/admin/user/${userId}/ban`
        break
      case 'unban':
        url = `http://localhost:5000/api/admin/user/${userId}/unban`
        break
      case 'delete':
        url = `http://localhost:5000/api/admin/user/${userId}/delete`
        method = 'DELETE'
        break
      case 'promote':
        url = `http://localhost:5000/api/admin/user/${userId}/promote`
        break
      case 'demote':
        url = `http://localhost:5000/api/admin/user/${userId}/demote`
        break
    }
    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      alert(data.message)
      fetchAdminStats() // 刷新数据
    } else {
      alert(data.message || '操作失败')
    }
  } catch (error) {
    console.error('操作失败:', error)
    alert('操作失败')
  }
}

// 文章操作处理函数
const handleArticleAction = async (articleId, action) => {
  if (!confirm(`确定要${action === 'hide' ? '隐藏' : action === 'show' ? '显示' : action === 'delete' ? '删除' : action === 'pin' ? '置顶' : '取消置顶'}该文章吗？`)) {
    return
  }

  try {
    let url = ''
    let method = 'POST'
    
    switch (action) {
      case 'hide':
        url = `http://localhost:5000/api/admin/article/${articleId}/hide`
        break
      case 'show':
        url = `http://localhost:5000/api/admin/article/${articleId}/show`
        break
      case 'delete':
        url = `http://localhost:5000/api/admin/article/${articleId}/delete`
        method = 'DELETE'
        break
      case 'pin':
        url = `http://localhost:5000/api/admin/article/${articleId}/pin`
        break
      case 'unpin':
        url = `http://localhost:5000/api/admin/article/${articleId}/unpin`
        break
    }

    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    const data = await response.json()
    if (data.code === 200) {
      alert(data.message)
      fetchAdminStats() // 刷新数据
    } else {
      alert(data.message || '操作失败')
    }
  } catch (error) {
    console.error('操作失败:', error)
    alert('操作失败')
  }
}

// 检查登录状态
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  
  // 获取用户详细信息
  try {
    const [profileResponse, roleResponse] = await Promise.all([
      axios.get('http://localhost:5000/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      axios.get('http://localhost:5000/api/user/role', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    ])
    
    const userData = profileResponse.data.data
    username.value = userData.username
    nickname.value = userData.nickname || userData.username
    userRole.value = roleResponse.data.data.role
    isBanned.value = userData.is_banned // 添加封禁状态
    // 设置头像和小黑盒信息
    if (userData.avatar) {
      avatarUrl.value = userData.avatar
    }
    if (userData.heybox_id) {
      heyboxId.value = userData.heybox_id
      isHeyboxBound.value = true
    }
    registrationDate.value = new Date(userData.created_at).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
    daysSinceRegistration.value = userData.days_since_registration
    if (userData.last_login) {
      lastLoginTime.value = new Date(userData.last_login).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 获取用户活动记录和文章统计
    await Promise.all([
      fetchUserActivities(),
      fetchArticleStats()
    ])

    if (userRole.value === 'admin') {
      await fetchAdminStats()
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
  }
})

// 更新用户资料
const handleUpdateProfile = async () => {
  try {
    isUpdating.value = true
    const token = localStorage.getItem('token')
    const response = await axios.put(
      'http://localhost:5000/api/user/profile',
      { nickname: editingNickname.value },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    if (response.data.code === 200) {
      ElMessage.success('更新成功')
      editProfileDialogVisible.value = false
      // 更新页面显示的昵称
      nickname.value = response.data.data.nickname
      // 刷新活动记录
      fetchUserActivities()
    }
  } catch (error) {
    console.error('更新用户资料失败:', error)
    ElMessage.error(error.response?.data?.message || '更新失败')
  } finally {
    isUpdating.value = false
  }
}

// 删除活动记录
const handleDeleteActivity = async (activityId) => {
  if (!activityId) {
    ElMessage.error('无效的活动记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要删除这条活动记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('token')
    const response = await axios.delete(
      `http://localhost:5000/api/user/activities/${activityId}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    if (response.data.code === 200) {
      ElMessage.success('删除成功')
      // 刷新活动记录
      fetchUserActivities()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除活动记录失败:', error)
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

// 切换视图的方法
const switchView = (view) => {
  viewTransition.value = true
  currentView.value = view
  setTimeout(() => {
    viewTransition.value = false
  }, 300)
}

// 添加 RGB 变量用于渐变效果
document.documentElement.style.setProperty('--primary-rgb', '79, 70, 229')
document.documentElement.style.setProperty('--primary-light-rgb', '129, 140, 248')
document.documentElement.style.setProperty('--secondary-rgb', '16, 185, 129')

// 头像上传相关
const avatarDialogVisible = ref(false)
const avatarInput = ref(null)
const avatarFile = ref(null)
const avatarPreview = ref('')

const triggerFileInput = () => {
  avatarInput.value.click()
}

const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    avatarFile.value = file
    avatarPreview.value = URL.createObjectURL(file)
  }
}

const closeAvatarDialog = () => {
  avatarDialogVisible.value = false
  avatarFile.value = null
  avatarPreview.value = ''
}

const handleAvatarUpload = async () => {
  if (!avatarFile.value) return
  
  const formData = new FormData()
  formData.append('file', avatarFile.value)
  
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(
      'http://localhost:5000/api/user/avatar',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    if (response.data.code === 200) {
      ElMessage.success('头像上传成功')
      closeAvatarDialog()
      // 刷新用户信息
      await fetchUserProfile()
    }
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('上传头像失败')
  }
}

const reportTab = ref('user')
const reportData = ref({ user: [], article: [], comment: [] })
const reportDetailDialogVisible = ref(false)
const reportDetail = ref([])

const fetchReportSummary = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:5000/api/admin/reports/summary', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.data && res.data.code === 200) {
      reportData.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('获取举报统计失败')
  }
}

const showReportDetail = async (type, item) => {
  try {
    currentReportId.value = item.id
    const token = localStorage.getItem('token')
    const res = await axios.get(`http://localhost:5000/api/admin/reports/detail?type=${type}&id=${item.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.data && res.data.code === 200) {
      // 保存完整的举报信息，包括文章ID
      reportDetail.value = res.data.data
      // 更新当前项的完整信息
      const index = reportData.value[type].findIndex(i => i.id === item.id)
      if (index !== -1) {
        reportData.value[type][index] = {
          ...reportData.value[type][index],
          ...res.data.data[0] // 使用第一条举报记录的完整信息
        }
      }
      reportDetailDialogVisible.value = true
    }
  } catch (e) {
    ElMessage.error('获取举报详情失败')
  }
}

const getReportRowStyle = (count) => {
  // 颜色深度随count递增，最大深度为5
  const max = Math.max(...reportData.value[reportTab.value].map(i => i.count), 1)
  const percent = Math.min(count / max, 1)
  const bg = `rgba(239,68,68,${0.1 + percent * 0.5})`
  return { background: bg, cursor: 'pointer' }
}
const getReportTextStyle = (count) => {
  const max = Math.max(...reportData.value[reportTab.value].map(i => i.count), 1)
  const percent = Math.min(count / max, 1)
  const color = percent > 0.7 ? '#fff' : percent > 0.4 ? '#fffbe6' : '#EF4444'
  return { color, fontWeight: 'bold' }
}
// 1. script setup 部分，增加 isSuperAdmin 变量
const isSuperAdmin = computed(() => username.value === 'administrator')
// 监听 reportTab，只有管理员才自动获取举报统计
watch(reportTab, () => {
  if (userRole.value === 'admin' || isSuperAdmin.value) {
    fetchReportSummary()
  }
}, { immediate: true })

// 在 script setup 部分添加处理函数
const handleReportAction = async (action) => {
  const currentItem = reportData.value[reportTab.value].find(item => item.id === currentReportId.value)
  if (!currentItem) return

  try {
    switch (action) {
      case 'delete_comment':
        await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await axios.delete(`http://localhost:5000/api/admin/comments/${currentItem.id}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        ElMessage.success('评论已删除')
        break

      case 'delete_article':
        await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await axios.delete(`http://localhost:5000/api/admin/articles/${currentItem.id}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        ElMessage.success('文章已删除')
        break

      case 'hide_article':
        await ElMessageBox.confirm('确定要隐藏这篇文章吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await axios.post(`http://localhost:5000/api/admin/articles/${currentItem.id}/hide`, {}, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        ElMessage.success('文章已隐藏')
        break

      case 'view':
        if (reportTab.value === 'comment') {
          // 优先用举报详情里的 article_id
          const detail = reportDetail.value[0]
          if (detail && detail.article_id) {
            router.push(`/articles/public/${detail.article_id}`)
          } else {
            ElMessage.warning('无法获取评论所属文章')
          }
        } else if (reportTab.value === 'article') {
          if (currentItem.id) {
            router.push(`/articles/public/${currentItem.id}`)
          } else {
            ElMessage.warning('无法获取文章信息')
          }
        }
        else if (reportTab.value === 'user') {
          router.push(`/user/${currentItem.id}`)
        }
        break

      case 'ban_user':
        await ElMessageBox.confirm('确定要封禁该用户吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await axios.post(`http://localhost:5000/api/admin/user/${currentItem.id}/ban`, {}, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
        ElMessage.success('用户已封禁')
        break
    }
    
    // 刷新举报列表
    await fetchReportSummary()
    reportDetailDialogVisible.value = false
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error(error.response?.data?.message || '操作失败')
    }
  }
}

// 添加当前举报项的 ID
const currentReportId = ref(null)


</script>

<style>
:root {
  /* 主题色系 */
  --primary: #4F46E5;
  --primary-light: #818CF8;
  --secondary: #10B981;
  --accent: #F59E0B;
  --danger: #EF4444;
  
  /* 明亮主题 */
  --bg-gradient: linear-gradient(135deg, #EEF2FF 0%, #F3F4F6 100%);
  --card-bg: rgba(255, 255, 255, 0.9);
  --text-primary: #1F2937;
  --text-secondary: #6B7280;
  --border-color: rgba(229, 231, 235, 0.6);
  
  /* 暗色主题 */
  --dark-bg-gradient: linear-gradient(135deg, #1E1B4B 0%, #1F2937 100%);
  --dark-card-bg: rgba(30, 41, 59, 0.8);
  --dark-text-primary: #F3F4F6;
  --dark-text-secondary: #9CA3AF;
  --dark-border-color: rgba(75, 85, 99, 0.4);
}

.dark {
  --bg-gradient: var(--dark-bg-gradient);
  --card-bg: var(--dark-card-bg);
  --text-primary: var(--dark-text-primary);
  --text-secondary: var(--dark-text-secondary);
  --border-color: var(--dark-border-color);
}
</style>

<style scoped>
.dashboard-container {
  background: var(--bg-gradient);
  min-height: 100vh;
  width: 100%;
  color: var(--text-primary);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
}

/* 侧边栏样式 */
.sidebar {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-color);
  width: 280px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  transition: all 0.3s ease;
  position: fixed;
  height: 100vh;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 88px;
  padding: 24px 12px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
}

.logo img {
  width: 36px;
  height: 36px;
  filter: brightness(0) invert(1);
  transition: transform 0.3s ease;
}

.logo span {
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(to right, #ffffff, #E0E7FF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  border-radius: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, var(--primary), var(--primary-light));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-item:hover::before {
  opacity: 0.1;
}

.nav-item.active {
  color: var(--primary);
  background: linear-gradient(90deg, rgba(79, 70, 229, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%);
}

.nav-item.active::before {
  opacity: 0.15;
}

.nav-item i {
  font-size: 20px;
  z-index: 1;
}

.nav-item span {
  font-weight: 500;
  z-index: 1;
}

/* 主内容区样式 */
.main-content {
  margin-left: 280px;
  flex: 1;
  padding: 32px;
  transition: all 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 88px;
}

.main-header {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px 32px;
  margin-bottom: 32px;
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb h2 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(to right, var(--primary), var(--primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

/* 统计卡片样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-light-rgb), 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: 24px;
  position: relative;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
}

.stat-icon::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: inherit;
  border-radius: inherit;
  filter: blur(16px);
  opacity: 0.3;
  z-index: -1;
}

.stat-info h3 {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-info p {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  background: linear-gradient(to right, var(--primary), var(--primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary);
}

.stat-trend.positive {
  background: rgba(var(--secondary-rgb), 0.1);
  color: var(--secondary);
}

/* 活动列表样式 */
.recent-activities {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
}

.section-header {
  margin-bottom: 32px;
}

.section-header h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.activity-item {
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.activity-item:hover {
  transform: translateX(8px);
  background: rgba(var(--primary-rgb), 0.1);
}

/* 动画效果 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stats-grid {
  animation: slideUp 0.6s ease-out;
}

.recent-activities {
  animation: slideUp 0.8s ease-out;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.collapsed {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
}

/* 侧边栏折叠按钮样式 */
.collapse-btn {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: 2px solid rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.collapse-btn::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  opacity: 0.3;
  z-index: -1;
  transition: opacity 0.3s ease;
}

.collapse-btn::after {
  content: '收起侧边栏';
  position: absolute;
  right: 50px;
  background: var(--card-bg);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
}

.sidebar.collapsed .collapse-btn {
  right: -20px;
  transform: translateY(-50%) rotate(180deg);
}

.sidebar.collapsed .collapse-btn::after {
  content: '展开侧边栏';
  right: auto;
  left: 50px;
  transform: translateX(10px) rotate(180deg);
}

.collapse-btn:hover::after {
  opacity: 1;
  transform: translateX(0);
}

.sidebar.collapsed .collapse-btn:hover::after {
  transform: translateX(0) rotate(180deg);
}

.collapse-btn:hover {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.4);
}

.sidebar.collapsed .collapse-btn:hover {
  transform: translateY(-50%) scale(1.1) rotate(180deg);
}

.collapse-btn i {
  font-size: 18px;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.9);
}

.collapse-btn:hover i {
  animation: pulseScale 1s infinite;
  color: white;
}

@keyframes pulseScale {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .collapse-btn {
    right: -28px;
    width: 36px;
    height: 36px;
  }
  
  .collapse-btn::after {
    display: none;
  }
  
  .sidebar.collapsed .collapse-btn {
    right: -28px;
  }
}

/* 主题切换按钮样式 */
.theme-toggle {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
  overflow: visible;
}

.theme-toggle::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border-radius: inherit;
  opacity: 0.5;
  z-index: -1;
  transition: all 0.3s ease;
}

.theme-toggle::after {
  content: '切换到夜间模式';
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--card-bg);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  opacity: 0;
  transition: all 0.3s ease;
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dark .theme-toggle::after {
  content: '切换到日间模式';
}

.theme-toggle:hover::after {
  opacity: 1;
  transform: translateX(-50%) translateY(-5px);
}

.theme-toggle:hover {
  transform: translateX(-50%) scale(1.1);
  box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.4);
}

.theme-toggle i {
  font-size: 24px;
  transition: all 0.3s ease;
}

.theme-toggle:hover i {
  animation: spin 2s linear infinite;
}

.dark .theme-toggle {
  background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
}

.dark .theme-toggle::before {
  background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .collapse-btn {
    right: -28px;
    width: 36px;
    height: 36px;
  }
  
  .theme-toggle {
    bottom: 24px;
    width: 42px;
    height: 42px;
  }
}

/* 个人资料页面样式 */
.profile-view {
  animation: slideUp 0.6s ease-out;
}

.profile-card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
  margin-bottom: 32px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border-color);
  position: relative;
}

.avatar-container {
  position: relative;
}

.avatar-container .el-avatar {
  border: 4px solid rgba(var(--primary-rgb), 0.1);
  box-shadow: 0 8px 16px rgba(var(--primary-rgb), 0.15);
  transition: all 0.3s ease;
}

.avatar-container .el-avatar:hover {
  transform: scale(1.05) rotate(5deg);
}

.profile-info {
  flex: 1;
}

.profile-info h2 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(to right, var(--primary), var(--primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.profile-info p {
  color: var(--text-secondary);
  font-size: 16px;
}

.profile-header .el-button {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.profile-header .el-button:hover {
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}

.profile-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 32px;
}

.info-group {
  padding: 20px;
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.info-group::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-light-rgb), 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.info-group:hover::before {
  opacity: 1;
}

.info-group:hover {
  background: rgba(var(--primary-rgb), 0.1);
  transform: translateY(-5px);
}

.info-group label {
  display: block;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 12px;
  font-weight: 500;
}

.info-group span {
  display: block;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.info-group .el-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.info-group .el-tag.el-tag--danger {
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.info-group .el-tag.el-tag--success {
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.info-group .el-tag i {
  font-size: 14px;
}

.info-group .el-tag.el-tag--danger:hover {
  background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.3);
  transform: translateY(-2px);
}

.info-group .el-tag.el-tag--success:hover {
  background: linear-gradient(135deg, #059669 0%, #10B981 100%);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
  transform: translateY(-2px);
}

/* 安全设置部分 */
.security-section {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
}

.security-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 24px;
}

.security-card {
  padding: 24px;
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.security-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-light-rgb), 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.security-card:hover {
  transform: translateY(-5px);
}

.security-card:hover::before {
  opacity: 1;
}

.security-card i {
  font-size: 24px;
  color: var(--primary);
  padding: 12px;
  background: rgba(var(--primary-rgb), 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.security-card:hover i {
  transform: scale(1.1);
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
}

.security-info {
  flex: 1;
}

.security-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.security-info p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.security-card .el-button {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: 500;
  color: var(--primary);
  transition: all 0.3s ease;
}

.security-card .el-button:hover {
  color: var(--primary-light);
  transform: translateY(-50%) scale(1.05);
}

@media (max-width: 1024px) {
  .security-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .profile-details {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .security-cards {
    grid-template-columns: 1fr;
  }
  
  .profile-details {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .profile-header .el-button {
    position: static;
    transform: none;
    margin-top: 16px;
  }
  
  .profile-header .el-button:hover {
    transform: scale(1.05);
  }
}

.user-profile-mini {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.user-profile-mini::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-light-rgb), 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.user-profile-mini:hover::before {
  opacity: 1;
}

.user-profile-mini .el-avatar {
  border: 2px solid rgba(var(--primary-rgb), 0.2);
  transition: all 0.3s ease;
}

.user-profile-mini:hover .el-avatar {
  transform: scale(1.05);
  border-color: var(--primary);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info p {
  font-size: 14px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--danger);
  cursor: pointer;
  border-radius: 14px;
  transition: all 0.3s ease;
  background: rgba(239, 68, 68, 0.05);
  margin-bottom: 80px;
}

.sidebar-footer i {
  font-size: 20px;
  transition: transform 0.3s ease;
}

.sidebar-footer span {
  font-size: 15px;
  font-weight: 500;
}

.sidebar-footer:hover {
  background: rgba(239, 68, 68, 0.1);
  transform: translateX(4px);
}

.sidebar-footer:hover i {
  transform: rotate(90deg);
}

.sidebar.collapsed .sidebar-footer {
  padding: 16px 0;
  justify-content: center;
}

.sidebar.collapsed .user-profile-mini {
  padding: 12px;
  justify-content: center;
}

.sidebar.collapsed .user-profile-mini .el-avatar {
  width: 36px;
  height: 36px;
}

@media (max-width: 768px) {
  .user-profile-mini {
    padding: 12px;
  }
  
 .sidebar-footer {
    margin-bottom: 60px;
  }
}

/* 第三方账号绑定区块样式 */
.connect-section {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid var(--border-color);
  margin-top: 32px;
}

.connect-section .section-header {
  margin-bottom: 24px;
}

.connect-section .section-header h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.connect-section .section-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.connect-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.connect-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.connect-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-light-rgb), 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.connect-card:hover::before {
  opacity: 1;
}

.connect-card.is-bound {
  background: rgba(var(--secondary-rgb), 0.05);
}

.connect-card.is-bound::before {
  background: linear-gradient(135deg, 
    rgba(16, 185, 129, 0.1) 0%,
    rgba(52, 211, 153, 0.1) 100%
  );
}

.connect-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.connect-card.is-bound .connect-icon {
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
}

.connect-icon i {
  font-size: 24px;
  color: white;
}

.connect-info {
  flex: 1;
  min-width: 0;
}

.connect-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.connect-info p {
  font-size: 14px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connect-btn {
  padding: 8px 16px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.2);
  position: relative;
  overflow: hidden;
}

.connect-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.connect-btn.is-bound {
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.connect-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.3);
}

.connect-btn:hover::before {
  opacity: 1;
}

.connect-btn.is-bound:hover {
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.3);
}

.connect-btn i {
  font-size: 16px;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 1;
}

.connect-btn:hover i {
  transform: rotate(90deg);
}

.connect-btn span {
  font-size: 14px;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .connect-cards {
    grid-template-columns: 1fr;
  }
  
  .connect-card {
    padding: 20px;
  }
  
  .connect-icon {
    width: 40px;
    height: 40px;
  }
  
  .connect-icon i {
    font-size: 20px;
  }
  
  .connect-btn {
    padding: 6px 12px;
  }
  
  .connect-btn i {
    font-size: 14px;
  }
  
  .connect-btn span {
    font-size: 12px;
  }
}

/* 头像上传相关样式 */
.change-avatar-btn {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  color: white;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}

.avatar-container:hover .change-avatar-btn {
  opacity: 1;
  bottom: -5px;
}

.change-avatar-btn:hover {
  transform: translateX(-50%) scale(1.05);
}

.avatar-upload {
  text-align: center;
  padding: 20px 0;
}

.file-input {
  display: none;
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  background: transparent;
  color: #606266;
}

.btn-upload:hover {
  border-color: #409eff;
  color: #409eff;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.upload-preview {
  margin: 16px 0;
}

.preview-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 4px;
}

.icon-upload::before {
  content: "📤";
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.bind-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
}

.input-field {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin: 12px 0;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel, .btn-confirm {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-cancel {
  background: #f4f4f5;
  color: #606266;
}

.btn-confirm {
  background: #409eff;
  color: white;
}

.btn-cancel:hover {
  background: #e9e9eb;
}

.btn-confirm:hover {
  background: #66b1ff;
}

.icon-gamepad::before {
  content: "🎮";
}

.icon-close::before {
  content: "✖";
}

.icon-link::before {
  content: "🔗";
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.back-home-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
  color: white;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.2);
}

.back-home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.3);
}

.back-home-btn i {
  font-size: 16px;
}

.admin-view {
  animation: slideUp 0.6s ease-out;
}

.admin-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.stat-card h3 {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.stat-card p {
  margin: 10px 0 0;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.admin-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.admin-section h2 {
  margin: 0 0 20px;
  color: #333;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.admin-table th {
  background: #f5f5f5;
  font-weight: 600;
  color: #333;
}

.admin-table tr:hover {
  background: #f9f9f9;
}

.btn-warning {
  background: #ffa500;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 8px;
  font-size: 14px;
}

button:hover {
  opacity: 0.9;
}

.write-article-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.el-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.el-tag.el-tag--danger {
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.el-tag.el-tag--success {
  background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.el-tag i {
  font-size: 14px;
}

.report-tabs { display: flex; gap: 16px; margin-bottom: 20px; }
.report-tabs button { padding: 8px 24px; border: none; border-radius: 8px; background: #f3f4f6; color: #EF4444; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.report-tabs button.active { background: #EF4444; color: #fff; }
.report-table-container { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(239,68,68,0.08); padding: 24px; }
.report-table { width: 100%; border-collapse: collapse; }
.report-table th, .report-table td { padding: 12px 16px; text-align: left; }
.report-table th { background: #f3f4f6; color: #EF4444; font-weight: 700; }
.report-table tr { transition: background 0.2s; }

.report-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.report-actions .el-button {
  min-width: 100px;
}

.report-actions .el-button--danger {
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  border: none;
}

.report-actions .el-button--warning {
  background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
  border: none;
  color: white;
}

.report-actions .el-button--primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
}

.report-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style> 