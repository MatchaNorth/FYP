<template>
    <div class="recommended-articles">
      <h2 class="section-title">为您推荐</h2>
      
      <div class="articles-list">
        <div 
          v-for="article in recommendations" 
          :key="article.article_id"
          class="article-item glass-card"
          @click="viewArticle(article.article_id)"
        >
          <!-- 左侧文章图片 -->
          <div class="article-image" v-if="article.cover">
            <img :src="article.cover" :alt="article.title">
          </div>
          <div class="article-image placeholder" v-else>
            <el-icon><Document /></el-icon>
          </div>
  
          <!-- 中间文章信息 -->
          <div class="article-info">
            <h3 class="article-title">{{ article.title }}</h3>
            <div class="article-meta">
              <span class="author">
                <el-icon><User /></el-icon>
                {{ article.author_nickname || article.author }}
              </span>
              <span class="date">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(article.created_at) }}
              </span>
              <span class="stats">
                <el-icon><View /></el-icon>
                {{ article.views || 0 }}
                <el-icon><Star /></el-icon>
                {{ article.likes || 0 }}
              </span>
            </div>
            <!-- 推荐理由 -->
            <div class="recommendation-reasons">
              <div 
                v-for="(reason, index) in article.reasons" 
                :key="index"
                :class="['reason-tag', `reason-${reason.type}`]"
              >
                <el-icon>
                  <component :is="getReasonIcon(reason.type)" />
                </el-icon>
                {{ reason.text }}
              </div>
            </div>
          </div>
  
          <!-- 右侧推荐权重 -->
          <div class="recommendation-weight">
            <div class="weight-circle" :style="getWeightStyle(article.weight)">
              {{ Math.round(article.weight) }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { 
    Document,
    User,
    Calendar,
    View,
    Star,
    InfoFilled,
    StarFilled,
    Timer,
    Clock,
    Histogram,
    Edit,
    UserFilled,
    Promotion
  } from '@element-plus/icons-vue'
  import axios from 'axios'
  
  const router = useRouter()
  const recommendations = ref([])
  
  // 获取推荐文章
  const fetchRecommendations = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/articles/recommendations', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        withCredentials: true
      })
      if (response.data.code === 200) {
        recommendations.value = response.data.data
      }
    } catch (error) {
      console.error('获取推荐失败:', error)
    }
  }
  
  // 查看文章
  const viewArticle = (id) => {
    router.push(`/articles/public/${id}`)
  }
  
  // 格式化日期
  const formatDate = (dateString) => {
    if (!dateString) return '未知日期'
    try {
    const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        console.error('无效的日期字符串:', dateString)
        return '未知日期'
      }
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
    } catch (error) {
      console.error('日期格式化错误:', error, '原始日期字符串:', dateString)
      return '未知日期'
    }
  }
  
  // 获取权重样式
  const getWeightStyle = (weight) => {
    const hue = weight * 1.2 // 0-100 映射到 0-120 的色相
    return {
      background: `linear-gradient(135deg, hsl(${hue}, 70%, 50%), hsl(${hue}, 70%, 40%))`
    }
  }
  
  // 获取推荐理由图标
  const getReasonIcon = (type) => {
    const iconMap = {
      'hot': Promotion,
      'popular': StarFilled,
      'new': Timer,
      'recent': Clock,
      'interest': Histogram,
      'preference': Star,
      'similar': Edit,
      'author': UserFilled
    }
    return iconMap[type] || InfoFilled
  }
  
  onMounted(() => {
    fetchRecommendations()
  })
  </script>
  
  <style scoped>
  .recommended-articles {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .section-title {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 24px;
    color: var(--text-primary);
    text-align: center;
    position: relative;
    padding-bottom: 12px;
  }
  
  .section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
    border-radius: 3px;
  }
  
  .articles-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .article-item {
    display: flex;
    align-items: stretch;
    padding: 16px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .article-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 0.08);
  }
  
  .article-image {
    width: 120px;
    height: 90px;
    border-radius: 8px;
    overflow: hidden;
    margin-right: 16px;
    flex-shrink: 0;
    background: var(--primary-light);
  }
  
  .article-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .article-image.placeholder {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }
  
  .article-image.placeholder .el-icon {
    font-size: 40px;
    opacity: 0.8;
  }
  
  .article-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .article-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary);
    line-height: 1.4;
  }
  
  .article-meta {
    display: flex;
    gap: 16px;
    color: var(--text-secondary);
    font-size: 13px;
    margin-bottom: 8px;
  }
  
  .article-meta span {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  
  .recommendation-reasons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
  }
  
  .reason-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
  }
  
  .reason-tag .el-icon {
    font-size: 14px;
  }
  
  /* 不同类型的推荐理由样式 */
  .reason-hot {
    background: rgba(255, 87, 34, 0.1);
    color: #ff5722;
  }
  
  .reason-popular {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
  }
  
  .reason-new {
    background: rgba(76, 175, 80, 0.1);
    color: #4caf50;
  }
  
  .reason-recent {
    background: rgba(33, 150, 243, 0.1);
    color: #2196f3;
  }
  
  .reason-interest {
    background: rgba(156, 39, 176, 0.1);
    color: #9c27b0;
  }
  
  .reason-preference {
    background: rgba(233, 30, 99, 0.1);
    color: #e91e63;
  }
  
  .reason-similar {
    background: rgba(0, 188, 212, 0.1);
    color: #00bcd4;
  }
  
  .reason-author {
    background: rgba(255, 152, 0, 0.1);
    color: #ff9800;
  }
  
  /* 悬停效果 */
  .reason-tag:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .recommendation-weight {
    margin-left: 16px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
  }
  
  .weight-circle {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .article-item {
      flex-direction: column;
      align-items: flex-start;
    }
  
    .article-image {
      width: 100%;
      height: 200px;
      margin-right: 0;
      margin-bottom: 16px;
    }
  
    .recommendation-weight {
      margin-left: 0;
      margin-top: 16px;
      align-self: center;
    }
    
    .article-meta {
      flex-wrap: wrap;
    }
  }
  </style>