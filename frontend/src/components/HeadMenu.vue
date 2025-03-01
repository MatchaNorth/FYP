<template>
  <nav class="head-menu">
    <div class="menu-container">
      <div class="menu-left">
        <router-link to="/" class="logo">
          <i class="icon-gamepad"></i>
          <span class="logo-text">游戏文章</span>
        </router-link>
        <div class="nav-links">
          <router-link to="/home" class="nav-link">
            <i class="icon-home"></i>
            发现
          </router-link>
          <router-link to="/articles" class="nav-link">
            <i class="icon-edit"></i>
            创作文章
          </router-link>
          <router-link to="/dashboard" class="nav-link">
            <i class="icon-articles"></i>
            我的文章
          </router-link>
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
                <i class="icon-dashboard"></i>
                个人中心
              </router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item" @click="handleLogout">
                <i class="icon-logout"></i>
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
  background: rgba(var(--card-bg-rgb), 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
}

.menu-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 60px;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

.logo i {
  font-size: 24px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
}

.nav-link i {
  font-size: 18px;
}

.nav-link:hover {
  color: var(--primary);
  background: rgba(var(--primary-rgb), 0.1);
}

.nav-link.router-link-active {
  color: var(--primary);
  background: rgba(var(--primary-rgb), 0.15);
  font-weight: 500;
}

.menu-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.auth-btn {
  padding: 8px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
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
}

.auth-btn.register:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}

.user-info {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(var(--primary-rgb), 0.2);
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.username {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 180px;
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
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
  gap: 8px;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.3s ease;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 14px;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--primary);
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 4px 0;
}

.icon-gamepad::before {
  content: "🎮";
}

.icon-home::before {
  content: "🏠";
}

.icon-edit::before {
  content: "✏️";
}

.icon-articles::before {
  content: "📚";
}

.icon-dashboard::before {
  content: "🎛️";
}

.icon-logout::before {
  content: "🚪";
}

/* 响应式布局 */
@media (max-width: 1440px) {
  .menu-container {
    padding: 0 40px;
  }
}

@media (max-width: 1024px) {
  .nav-link span {
    display: none;
  }
  
  .nav-link {
    padding: 8px;
  }
  
  .nav-links {
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .menu-container {
    padding: 0 20px;
  }
  
  .logo-text {
    display: none;
  }
  
  .menu-left {
    gap: 24px;
  }
  
  .username {
    display: none;
  }
}
</style> 