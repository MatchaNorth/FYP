<template>
  <div class="user-profile-container" :class="{ 'dark': isDark }">
    <!-- 用户基本信息卡片 -->
    <div class="profile-hero glass-card">
      <div class="profile-cover">
        <div class="cover-overlay"></div>
      </div>
      <div class="profile-main">
        <div class="profile-avatar">
          <el-avatar :size="120" :src="userInfo.avatar">
            {{ userInfo.nickname?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="user-status" :class="{ 'online': userInfo.isOnline }">
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
          <h3>个人信息</h3>
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
          <h3>游戏标签</h3>
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
          <h3>活跃度</h3>
          <div class="heatmap-container" ref="heatmapContainer"></div>
        </div>

        <!-- 最近发布的文章 -->
        <div class="recent-articles glass-card">
          <h3>最近发布</h3>
          <div class="article-list">
            <div 
              v-for="article in userInfo.recentArticles" 
              :key="article.id"
              class="article-card"
              @click="viewArticle(article.id)"
            >
              <div class="article-cover" :style="{ backgroundImage: `url(${article.cover})` }">
                <div class="article-meta">
                  <span class="article-date">{{ formatDate(article.publishDate) }}</span>
                  <span class="article-views">
                    <i class="el-icon-view"></i>
                    {{ article.views }}
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
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

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
  router.push(`/article/${articleId}`)
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
        borderWidth: 0.5
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
    const response = await axios.get(`http://localhost:5000/api/user/${userId}/profile`)
    if (response.data.code === 200) {
      userInfo.value = response.data.data
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
.user-profile-container {
  padding: 32px;
  min-height: 100vh;
  background: var(--bg-gradient);
}

.profile-hero {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 32px;
}

.profile-cover {
  height: 240px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  position: relative;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.4) 100%);
}

.profile-main {
  padding: 32px;
  margin-top: -80px;
  position: relative;
  z-index: 1;
  display: flex;
  gap: 32px;
}

.profile-avatar {
  position: relative;
}

.user-status {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(239, 68, 68, 0.9);
  color: white;
}

.user-status.online {
  background: rgba(16, 185, 129, 0.9);
}

.profile-info {
  flex: 1;
}

.profile-info h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(to right, var(--primary), var(--primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.user-bio {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 24px;
}

.user-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
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
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
  margin-top: 32px;
}

.glass-card {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  border: 1px solid var(--border-color);
}

.info-card h3,
.game-tags h3,
.activity-heatmap h3,
.recent-articles h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
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
}

.game-tag:hover {
  transform: translateY(-2px);
}

.tag-count {
  margin-left: 8px;
  opacity: 0.8;
}

.heatmap-container {
  height: 200px;
  margin-top: 16px;
}

.article-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.article-card {
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.article-card:hover {
  transform: translateY(-4px);
}

.article-cover {
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
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
  padding: 16px;
}

.article-info h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.article-info p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .left-sidebar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .user-profile-container {
    padding: 16px;
  }
  
  .profile-main {
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-top: -60px;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .user-badges {
    justify-content: center;
  }
}
</style> 