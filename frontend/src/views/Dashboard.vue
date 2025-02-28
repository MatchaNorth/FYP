<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <img src="@/assets/logo.png" alt="Logo" />
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
            <p>普通用户</p>
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
        </nav>
      </div>
      
      <div class="sidebar-footer" @click="handleLogout">
        <i class="el-icon-switch-button"></i>
        <span v-show="!isSidebarCollapsed">退出登录</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="main-header">
        <div class="breadcrumb">
          <h2>{{ viewTitles[currentView] }}</h2>
          <p>{{ new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
        </div>
        <div class="header-actions">
          <button 
            class="action-btn" 
            :class="{ 'bound': isHeyboxBound }"
            @click="handleHeyboxAction"
            @mouseenter="showUnbindText = true"
            @mouseleave="showUnbindText = false"
          >
            <i :class="isHeyboxBound ? 'el-icon-user' : 'el-icon-link'"></i>
            <span v-if="isHeyboxBound">
              {{ showUnbindText ? '解绑账号' : `ID: ${heyboxId}` }}
            </span>
            <span v-else>绑定小黑盒</span>
          </button>
        </div>
      </div>

      <div class="view-container">
        <!-- 总览页面 -->
        <div v-if="currentView === 'overview'" class="overview-view" :class="{ 'fade-enter': viewTransition }">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon"><i class="el-icon-document"></i></div>
              <div class="stat-info">
                <h3>文章总数</h3>
                <p>{{ articleStats.total || 0 }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="el-icon-view"></i></div>
              <div class="stat-info">
                <h3>总阅读量</h3>
                <p>{{ articleStats.views || 0 }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="el-icon-time"></i></div>
              <div class="stat-info">
                <h3>注册天数</h3>
                <p>{{ daysSinceRegistration }}天</p>
              </div>
            </div>
          </div>

          <div class="recent-activities">
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
              <el-avatar :size="100" :src="avatarUrl">
                {{ nickname?.charAt(0)?.toUpperCase() }}
              </el-avatar>
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
                <el-tag size="small" type="success">正常</el-tag>
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
        </div>
      </div>
    </div>
  </div>

  <!-- 弹窗组件保持不变 -->
  <el-dialog v-model="heyboxDialogVisible" title="绑定小黑盒账号" width="500px">
    <div class="bind-heybox-form">
      <p class="bind-desc">请输入您的小黑盒个人主页链接，例如：</p>
      <p class="bind-example">https://www.xiaoheihe.cn/app/user/profile/19453679</p>
      <p class="bind-example">https://web.xiaoheihe.cn/bbs/user_profile_share?user_id=19453679</p>
      <el-input
        v-model="heyboxProfileUrl"
        placeholder="请输入小黑盒个人主页链接"
        clearable
      />
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="heyboxDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleBindHeybox"
          :loading="isBinding"
        >
          绑定
        </el-button>
      </span>
    </template>
  </el-dialog>

  <el-dialog v-model="editProfileDialogVisible" title="编辑个人资料" width="500px">
    <div class="edit-profile-form">
      <el-form :model="editProfileForm" label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editProfileForm.nickname" placeholder="请输入新的昵称" />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editProfileDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleUpdateProfile"
          :loading="isUpdating"
        >
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ArticleManager from './ArticleManager.vue'

const router = useRouter()
const username = ref('')
const nickname = ref('')
const registrationDate = ref('')
const lastLoginTime = ref('首次登录')
const avatarUrl = ref('')
const daysSinceRegistration = ref(0)
const heyboxDialogVisible = ref(false)
const heyboxProfileUrl = ref('')
const isBinding = ref(false)
const editProfileDialogVisible = ref(false)
const editProfileForm = ref({
  nickname: ''
})
const isUpdating = ref(false)
const heyboxId = ref('')
const isHeyboxBound = ref(false)
const showUnbindText = ref(false)

const recentActivities = ref([])

// 新增的响应式数据
const isSidebarCollapsed = ref(false)
const currentView = ref('overview')
const viewTransition = ref(false)
const articleStats = ref({
  total: 0,
  views: 0
})

const viewTitles = {
  overview: '总览',
  articles: '文章管理',
  profile: '个人资料'
}

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

// 检查登录状态
onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  
  // 获取用户详细信息
  axios.get('http://localhost:5000/api/user/profile', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(response => {
    const userData = response.data.data
    username.value = userData.username
    nickname.value = userData.nickname || userData.username
    // 设置头像和小黑盒信息
    if (userData.heybox_avatar) {
      avatarUrl.value = userData.heybox_avatar
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
    
    // 获取用户活动记录
    fetchUserActivities()
  })
  .catch(error => {
    console.error('获取用户信息失败:', error)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
  })
})

// 打开编辑资料对话框时，初始化表单数据
watch(editProfileDialogVisible, (newVal) => {
  if (newVal) {
    editProfileForm.value.nickname = nickname.value
  }
})

// 更新用户资料
const handleUpdateProfile = async () => {
  try {
    isUpdating.value = true
    const token = localStorage.getItem('token')
    const response = await axios.put(
      'http://localhost:5000/api/user/profile',
      editProfileForm.value,
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

// 在 onMounted 中添加获取文章统计信息
onMounted(async () => {
  // ... 原有的 onMounted 逻辑 ...
  
  // 获取文章统计信息
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/articles/stats', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.data.code === 200) {
      articleStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取文章统计信息失败:', error)
  }
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.sidebar {
  width: 260px;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: fixed;
  height: 100vh;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(to right, #2563eb, #3b82f6);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo img {
  width: 32px;
  height: 32px;
  filter: brightness(0) invert(1);
}

.logo span {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
}

.collapse-btn {
  background: none;
  border: none;
  color: #ffffff;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

.user-profile-mini {
  padding: 20px 24px;
  margin: 20px 0;
  background-color: #f8fafc;
  border-radius: 12px;
  margin: 20px;
}

.user-info h3 {
  margin: 0;
  font-size: 14px;
  color: #0f172a;
}

.user-info p {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #64748b;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  padding: 14px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  margin: 4px 0;
}

.nav-item:hover {
  background-color: #f1f5f9;
  color: #2563eb;
}

.nav-item.active {
  background-color: #eff6ff;
  color: #2563eb;
  border-left-color: #2563eb;
  font-weight: 500;
}

.nav-item.collapsed {
  justify-content: center;
  padding: 12px;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #e2e8f0;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sidebar-footer:hover {
  background-color: #fef2f2;
}

.main-content {
  margin-left: 260px;
  flex: 1;
  padding: 0;
  transition: all 0.3s ease;
  min-width: 1000px;
}

.main-content.sidebar-collapsed {
  margin-left: 80px;
}

.main-header {
  height: 64px;
  background-color: #ffffff;
  padding: 0 40px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.breadcrumb h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
  font-weight: 600;
}

.breadcrumb p {
  margin: 4px 0 0 0;
  color: #64748b;
  font-size: 14px;
}

.view-container {
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.stat-info h3 {
  margin: 0;
  font-size: 15px;
  color: #64748b;
  font-weight: 500;
}

.stat-info p {
  margin: 8px 0 0 0;
  font-size: 28px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.recent-activities {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.section-header {
  margin-bottom: 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 20px;
  color: #0f172a;
  font-weight: 600;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: #ffffff;
  border-radius: 12px;
  margin-bottom: 16px;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.activity-item:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
  transform: translateX(5px);
}

.profile-card {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.profile-info h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
}

.profile-info p {
  margin: 4px 0 0 0;
  color: #64748b;
}

.profile-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-group label {
  font-size: 14px;
  color: #64748b;
}

.info-group span {
  font-size: 16px;
  color: #0f172a;
}

.security-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.security-card {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.security-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.security-card i {
  font-size: 24px;
  color: #2563eb;
}

.security-info {
  flex: 1;
}

.security-info h4 {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
}

.security-info p {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #64748b;
}

.action-btn {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 10px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.action-btn:hover {
  background-color: #f8fafc;
  border-color: #2563eb;
  color: #2563eb;
}

.action-btn.bound {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
  color: #16a34a;
}

.action-btn.bound:hover {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #ef4444;
}

:deep(.el-timeline-item__node) {
  background-color: #2563eb;
  border-color: #2563eb;
}

:deep(.el-timeline-item__tail) {
  border-left-color: #e2e8f0;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}

:deep(.el-timeline-item__timestamp) {
  color: #64748b;
  font-size: 13px;
}

.fade-enter {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
</style> 