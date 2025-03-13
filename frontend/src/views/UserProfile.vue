<template>
  <div class="user-profile-container" :class="{ 'dark': isDark }">
    <!-- 用户基本信息卡片 -->
    <div class="profile-hero glass-card">
      <div class="profile-cover">
        <div class="cover-overlay"></div>
      </div>
      <div class="profile-main">
        <div class="profile-avatar">
          <el-avatar :size="120" :src="userInfo.avatar" class="avatar-image">
            {{ userInfo.nickname?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="user-status" :class="{ 'online': userInfo.isOnline }">
            <span class="status-dot"></span>
            {{ userInfo.isOnline ? '在线' : '离线' }}
          </div>
        </div>
        <div class="profile-info">
          <h1>{{ userInfo.nickname }}</h1>
          <p class="user-bio">{{ userInfo.bio || '这个用户很懒，还没有写简介' }}</p>
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.articleCount }}</span>
              <span class="stat-label">文章</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.totalViews }}</span>
              <span class="stat-label">阅读量</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.likeCount }}</span>
              <span class="stat-label">获赞</span>
            </div>
          </div>
          <div class="user-badges">
            <el-tooltip 
              v-for="badge in userInfo.badges" 
              :key="badge.id"
              :content="badge.description"
              placement="top"
            >
              <div class="badge-item" :class="badge.type">
                <i :class="badge.icon"></i>
                <span>{{ badge.name }}</span>
              </div>
            </el-tooltip>
          </div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-grid">
      <!-- 左侧信息栏 -->
      <div class="left-sidebar">
        <div class="info-card glass-card">
          <h3><i class="el-icon-user"></i> 个人信息</h3>
          <div class="info-list">
            <div class="info-item">
              <i class="el-icon-date"></i>
              <span>加入时间：{{ formatDate(userInfo.joinDate) }}</span>
            </div>
            <div class="info-item">
              <i class="el-icon-medal"></i>
              <span>活跃等级：LV{{ userInfo.level }}</span>
            </div>
            <div class="info-item">
              <i class="el-icon-trophy"></i>
              <span>成就点数：{{ userInfo.achievementPoints }}</span>
            </div>
          </div>
        </div>

        <div class="game-tags glass-card">
          <h3><i class="el-icon-collection-tag"></i> 游戏标签</h3>
          <div class="tag-cloud">
            <el-tag
              v-for="tag in userInfo.gameTags"
              :key="tag.id"
              :type="tag.type"
              effect="dark"
              class="game-tag"
            >
              {{ tag.name }}
              <span class="tag-count">{{ tag.count }}</span>
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 主要内容区 -->
      <div class="main-content">
        <!-- 活跃度热力图 -->
        <div class="activity-heatmap glass-card">
          <h3><i class="el-icon-data-line"></i> 活跃度</h3>
          <div class="heatmap-container" ref="heatmapContainer"></div>
        </div>

        <!-- 最近发布的文章 -->
        <div class="recent-articles glass-card">
          <h3><i class="el-icon-document"></i> 最近发布</h3>
          <div class="article-list">
            <div 
              v-for="article in userInfo.recentArticles" 
              :key="article.id"
              class="article-card"
              @click="viewArticle(article.id)"
            >
              <div class="article-cover" :style="{ backgroundImage: `url(${article.cover})` }">
                <div class="article-meta">
                  <span class="article-date">
                    <i class="el-icon-time"></i> {{ formatDate(article.publishDate) }}
                  </span>
                  <span class="article-views">
                    <i class="el-icon-view"></i> {{ article.views }}
                  </span>
                </div>
              </div>
              <div class="article-info">
                <h4>{{ article.title }}</h4>
                <p>{{ article.summary }}</p>
                <div class="article-tags">
                  <el-tag 
                    v-for="tag in article.tags" 
                    :key="tag"
                    size="small"
                    effect="dark"
                    class="article-tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
          <div class="view-more" v-if="userInfo.articleCount > userInfo.recentArticles.length">
            <el-button type="primary" plain>查看更多文章</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isDark = ref(false)
const heatmapChart = ref(null)
const heatmapContainer = ref(null)

const userInfo = ref({
  id: '',
  nickname: '',
  avatar: '',
  bio: '',
  isOnline: false,
  articleCount: 0,
  totalViews: 0,
  likeCount: 0,
  joinDate: '',
  level: 1,
  achievementPoints: 0,
  badges: [],
  gameTags: [],
  recentArticles: [],
  activityData: []
})

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 查看文章详情
const viewArticle = (articleId) => {
  router.push(`/articles/public/${articleId}`)
}

// 初始化热力图
const initHeatmap = () => {
  if (!heatmapContainer.value) return

  heatmapChart.value = echarts.init(heatmapContainer.value)
  const option = {
    tooltip: {
      position: 'top',
      formatter: (params) => {
        return `${params.data[0]}: ${params.data[1]} 次活动`
      },
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      borderWidth: 0,
      textStyle: {
        color: '#fff'
      }
    },
    visualMap: {
      min: 0,
      max: 10,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%',
      textStyle: {
        color: '#888'
      },
      inRange: {
        color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
      }
    },
    calendar: {
      top: 'middle',
      left: 'center',
      orient: 'horizontal',
      range: new Date().getFullYear(),
      dayLabel: {
        firstDay: 1,
        nameMap: 'cn'
      },
      monthLabel: {
        nameMap: 'cn'
      },
      yearLabel: {
        show: false
      },
      itemStyle: {
        borderWidth: 0.5,
        borderColor: '#eee'
      }
    },
    series: [{
      type: 'heatmap',
      coordinateSystem: 'calendar',
      data: userInfo.value.activityData,
      label: {
        show: false
      }
    }]
  }

  heatmapChart.value.setOption(option)
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const userId = route.params.id
    const [profileResponse, activityResponse] = await Promise.all([
      axios.get(`http://localhost:5000/api/users/${userId}/profile`),
      axios.get(`http://localhost:5000/api/users/${userId}/activity`)
    ])
    
    if (profileResponse.data.code === 200) {
      userInfo.value = {
        ...profileResponse.data.data,
        activityData: activityResponse.data.code === 200 ? activityResponse.data.data : []
      }
      
      // 初始化热力图
      nextTick(() => {
        initHeatmap()
      })
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 监听窗口大小变化，重绘热力图
window.addEventListener('resize', () => {
  if (heatmapChart.value) {
    heatmapChart.value.resize()
  }
})

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
:root {
  --primary: #3b82f6;
  --primary-light: #60a5fa;
  --primary-dark: #2563eb;
  --primary-rgb: 59, 130, 246;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: rgba(229, 231, 235, 0.5);
  --card-bg: rgba(255, 255, 255, 0.8);
  --bg-gradient: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}

.dark {
  --text-primary: #f3f4f6;
  --text-secondary: #d1d5db;
  --border-color: rgba(75, 85, 99, 0.5);
  --card-bg: rgba(31, 41, 55, 0.8);
  --bg-gradient: linear-gradient(135deg, #111827 0%, #1f2937 100%);
}

.user-profile-container {
  padding: 0;
  min-height: 100vh;
  background: var(--bg-gradient);
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.profile-hero {
  position: relative;
  overflow: hidden;
  margin-bottom: 0;
  width: 100%;
  border-radius: 0;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.1),
    0 1px 1px rgba(255, 255, 255, 0.1);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.profile-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(
      circle at 0% 0%,
      rgba(var(--primary-rgb), 0.15) 0%,
      transparent 50%
    ),
    radial-gradient(
      circle at 100% 100%,
      rgba(var(--primary-rgb), 0.15) 0%,
      transparent 50%
    );
  opacity: 0.8;
  z-index: 0;
}

.profile-hero::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
}

.profile-cover {
  height: 360px;
  background: linear-gradient(
    135deg,
    rgba(var(--primary-rgb), 0.7) 0%,
    rgba(var(--primary-rgb), 0.3) 100%
  );
  position: relative;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.profile-cover::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(
      circle at 50% 50%,
      rgba(255, 255, 255, 0.2) 0%,
      transparent 70%
    ),
    repeating-linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.1) 1px,
      transparent 1px,
      transparent 8px
    );
  opacity: 0.8;
  mix-blend-mode: overlay;
  animation: backgroundShift 20s linear infinite;
}

@keyframes backgroundShift {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 100% 100%;
  }
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(0, 0, 0, 0.3) 50%,
    rgba(0, 0, 0, 0.6) 100%
  );
  backdrop-filter: blur(3px);
}

.profile-main {
  padding: 0 48px;
  margin-top: -120px;
  position: relative;
  z-index: 1;
  display: flex;
  gap: 48px;
  align-items: flex-start;
  max-width: 1920px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  box-sizing: border-box;
  animation: slideUp 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.profile-avatar {
  flex-shrink: 0;
  position: relative;
  transform-style: preserve-3d;
  perspective: 1000px;
}

.avatar-image {
  width: 160px !important;
  height: 160px !important;
  font-size: 48px !important;
  border: 4px solid rgba(255, 255, 255, 0.9) !important;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.2),
    0 0 0 8px rgba(255, 255, 255, 0.1);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 2;
  transform: translateZ(50px);
}

.avatar-image::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  background: linear-gradient(
    45deg,
    var(--primary-light),
    var(--primary-dark)
  );
  opacity: 0;
  z-index: -1;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.avatar-image::after {
  content: '';
  position: absolute;
  inset: -10px;
  border-radius: 50%;
  background: radial-gradient(
    circle at center,
    rgba(var(--primary-rgb), 0.3),
    transparent 70%
  );
  z-index: -1;
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.avatar-image:hover {
  transform: translateZ(60px) rotateY(-15deg);
  box-shadow: 
    20px 20px 60px rgba(0, 0, 0, 0.2),
    0 0 0 12px rgba(255, 255, 255, 0.2);
}

.avatar-image:hover::before {
  opacity: 1;
  inset: -4px;
}

.avatar-image:hover::after {
  opacity: 1;
  transform: scale(1.2);
}

.user-status {
  position: absolute;
  bottom: -12px;
  right: -12px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
  transform: translateZ(70px);
}

.user-status::before {
  content: '';
  position: absolute;
  inset: -1px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.2));
  border-radius: 20px;
  z-index: -1;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #fff;
  display: inline-block;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
  position: relative;
}

.status-dot::after {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: ripple 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.user-status.online {
  background: rgba(16, 185, 129, 0.95);
}

.user-status:hover {
  transform: translateZ(70px) scale(1.05);
  box-shadow: 
    0 8px 30px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.2);
}

@keyframes ripple {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(40px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.profile-info {
  flex: 1;
  padding-top: 40px;
}

.profile-info h1 {
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(to right, var(--primary), var(--primary-light));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.user-bio {
  color: var(--text-secondary);
  font-size: clamp(14px, 2vw, 16px);
  margin-bottom: 24px;
  line-height: 1.6;
}

.user-stats {
  display: flex;
  gap: clamp(16px, 4vw, 32px);
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: clamp(20px, 3vw, 24px);
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.user-badges {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.badge-item:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.badge-item.gold {
  background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
  color: white;
}

.badge-item.silver {
  background: linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%);
  color: white;
}

.badge-item.bronze {
  background: linear-gradient(135deg, #D97706 0%, #92400E 100%);
  color: white;
}

.content-grid {
  padding: 48px;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 48px;
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.glass-card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: clamp(16px, 3vw, 24px);
  padding: clamp(16px, 3vw, 24px);
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.08);
}

.info-card h3,
.game-tags h3,
.activity-heatmap h3,
.recent-articles h3 {
  font-size: clamp(18px, 2.5vw, 20px);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-card h3 i,
.game-tags h3 i,
.activity-heatmap h3 i,
.recent-articles h3 i {
  color: var(--primary);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  transition: transform 0.3s ease;
  padding: 8px;
  border-radius: 8px;
}

.info-item:hover {
  transform: translateX(5px);
  background-color: rgba(var(--primary-rgb), 0.1);
}

.info-item i {
  font-size: 20px;
  color: var(--primary);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.game-tag {
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
}

.game-tag:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}

.tag-count {
  margin-left: 8px;
  opacity: 0.8;
  background: rgba(255,255,255,0.2);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8em;
}

.heatmap-container {
  height: 240px;
  margin-top: 16px;
  border-radius: 12px;
  overflow: hidden;
}

.article-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.article-card {
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.article-cover {
  height: 200px;
  background-size: cover;
  background-position: center;
  position: relative;
  transition: all 0.3s ease;
}

.article-card:hover .article-cover {
  transform: scale(1.05);
}

.article-meta {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.article-info {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.article-info h4 {
  font-size: 20px;
  margin-bottom: 12px;
}

.article-info p {
  font-size: 15px;
  margin-bottom: 20px;
  flex: 1;
}

.article-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.article-tag {
  transition: transform 0.3s ease;
}

.article-tag:hover {
  transform: translateY(-2px);
}

.view-more {
  margin-top: 24px;
  text-align: center;
}

.left-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 72px);
  overflow-y: auto;
  padding-right: 12px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0; /* 防止内容溢出 */
}

.activity-heatmap {
  margin-bottom: 24px;
}

/* 响应式布局优化 */
@media (min-width: 2000px) {
  .profile-main,
  .content-grid {
    padding-left: calc((100% - 1920px) / 2 + 48px);
    padding-right: calc((100% - 1920px) / 2 + 48px);
  }
}

@media (max-width: 1600px) {
  .profile-cover {
    height: 320px;
  }

  .profile-main {
    padding: 0 40px;
  }

  .content-grid {
    padding: 40px;
    grid-template-columns: 300px 1fr;
    gap: 40px;
  }
}

@media (max-width: 1200px) {
  .profile-cover {
    height: 280px;
  }

  .profile-main {
    padding: 0 32px;
  }

  .content-grid {
    padding: 32px;
    grid-template-columns: 280px 1fr;
    gap: 32px;
  }
}

@media (max-width: 1024px) {
  .profile-cover {
    height: 240px;
  }

  .content-grid {
    grid-template-columns: 1fr;
    padding: 24px;
  }
  
  .left-sidebar {
    position: static;
    max-height: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    padding-right: 0;
  }
}

@media (max-width: 768px) {
  .profile-cover {
    height: 200px;
  }

  .profile-main {
    padding: 0 20px;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-top: -60px;
  }

  .content-grid {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .profile-cover {
    height: 180px;
  }
  
  .profile-main {
    padding: 0 16px;
    margin-top: -50px;
  }

  .content-grid {
    padding: 16px;
  }
}
</style>