<template>
  <div>
    <HeadMenu />
    <div class="home-container">
      <header class="home-header glass-card">
        <div class="header-content">
          <h1>我的文章</h1>
          <p>{{ new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
        </div>
      </header>

      <main class="articles-container">
        <div class="articles-grid">
          <article v-for="article in articles" :key="article.id" class="article-card glass-card" @click="viewArticle(article.id)">
            <div class="article-content">
              <h2>{{ article.title }}</h2>
              <p class="article-summary">{{ article.summary }}</p>
              <div class="article-meta">
                <div class="meta-item">
                  <i class="icon-calendar"></i>
                  <span>{{ formatDate(article.created_at) }}</span>
                </div>
                <div class="meta-item">
                  <i class="icon-user"></i>
                  <span>{{ article.author }}</span>
                </div>
              </div>
            </div>
            <div class="article-status" :class="article.status">
              {{ article.status === 'published' ? '已发布' : '草稿' }}
            </div>
          </article>
        </div>

        <div v-if="articles.length === 0" class="empty-state">
          <i class="icon-article"></i>
          <p>暂无文章</p>
          <button class="create-btn" @click="createArticle">写文章</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import HeadMenu from '../components/HeadMenu.vue'

const router = useRouter()
const articles = ref([])

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 获取文章列表
const fetchArticles = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/articles', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
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
  router.push(`/article/${id}`)
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
  max-width: 1440px;
  margin: 0 auto;
  padding: 104px 60px 40px;
  min-height: 100vh;
  background: var(--bg-gradient);
}

.home-header {
  padding: 48px 60px;
  margin-bottom: 48px;
  border-radius: 32px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(to right, var(--primary), var(--primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.header-content p {
  color: var(--text-secondary);
  font-size: 18px;
  opacity: 0.8;
}

.articles-container {
  margin-top: 40px;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.article-card {
  padding: 32px;
  border-radius: 24px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: 100%;
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

.article-content h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
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
  flex: 1;
}

.article-meta {
  display: flex;
  gap: 20px;
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: auto;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-item i {
  font-size: 18px;
}

.article-status {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.article-status.published {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
}

.article-status.draft {
  background: rgba(var(--primary-rgb), 0.15);
  color: var(--primary);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-secondary);
  background: var(--card-bg);
  border-radius: 32px;
  backdrop-filter: blur(20px);
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 24px;
  display: block;
  opacity: 0.8;
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

.icon-calendar::before {
  content: "📅";
}

.icon-user::before {
  content: "👤";
}

.icon-article::before {
  content: "📝";
}

/* 响应式布局 */
@media (max-width: 1440px) {
  .home-container {
    padding: 32px 40px;
  }
  
  .articles-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}

@media (max-width: 1024px) {
  .home-container {
    padding: 24px;
  }
  
  .home-header {
    padding: 32px;
    margin-bottom: 32px;
  }
  
  .header-content h1 {
    font-size: 36px;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 16px;
  }
  
  .home-header {
    padding: 24px;
    margin-bottom: 24px;
  }
  
  .header-content h1 {
    font-size: 28px;
  }
  
  .article-card {
    padding: 24px;
  }
}
</style> 