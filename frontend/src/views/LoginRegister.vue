<template>
  <div class="login-register-container">
    <div class="auth-content">
      <div class="brand-section">
        <div class="brand-content">
          <h1 class="brand-title">欢迎使用</h1>
          <p class="brand-description">
            {{ activeTab === 'login' ? '登录您的账号以继续使用' : '创建一个新账号开始使用' }}
          </p>
        </div>
      </div>

      <div class="form-section">
        <div class="form-card">
          <div class="tabs">
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'login' }" 
              @click="switchTab('login')"
            >
              <i class="el-icon-user"></i>
              登录
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'register' }" 
              @click="switchTab('register')"
            >
              <i class="el-icon-plus"></i>
              注册
            </button>
          </div>

          <div class="form-container" :class="{ 'slide-left': activeTab === 'login', 'slide-right': activeTab === 'register' }">
            <!-- 登录表单 -->
            <form v-show="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form" :class="{ active: activeTab === 'login' }">
              <div class="form-group">
                <label for="login-username">
                  <i class="el-icon-user"></i>
                  用户名
                </label>
                <input 
                  id="login-username"
                  type="text" 
                  v-model="loginForm.username" 
                  placeholder="请输入用户名"
                  @blur="validateField('login', 'username')"
                >
                <span class="error-message" v-if="loginErrors.username">{{ loginErrors.username }}</span>
              </div>

              <div class="form-group">
                <label for="login-password">
                  <i class="el-icon-lock"></i>
                  密码
                </label>
                <div class="password-input">
                  <input 
                    id="login-password"
                    :type="showLoginPassword ? 'text' : 'password'"
                    v-model="loginForm.password" 
                    placeholder="请输入密码"
                    @blur="validateField('login', 'password')"
                  >
                  <button 
                    type="button"
                    class="toggle-password"
                    @click="showLoginPassword = !showLoginPassword"
                  >
                    <i :class="showLoginPassword ? 'el-icon-view' : 'el-icon-hide'"></i>
                  </button>
                </div>
                <span class="error-message" v-if="loginErrors.password">{{ loginErrors.password }}</span>
              </div>

              <div class="form-options">
                <label class="remember-me">
                  <input type="checkbox" v-model="rememberMe">
                  <span>记住我</span>
                </label>
                <a href="#" class="forgot-password">忘记密码？</a>
              </div>

              <button type="submit" class="submit-btn" :disabled="loading">
                <i class="el-icon-right" v-if="!loading"></i>
                <i class="el-icon-loading" v-else></i>
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </form>

            <!-- 注册表单 -->
            <form v-show="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form" :class="{ active: activeTab === 'register' }">
              <div class="form-group">
                <label for="register-username">
                  <i class="el-icon-user"></i>
                  用户名
                </label>
                <input 
                  id="register-username"
                  type="text" 
                  v-model="registerForm.username" 
                  placeholder="3-20个字符，用于登录"
                  @blur="validateField('register', 'username')"
                >
                <span class="error-message" v-if="registerErrors.username">{{ registerErrors.username }}</span>
              </div>

              <div class="form-group">
                <label for="register-nickname">
                  <i class="el-icon-user"></i>
                  昵称
                </label>
                <input 
                  id="register-nickname"
                  type="text" 
                  v-model="registerForm.nickname" 
                  placeholder="选填，2-20个字符，用于显示"
                  @blur="validateField('register', 'nickname')"
                >
                <span class="error-message" v-if="registerErrors.nickname">{{ registerErrors.nickname }}</span>
              </div>

              <div class="form-group">
                <label for="register-password">
                  <i class="el-icon-lock"></i>
                  密码
                </label>
                <div class="password-input">
                  <input 
                    id="register-password"
                    :type="showRegisterPassword ? 'text' : 'password'"
                    v-model="registerForm.password" 
                    placeholder="6-20个字符"
                    @blur="validateField('register', 'password')"
                  >
                  <button 
                    type="button"
                    class="toggle-password"
                    @click="showRegisterPassword = !showRegisterPassword"
                  >
                    <i :class="showRegisterPassword ? 'el-icon-view' : 'el-icon-hide'"></i>
                  </button>
                </div>
                <span class="error-message" v-if="registerErrors.password">{{ registerErrors.password }}</span>
              </div>

              <div class="form-agreement">
                <label class="agreement-checkbox">
                  <input type="checkbox" v-model="agreeToTerms">
                  <span>我已阅读并同意</span>
                </label>
                <a href="#" class="terms-link">服务条款</a>
              </div>

              <button type="submit" class="submit-btn" :disabled="loading || !agreeToTerms">
                <i class="el-icon-plus" v-if="!loading"></i>
                <i class="el-icon-loading" v-else></i>
                {{ loading ? '注册中...' : '注册' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const rememberMe = ref(false)
const agreeToTerms = ref(false)

const switchTab = (tab) => {
  if (activeTab.value === tab) return
  activeTab.value = tab
}

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  nickname: '',
  password: ''
})

const loginErrors = reactive({
  username: '',
  password: ''
})

const registerErrors = reactive({
  username: '',
  nickname: '',
  password: ''
})

const validateField = (formType, field) => {
  const form = formType === 'login' ? loginForm : registerForm
  const errors = formType === 'login' ? loginErrors : registerErrors

  errors[field] = ''

  if (field !== 'nickname' && !form[field]) {
    errors[field] = `请输入${field === 'username' ? '用户名' : '密码'}`
    return false
  }

  if (field === 'username' && (form[field].length < 3 || form[field].length > 20)) {
    errors[field] = '用户名长度在 3 到 20 个字符'
    return false
  }

  if (field === 'nickname' && form[field] && (form[field].length < 2 || form[field].length > 20)) {
    errors[field] = '昵称长度在 2 到 20 个字符'
    return false
  }

  if (field === 'password' && (form[field].length < 6 || form[field].length > 20)) {
    errors[field] = '密码长度在 6 到 20 个字符'
    return false
  }

  return true
}

const validateForm = (formType) => {
  const isUsernameValid = validateField(formType, 'username')
  const isPasswordValid = validateField(formType, 'password')
  return isUsernameValid && isPasswordValid
}

const handleLogin = async () => {
  if (!validateForm('login')) return

  loading.value = true
  try {
    const response = await axios.post('http://localhost:5000/api/auth/login', loginForm)
    const { token, username } = response.data
    ElMessage({
      message: '登录成功',
      type: 'success',
      duration: 2000,
      showClose: true,
      offset: 80
    })
    setTimeout(() => {
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      router.push('/dashboard')
    }, 500)
  } catch (error) {
    ElMessage({
      message: error.response?.data?.message || '登录失败',
      type: 'error',
      duration: 2000,
      showClose: true,
      offset: 80
    })
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!validateForm('register')) return

  loading.value = true
  try {
    const response = await axios.post('http://localhost:5000/api/auth/register', registerForm)
    ElMessage({
      message: '注册成功！请登录',
      type: 'success',
      duration: 2000,
      showClose: true,
      offset: 80
    })
    activeTab.value = 'login'
    registerForm.username = ''
    registerForm.nickname = ''
    registerForm.password = ''
  } catch (error) {
    ElMessage({
      message: error.response?.data?.message || '注册失败',
      type: 'error',
      duration: 2000,
      showClose: true,
      offset: 80
    })
  } finally {
    loading.value = false
  }
}
</script>

<style>
/* 全局消息样式 */
:root {
  --el-message-bg-color: rgba(255, 255, 255, 0.95);
  --el-message-border-color: #e4e7ed;
  --el-message-padding: 15px 20px;
  --el-message-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.el-message {
  border-radius: 8px !important;
  border: none !important;
  box-shadow: var(--el-message-shadow) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  transform-origin: top !important;
  animation: message-slide-down 0.3s ease-out !important;
}

.el-message--success {
  background: rgba(240, 255, 244, 0.95) !important;
  border-left: 4px solid #67c23a !important;
}

.el-message--error {
  background: rgba(255, 242, 242, 0.95) !important;
  border-left: 4px solid #f56c6c !important;
}

.el-message--warning {
  background: rgba(255, 247, 232, 0.95) !important;
  border-left: 4px solid #e6a23c !important;
}

.el-message--info {
  background: rgba(240, 247, 255, 0.95) !important;
  border-left: 4px solid #909399 !important;
}

.el-message__content {
  font-size: 14px !important;
  line-height: 1.4 !important;
}

.el-message .el-message__icon {
  font-size: 16px !important;
  margin-right: 8px !important;
}

.el-message .el-message__closeBtn {
  right: 12px !important;
  font-size: 14px !important;
  opacity: 0.7 !important;
  transition: opacity 0.3s !important;
}

.el-message .el-message__closeBtn:hover {
  opacity: 1 !important;
}

@keyframes message-slide-down {
  from {
    opacity: 0;
    transform: translateY(-100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 消息退出动画 */
.el-message.is-closing {
  animation: message-slide-up 0.3s ease-out !important;
}

@keyframes message-slide-up {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-100%);
  }
}
</style>

<style scoped>
.login-register-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    135deg,
    rgba(255, 182, 193, 0.4) 0%,
    rgba(173, 216, 230, 0.4) 50%,
    rgba(255, 255, 224, 0.4) 100%
  );
  padding: 20px;
  box-sizing: border-box;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

/* 添加漂浮的气泡效果 */
.login-register-container::before,
.login-register-container::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: linear-gradient(
    135deg,
    rgba(255, 182, 193, 0.3),
    rgba(173, 216, 230, 0.3)
  );
  animation: float 15s infinite ease-in-out;
}

.login-register-container::before {
  top: -150px;
  left: -150px;
}

.login-register-container::after {
  bottom: -150px;
  right: -150px;
  animation-delay: -7.5s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(50px, 50px) scale(1.1);
  }
  50% {
    transform: translate(0, 100px) scale(1);
  }
  75% {
    transform: translate(-50px, 50px) scale(0.9);
  }
}

.auth-content {
  width: 100%;
  max-width: 1000px;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: appear 0.6s ease-out;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes appear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-section {
  background: linear-gradient(135deg, rgba(255, 182, 193, 0.8) 0%, rgba(173, 216, 230, 0.8) 100%);
  padding: 60px 40px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.brand-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><path fill="%23FFFFFF" fill-opacity="0.05" d="M45,-78.1C58.3,-71.3,69.1,-58.9,76.8,-44.7C84.5,-30.5,89.2,-14.3,88.7,1.8C88.2,17.9,82.4,33.8,73.1,47.2C63.8,60.7,51,71.7,36.3,77.7C21.7,83.7,5.3,84.7,-11.4,83.1C-28.2,81.5,-45.3,77.3,-58.8,67.7C-72.3,58.2,-82.1,43.3,-86.9,27C-91.7,10.7,-91.5,-7,-85.8,-22.2C-80.1,-37.4,-69,-50.1,-55.6,-57C-42.1,-63.9,-26.4,-65,-11.2,-70.3C4,-75.6,19.1,-85,33.8,-83.8C48.5,-82.6,62.8,-70.9,45,-78.1Z" transform="translate(100 100)" /></svg>') no-repeat center center;
  background-size: 140%;
  opacity: 0.1;
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.brand-description {
  font-size: 16px;
  opacity: 0.9;
  line-height: 1.6;
  transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1),
              opacity 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.brand-description.slide-enter {
  opacity: 0;
  transform: translateY(20px);
}

.brand-description.slide-leave {
  opacity: 0;
  transform: translateY(-20px);
}

.form-section {
  padding: 40px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.form-card {
  max-width: 400px;
  margin: 0 auto;
  transition: height 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 32px;
  border-bottom: 2px solid rgba(229, 231, 235, 0.5);
  padding-bottom: 16px;
}

.tab-btn {
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 16px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.tab-btn::before {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(135deg, #ff69b4, #4f46e5);
  transform: scaleX(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-btn.active {
  color: #4f46e5;
  font-weight: 500;
}

.tab-btn.active::before {
  transform: scaleX(1);
}

.form-container {
  position: relative;
  min-height: 300px;
  height: auto;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.auth-form {
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: absolute;
  width: 100%;
  height: auto;
}

.auth-form.active {
  opacity: 1;
  transform: scale(1);
  position: relative;
}

/* 登录表单和注册表单的特定高度 */
.auth-form[v-show="activeTab === 'login'"] {
  min-height: 320px;
}

.auth-form[v-show="activeTab === 'register'"] {
  min-height: 420px;
}

/* 果冻效果的切换动画 */
.slide-left {
  transform: translateX(0) scale(1);
  animation: jellyLeft 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.slide-right {
  transform: translateX(0) scale(1);
  animation: jellyRight 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes jellyLeft {
  0% { transform: translateX(100%) scale(0.8); }
  40% { transform: translateX(0) scale(1.1); }
  70% { transform: translateX(0) scale(0.95); }
  100% { transform: translateX(0) scale(1); }
}

@keyframes jellyRight {
  0% { transform: translateX(-100%) scale(0.8); }
  40% { transform: translateX(0) scale(1.1); }
  70% { transform: translateX(0) scale(0.95); }
  100% { transform: translateX(0) scale(1); }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0;
  transform: translateY(20px);
  animation: formGroupEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes formGroupEnter {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-group:nth-child(1) { animation-delay: 0.1s; }
.form-group:nth-child(2) { animation-delay: 0.2s; }
.form-group:nth-child(3) { animation-delay: 0.3s; }

.form-group label {
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
              color 0.3s ease;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid rgba(229, 231, 235, 0.5);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  width: 100%;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  transform-origin: left;
}

.form-group input:focus {
  border-color: #4f46e5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
  background: rgba(255, 255, 255, 0.95);
  transform: scale(1.02);
}

.form-group input:focus + label {
  transform: translateY(-2px);
  color: #4f46e5;
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-password:hover {
  color: #4f46e5;
}

.error-message {
  color: #ef4444;
  font-size: 13px;
  margin-top: 4px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  opacity: 0;
  transform: translateY(20px);
  animation: fadeSlideUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
}

@keyframes fadeSlideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  cursor: pointer;
}

.forgot-password {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #4338ca;
}

.form-agreement {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #4b5563;
  opacity: 0;
  transform: translateY(20px);
  animation: fadeSlideUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards;
}

.terms-link {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.terms-link:hover {
  text-decoration: underline;
}

.submit-btn {
  background: linear-gradient(135deg, #ff69b4, #4f46e5);
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  background-size: 200% auto;
  transform-origin: center;
  opacity: 0;
  transform: translateY(20px);
  animation: buttonEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s forwards;
}

@keyframes buttonEnter {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.submit-btn:hover {
  background-position: right center;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
}

.submit-btn:active {
  transform: translateY(0) scale(0.98);
}

.submit-btn:disabled {
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计调整 */
@media (max-width: 768px) {
  .auth-content {
    grid-template-columns: 1fr;
  }

  .brand-section {
    padding: 40px 20px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .login-register-container {
    padding: 16px;
  }

  .auth-content {
    border-radius: 16px;
  }
}
</style>