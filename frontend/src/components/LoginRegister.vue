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
              @click="activeTab = 'login'"
            >
              <i class="el-icon-user"></i>
              登录
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'register' }" 
              @click="activeTab = 'register'"
            >
              <i class="el-icon-plus"></i>
              注册
            </button>
          </div>

          <div class="form-container" :class="{ 'slide-left': activeTab === 'login', 'slide-right': activeTab === 'register' }">
            <!-- 登录表单 -->
            <form v-show="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
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
            <form v-show="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
              <div class="form-group">
                <label for="register-username">
                  <i class="el-icon-user"></i>
                  用户名
                </label>
                <input 
                  id="register-username"
                  type="text" 
                  v-model="registerForm.username" 
                  placeholder="3-20个字符"
                  @blur="validateField('register', 'username')"
                >
                <span class="error-message" v-if="registerErrors.username">{{ registerErrors.username }}</span>
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

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: ''
})

const loginErrors = reactive({
  username: '',
  password: ''
})

const registerErrors = reactive({
  username: '',
  password: ''
})

const validateField = (formType, field) => {
  const form = formType === 'login' ? loginForm : registerForm
  const errors = formType === 'login' ? loginErrors : registerErrors

  errors[field] = ''

  if (!form[field]) {
    errors[field] = `请输入${field === 'username' ? '用户名' : '密码'}`
    return false
  }

  if (field === 'username' && (form[field].length < 3 || form[field].length > 20)) {
    errors[field] = '用户名长度在 3 到 20 个字符'
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
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-content {
  width: 100%;
  max-width: 1000px;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.brand-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 40px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
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
}

.form-section {
  padding: 40px;
  background: white;
}

.form-card {
  max-width: 400px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 32px;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 16px;
}

.tab-btn {
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 16px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.tab-btn i {
  font-size: 18px;
}

.tab-btn.active {
  color: #4f46e5;
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -18px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #4f46e5;
  border-radius: 2px;
}

.form-container {
  position: relative;
  transition: all 0.3s ease-in-out;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group label i {
  color: #6b7280;
  font-size: 16px;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  width: 100%;
}

.form-group input:focus {
  border-color: #4f46e5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
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
  background: #4f46e5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover {
  background: #4338ca;
  transform: translateY(-1px);
}

.submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.submit-btn i {
  font-size: 18px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth-content {
    grid-template-columns: 1fr;
  }

  .brand-section {
    padding: 40px 20px;
    text-align: center;
  }

  .form-section {
    padding: 30px 20px;
  }

  .form-card {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .login-register-container {
    padding: 0;
  }

  .auth-content {
    border-radius: 0;
    min-height: 100vh;
  }

  .tabs {
    gap: 10px;
  }

  .tab-btn {
    padding: 8px 12px;
    font-size: 14px;
  }

  .form-options {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>