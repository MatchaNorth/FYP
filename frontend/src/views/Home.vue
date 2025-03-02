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
          </div>
        </div>
      </header>

      <main class="articles-container">
        <div class="articles-grid">
          <article v-for="article in filteredArticles" :key="article.id" class="article-card glass-card" @click="viewArticle(article.id)">
            <div class="article-content">
              <div class="article-header">
                <h2>{{ article.title }}</h2>
                <div class="article-status" :class="article.status">
                  {{ article.status === 'published' ? '已发布' : '草稿' }}
                </div>
              </div>
              <p class="article-summary">{{ article.summary }}</p>
              <div class="article-meta">
                <div class="meta-left">
                  <div class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    <span>{{ formatDate(article.created_at) }}</span>
                  </div>
                  <div class="meta-item author">
                    <img v-if="article.author_avatar" :src="article.author_avatar" class="author-avatar" alt="作者头像">
                    <span v-else class="author-placeholder">{{ article.author.slice(0, 2) }}</span>
                    <span>{{ article.author_nickname || article.author }}</span>
                  </div>
                </div>
                <div class="meta-right">
                  <div class="meta-item">
                    <el-icon><View /></el-icon>
                    <span>{{ article.views || 0 }}</span>
                  </div>
                  <div class="meta-item">
                    <el-icon><Star /></el-icon>
                    <span>{{ article.likes || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-if="articles.length === 0" class="empty-state">
          <el-icon class="empty-icon"><Edit /></el-icon>
          <p>暂无文章</p>
          <button class="create-btn" @click="createArticle">写文章</button>
        </div>
      </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import HeadMenu from '../components/HeadMenu.vue'
import { Search, Calendar, User, View, Star, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const articles = ref([])
const searchQuery = ref('')
const currentFilter = ref('all')

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
  // 首先过滤出已发布的文章
  let result = articles.value.filter(article => article.status === 'published')

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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 32px;
}

.article-card {
  height: 100%;
  padding: 32px;
  border-radius: 24px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.article-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, 
    rgba(var(--primary-rgb), 0.1) 0%,
    rgba(var(--primary-light-rgb), 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.4s ease;
}

.article-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
  border-color: rgba(var(--primary-rgb), 0.2);
}

.article-card:hover::before {
  opacity: 1;
}

.article-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.article-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  flex: 1;
}

.article-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.article-status.published {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
}

.article-status.draft {
  background: rgba(var(--primary-rgb), 0.15);
  color: var(--primary);
}

.article-summary {
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 24px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 76px;
  flex: 1;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.meta-left, .meta-right {
  display: flex;
  gap: 16px;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-item.author {
  color: var(--text-primary);
  font-weight: 500;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.author-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-secondary);
  background: var(--card-bg);
  border-radius: 32px;
  backdrop-filter: blur(20px);
  margin: 0 auto;
  max-width: 600px;
}

.empty-state .empty-icon {
  font-size: 48px;
  margin-bottom: 24px;
  display: block;
  opacity: 0.8;
  color: var(--text-secondary);
}

.empty-state p {
  font-size: 18px;
  margin-bottom: 32px;
  opacity: 0.8;
}

.create-btn {
  padding: 14px 32px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.2);
}

.create-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(var(--primary-rgb), 0.4);
}

.meta-item .el-icon {
  font-size: 16px;
  color: var(--text-secondary);
}

/* 响应式布局 */
@media (max-width: 1440px) {
  .header-content,
  .header-actions,
  .articles-grid {
    padding: 0 40px;
  }

  .articles-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 24px;
  }
  
  .home-header {
    padding: 32px 0;
  }
}

@media (max-width: 1024px) {
  .header-content,
  .header-actions,
  .articles-grid {
    padding: 0 24px;
  }

  .articles-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }
  
  .home-header {
    padding: 24px 0;
  }
  
  .header-content h1 {
    font-size: 36px;
  }
}

@media (max-width: 768px) {
  .header-content,
  .header-actions,
  .articles-grid {
    padding: 0 20px;
  }

  .articles-grid {
    grid-template-columns: 1fr;
  }
  
  .home-header {
    padding: 20px 0;
  }
  
  .header-content h1 {
    font-size: 28px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 16px;
  }
  
  .search-box {
    max-width: none;
  }
  
  .filter-box {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 8px;
  }
  
  .filter-btn {
    white-space: nowrap;
  }
}
</style> 