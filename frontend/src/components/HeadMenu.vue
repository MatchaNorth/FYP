<template>
  <nav class="head-menu">
    <div class="menu-container">
      <div class="menu-left">
        <router-link to="/" class="logo">
          <el-icon class="logo-icon"><VideoPlay /></el-icon>
          <span class="logo-text">游戏文章</span>
        </router-link>
        <div class="nav-links">
          <router-link to="/home" class="nav-link">
            <el-icon><HomeFilled /></el-icon>
            发现
          </router-link>
          <template v-if="isLoggedIn">
            <router-link to="/articles" class="nav-link">
              <el-icon><EditPen /></el-icon>
              创作文章
            </router-link>
            <router-link to="/dashboard" class="nav-link">
              <el-icon><Document /></el-icon>
              我的文章
            </router-link>
          </template>
        </div>
      </div>
      
      <div class="menu-right">
        <template v-if="isLoggedIn">
          <div class="user-info" @click="showUserMenu = !showUserMenu">
            <img v-if="userAvatar" :src="userAvatar" class="avatar" alt="用户头像">
            <span v-else class="avatar-placeholder">{{ userInitials }}</span>
            <span class="username">{{ nickname }}</span>
            
            <!-- 用户菜单下拉框 -->
            <div v-show="showUserMenu" class="user-dropdown">
              <router-link to="/dashboard" class="dropdown-item">
                <el-icon><User /></el-icon>
                个人中心
              </router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item" @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="auth-btn login">登录</router-link>
          <router-link to="/login?tab=register" class="auth-btn register">注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { HomeFilled, EditPen, Document, User, SwitchButton, VideoPlay } from '@element-plus/icons-vue'

const router = useRouter()
const showUserMenu = ref(false)
const userInfo = ref(null)

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const nickname = computed(() => userInfo.value?.nickname || '用户')
const userAvatar = computed(() => userInfo.value?.avatar || '')
const userInitials = computed(() => {
  const name = userInfo.value?.nickname || userInfo.value?.username || ''
  return name.slice(0, 2).toUpperCase()
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return
    
    const response = await axios.get('http://localhost:5000/api/user/profile', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      userInfo.value = response.data.data
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token')
  showUserMenu.value = false
  userInfo.value = null
  ElMessage.success('退出登录成功')
  router.push('/login')
}

// 点击其他地方关闭用户菜单
const handleClickOutside = (event) => {
  const userMenu = document.querySelector('.user-info')
  if (userMenu && !userMenu.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  fetchUserInfo()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.head-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(var(--card-bg-rgb), 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
}

.menu-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 48px;
}

.logo {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  padding: 8px 16px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.logo:hover {
  background: rgba(var(--primary-rgb), 0.1);
  transform: translateY(-1px);
}

.logo:hover .logo-icon {
  transform: scale(1.1) rotate(-10deg);
}

.logo .logo-icon {
  font-size: 28px;
  color: var(--primary);
  transition: all 0.3s ease;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 12px;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 14px;
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.nav-link .el-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.nav-link:hover {
  color: white;
}

.nav-link:hover::before {
  opacity: 1;
}

.nav-link:hover .el-icon {
  transform: scale(1.1);
}

.nav-link.router-link-active {
  color: white;
  font-weight: 600;
}

.nav-link.router-link-active::before {
  opacity: 1;
}

.menu-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.auth-btn {
  padding: 10px 24px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.auth-btn.login {
  color: var(--primary);
  background: rgba(var(--primary-rgb), 0.1);
}

.auth-btn.login:hover {
  background: rgba(var(--primary-rgb), 0.15);
  transform: translateY(-2px);
}

.auth-btn.register {
  color: white;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  box-shadow: 0 4px 15px rgba(var(--primary-rgb), 0.2);
}

.auth-btn.register:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-rgb), 0.3);
}

.user-info {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 20px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(var(--primary-rgb), 0.1);
}

.user-info:hover {
  background: rgba(var(--primary-rgb), 0.15);
  transform: translateY(-1px);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid rgba(var(--primary-rgb), 0.2);
}

.avatar-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.username {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 200px;
  background: var(--card-bg);
  border-radius: 16px;
  padding: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
  animation: dropdownFadeIn 0.2s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
  background: none;
  width: 100%;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary);
}

.dropdown-item .el-icon {
  font-size: 18px;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 8px 0;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .menu-container {
    padding: 0 20px;
  }

  .logo-text {
    display: none;
  }

  .nav-links {
    gap: 8px;
  }

  .nav-link {
    padding: 8px 12px;
  }

  .nav-link span {
    display: none;
  }

  .auth-btn {
    padding: 8px 16px;
  }

  .username {
    display: none;
  }
}
</style> 