<template>
    <HeadMenu />
    <div class="home-container">
      <header class="home-header glass-card">
        <div class="header-content">
          <h1>发现游戏文章</h1>
          <p>探索来自游戏玩家的精彩文章</p>
        </div>
        <div class="header-actions">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜索文章..." 
              @input="handleSearch"
            >
          </div>
          <div class="filter-box">
            <button 
              v-for="filter in filters" 
              :key="filter.value"
              :class="['filter-btn', { active: currentFilter === filter.value }]"
              @click="currentFilter = filter.value"
            >
              {{ filter.label }}
            </button>
            <button 
              class="filter-btn recommend-btn"
              @click="showRecommendations = true"
            >
              <el-icon><Star /></el-icon>
              为您推荐
            </button>
          </div>
        </div>
      </header>

      <main class="articles-container">
        <TransitionGroup 
          name="article-list" 
          tag="div" 
          class="articles-grid"
        >
          <article 
            v-for="article in filteredArticles" 
            :key="article.id" 
            class="article-card glass-card" 
            @click="viewArticle(article.id)"
          >
            <div class="article-content">
              <div class="article-header">
                <div class="title-section">
                  <h2 class="article-title">
                    {{ article.title }}
                    <span v-if="article.is_pinned" class="pinned-badge">置顶</span>
                  </h2>
                  <div class="article-tags">
                    <span class="article-tag">游戏</span>
                  </div>
                </div>
              </div>
              <p class="article-summary">{{ article.summary }}</p>
              <div class="article-meta">
                <div class="meta-left">
                  <div class="author-info">
                    <div class="author-avatar">
                      <img 
                        v-if="article.author_avatar" 
                        :src="article.author_avatar" 
                        alt="作者头像"
                      >
                      <span v-else class="avatar-placeholder">
                        {{ article.author.slice(0, 2) }}
                      </span>
                    </div>
                    <div class="author-details">
                      <span class="author-name">{{ article.author_nickname || article.author }}</span>
                      <span class="publish-time">{{ formatDate(article.created_at) }}</span>
                    </div>
                  </div>
                </div>
                <div class="meta-right">
                  <div class="stat-item">
                    <el-icon><View /></el-icon>
                    <span>{{ article.views || 0 }}</span>
                  </div>
                  <div class="stat-item">
                    <el-icon><Star /></el-icon>
                    <span>{{ article.likes || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="hover-effect"></div>
          </article>
        </TransitionGroup>

        <div v-if="articles.length === 0" class="empty-state">
          <el-icon class="empty-icon"><Edit /></el-icon>
          <p>暂无文章</p>
          <button class="create-btn" @click="createArticle">写文章</button>
        </div>
      </main>
    </div>

    <!-- 推荐文章对话框 -->
    <el-dialog
      v-model="showRecommendations"
      title="为您推荐"
      width="80%"
      :close-on-click-modal="false"
      class="recommendations-dialog"
    >
      <RecommendedArticles />
    </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import HeadMenu from '../components/HeadMenu.vue'
import RecommendedArticles from '../components/RecommendedArticles.vue'
import { Search, Calendar, User, View, Star, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const articles = ref([])
const searchQuery = ref('')
const currentFilter = ref('all')
const showRecommendations = ref(false)

const filters = [
  { label: '全部', value: 'all' },
  { label: '最新发布', value: 'latest' },
  { label: '最多浏览', value: 'most-viewed' },
  { label: '最多点赞', value: 'most-liked' }
]

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 筛选文章
const filteredArticles = computed(() => {
  // 只显示已发布且未隐藏的文章
  let result = articles.value.filter(article => 
    article.status === 'published' && !article.is_hidden
  )

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(article => 
      article.title.toLowerCase().includes(query) ||
      article.summary.toLowerCase().includes(query)
    )
  }

  // 分类过滤
  switch (currentFilter.value) {
    case 'latest':
      result = [...result].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'most-viewed':
      result = [...result].sort((a, b) => (b.views || 0) - (a.views || 0))
      break
    case 'most-liked':
      result = [...result].sort((a, b) => (b.likes || 0) - (a.likes || 0))
      break
  }

  // 置顶文章排最前
  result = result.sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return 0
  })

  return result
})

// 搜索处理（可以添加防抖）
const handleSearch = () => {
  // 这里可以添加防抖逻辑
}

// 获取文章列表
const fetchArticles = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/articles/public')
    if (response.data.code === 200) {
      articles.value = response.data.data.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      )
    }
  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('获取文章列表失败')
  }
}

// 查看文章详情
const viewArticle = (id) => {
  router.push(`/articles/public/${id}`)
}

// 创建新文章
const createArticle = () => {
  router.push('/articles')
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.home-container {
  width: 100%;
  min-height: calc(100vh - 64px);
  margin-top: 10rem;
  margin: 0;
  padding: 0;
  background: var(--bg-gradient);
  display: flex;
  flex-direction: column;
}

.home-header {
  width: 100%;
  padding: 40px 0;
  margin: 0;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto 32px;
  padding: 0 60px;
}

.header-content h1 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.header-content p {
  color: var(--text-secondary);
  font-size: 18px;
  opacity: 0.8;
}

.header-actions {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 60px;
  display: flex;
  gap: 24px;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 480px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 12px 20px 12px 44px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: rgba(var(--primary-rgb), 0.5);
  background: rgba(255, 255, 255, 0.1);
}

.search-box .search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 18px;
}

.filter-box {
  display: flex;
  gap: 12px;
}

.filter-btn {
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(var(--primary-rgb), 0.3);
}

.filter-btn.active {
  background: rgba(var(--primary-rgb), 0.15);
  border-color: rgba(var(--primary-rgb), 0.5);
  color: var(--primary);
}

.filter-btn.recommend-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  border: none;
}

.filter-btn.recommend-btn:hover {
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
  transform: translateY(-1px);
}

.filter-btn.recommend-btn .el-icon {
  font-size: 16px;
}

.articles-container {
  flex: 1;
  width: 100%;
  padding: 40px 0;
  margin: 0 auto;
}

.articles-grid {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 60px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

/* 文章卡片动画 */
.article-list-enter-active,
.article-list-leave-active {
  transition: all 0.5s ease;
}

.article-list-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.article-list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

/* 文章卡片样式 */
.article-card {
  position: relative;
  background: var(--card-bg);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.article-content {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.title-section {
  margin-bottom: 16px;
}

.article-title {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-tags {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.article-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary);
  background: rgba(var(--primary-rgb), 0.1);
}

.article-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  opacity: 0.8;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
}

.author-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 600;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.author-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.publish-time {
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0.8;
}

.meta-right {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-item .el-icon {
  font-size: 16px;
}

/* 悬停效果 */
.hover-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-rgb), 0) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.article-card:hover .hover-effect {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .articles-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .articles-container {
    padding: 0 20px;
  }

  .articles-grid {
    grid-template-columns: 1fr;
  }

  .article-card {
    margin-bottom: 16px;
  }
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.create-btn {
  margin-top: 20px;
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}

/* 推荐文章对话框样式 */
:deep(.recommendations-dialog) {
  .el-dialog__body {
    padding: 0;
  }
  
  .el-dialog__header {
    margin-right: 0;
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .el-dialog__title {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.pinned-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  border-radius: 8px;
  vertical-align: middle;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
  letter-spacing: 2px;
}
</style> 