<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="dashboard-header-content">
        <div class="user-welcome">
          <h1>欢迎回来, {{ nickname }}</h1>
          <p class="last-login">上次登录: {{ lastLoginTime }}</p>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <i class="el-icon-switch-button"></i>
          退出登录
        </button>
      </div>
    </header>

    <main class="dashboard-main">
      <div class="dashboard-content">
        <section class="info-card user-profile">
          <div class="profile-sidebar">
            <div class="avatar-wrapper">
              <el-avatar :size="120" :src="avatarUrl">
                {{ nickname?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <h2>{{ nickname }}</h2>
              <p class="user-role">普通用户</p>
              <div class="profile-actions">
                <button class="action-btn" @click="heyboxDialogVisible = true">
                  <i class="el-icon-link"></i>
                  绑定小黑盒
                </button>
                <button class="action-btn">
                  <i class="el-icon-picture"></i>
                  更换头像
                </button>
              </div>
            </div>
            
            <div class="quick-stats">
              <div class="stat-item">
                <span class="stat-label">注册天数</span>
                <span class="stat-value">{{ daysSinceRegistration }}天</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">账号状态</span>
                <el-tag size="small" type="success">正常</el-tag>
              </div>
            </div>
          </div>

          <div class="profile-main">
            <div class="section-title">
              <h3>基本信息</h3>
              <el-button type="primary" size="small">编辑资料</el-button>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <label>用户名</label>
                <span>{{ username }}</span>
              </div>
              <div class="info-item">
                <label>昵称</label>
                <span>{{ nickname }}</span>
              </div>
              <div class="info-item">
                <label>注册时间</label>
                <span>{{ registrationDate }}</span>
              </div>
              <div class="info-item">
                <label>邮箱</label>
                <span>未绑定</span>
              </div>
              <div class="info-item">
                <label>手机号</label>
                <span>未绑定</span>
              </div>
            </div>

            <div class="section-title">
              <h3>账号安全</h3>
            </div>

            <div class="security-section">
              <div class="security-card">
                <i class="el-icon-lock security-icon"></i>
                <div class="security-info">
                  <h4>修改密码</h4>
                  <p>定期更换密码以保护账号安全</p>
                </div>
              </div>
              <div class="security-card">
                <i class="el-icon-mobile-phone security-icon"></i>
                <div class="security-info">
                  <h4>绑定手机</h4>
                  <p>绑定手机号获得额外安全保障</p>
                </div>
              </div>
              <div class="security-card">
                <i class="el-icon-message security-icon"></i>
                <div class="security-info">
                  <h4>绑定邮箱</h4>
                  <p>绑定邮箱接收重要通知</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="info-card">
          <div class="section-title">
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
                {{ activity.content }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </section>
      </div>
    </main>

    <!-- 绑定小黑盒对话框 -->
    <el-dialog
      v-model="heyboxDialogVisible"
      title="绑定小黑盒账号"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

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

const recentActivities = ref([])

// 获取用户活动记录
const fetchUserActivities = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/user/activities', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      recentActivities.value = response.data.data.map(activity => ({
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
      if (userData.heybox_avatar) {
        avatarUrl.value = userData.heybox_avatar
      }
      if (userData.heybox_nickname) {
        nickname.value = userData.heybox_nickname
      }
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
    // 设置头像
    if (userData.heybox_avatar) {
      avatarUrl.value = userData.heybox_avatar
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
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  width: 100%;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.dashboard-header {
  background: white;
  padding: 20px 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
}

.dashboard-header-content {
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-main {
  flex: 1;
  max-width: 1920px;
  width: 100%;
  margin: 0 auto;
  padding: 40px;
  box-sizing: border-box;
  overflow-x: hidden;

}

.dashboard-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 32px;
}

.info-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.user-profile {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 40px;
}

.profile-sidebar {
  background: #f8fafc;
  border-radius: 12px;
  padding: 32px;
  height: fit-content;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.info-item {
  background: #f9fafb;
  padding: 24px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.security-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-top: 32px;
}

.security-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.security-card:hover {
  background: #4f46e5;
  color: white;
  transform: translateY(-2px);
}

.security-icon {
  font-size: 24px;
  color: #4f46e5;
}

.security-card:hover .security-icon {
  color: white;
}

.activity-timeline {
  margin-top: 32px;
}

/* 大屏幕优化 */
@media (min-width: 1600px) {
  .dashboard-main {
    padding: 60px;
  }
  
  .dashboard-content {
    grid-template-columns: 2fr 1fr;
  }
  
  .user-profile {
    grid-column: 1 / -1;
  }
}

/* 平板电脑 */
@media (max-width: 1200px) {
  .user-profile {
    grid-template-columns: 1fr;
  }
  
  .profile-sidebar {
    padding: 24px;
  }
  
  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

/* 移动设备 */
@media (max-width: 768px) {
  .dashboard-main {
    padding: 20px;
  }
  
  .dashboard-header {
    padding: 16px;
  }
  
  .dashboard-header-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .security-section {
    grid-template-columns: 1fr;
  }
}

.user-welcome h1 {
  font-size: 24px;
  color: #1f2937;
  margin: 0;
}

.last-login {
  color: #6b7280;
  font-size: 14px;
  margin: 4px 0 0 0;
}

.logout-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #dc2626;
}

.avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.avatar-wrapper h2 {
  margin: 16px 0 4px 0;
  font-size: 20px;
  color: #1f2937;
}

.user-role {
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.profile-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  width: 100%;
}

.action-btn {
  flex: 1;
  background: none;
  border: 2px solid #e5e7eb;
  padding: 8px 16px;
  border-radius: 6px;
  color: #4f46e5;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.action-btn:hover {
  background: #4f46e5;
  color: white;
}

.bind-heybox-form {
  padding: 0 20px;
}

.bind-desc {
  margin: 0 0 12px;
  color: #374151;
}

.bind-example {
  margin: 4px 0;
  color: #6b7280;
  font-size: 13px;
  font-family: monospace;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
}

.quick-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.stat-label {
  color: #6b7280;
  font-size: 14px;
}

.stat-value {
  color: #1f2937;
  font-weight: 500;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  color: #6b7280;
  font-size: 14px;
}

.info-item span {
  color: #1f2937;
  font-size: 15px;
  font-weight: 500;
}

.security-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.security-info h4 {
  margin: 0;
  font-size: 15px;
  color: inherit;
}

.security-info p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.security-card:hover .security-info p {
  color: #e5e7eb;
}

.activity-timeline {
  padding: 0 16px;
}

:deep(.el-timeline-item__content) {
  font-size: 14px;
}

:deep(.el-timeline-item__timestamp) {
  font-size: 13px;
}
</style> 