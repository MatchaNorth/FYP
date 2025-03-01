<template>
  <div class="article-detail-container">
    <HeadMenu />
    <div class="article-content">
      <!-- 左侧文章内容 -->
      <div class="article-main glass-card">
        <div class="article-header">
          <h1>{{ article.title }}</h1>
          <div class="article-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDate(article.created_at) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><View /></el-icon>
              <span>{{ article.views || 0 }} 阅读</span>
            </div>
            <div class="meta-item">
              <el-icon><Star /></el-icon>
              <span>{{ article.likes || 0 }} 点赞</span>
            </div>
          </div>
        </div>
        <div class="article-body markdown-content" v-html="renderedContent"></div>
      </div>

      <!-- 右侧作者信息和操作 -->
      <div class="article-sidebar">
        <div class="author-card glass-card">
          <div class="author-info">
            <img v-if="article.author_avatar" :src="article.author_avatar" class="author-avatar" alt="作者头像">
            <span v-else class="author-avatar-placeholder">{{ article.author?.slice(0, 2) }}</span>
            <div class="author-details">
              <h3>{{ article.author_nickname || article.author }}</h3>
              <p class="author-bio">游戏爱好者</p>
            </div>
          </div>
          <div class="author-stats">
            <div class="stat-item">
              <span class="stat-value">{{ authorStats.articles || 0 }}</span>
              <span class="stat-label">文章</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ authorStats.total_views || 0 }}</span>
              <span class="stat-label">总阅读</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ authorStats.total_likes || 0 }}</span>
              <span class="stat-label">获赞</span>
            </div>
          </div>
        </div>

        <div class="action-card glass-card">
          <button class="action-btn like-btn" :class="{ active: isLiked }" @click="handleLike">
            <el-icon><Star /></el-icon>
            <span>{{ isLiked ? '已点赞' : '点赞' }}</span>
          </button>
          <button v-if="isAuthor" class="action-btn edit-btn" @click="handleEdit">
            <el-icon><EditPen /></el-icon>
            <span>编辑文章</span>
          </button>
          <button v-if="isAuthor" class="action-btn delete-btn" @click="handleDelete">
            <el-icon><Delete /></el-icon>
            <span>删除文章</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import HeadMenu from '../components/HeadMenu.vue'
import { Calendar, View, Star, EditPen, Delete } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: true
})

const route = useRoute()
const router = useRouter()
const article = ref({})
const authorStats = ref({})
const isLiked = ref(false)

// 渲染Markdown内容
const renderedContent = computed(() => {
  return md.render(article.value.content || '')
})

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 判断是否为作者
const isAuthor = computed(() => {
  const userId = localStorage.getItem('userId')
  return userId && article.value.author_id === parseInt(userId)
})

// 获取文章详情
const fetchArticle = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:5000/api/articles/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      article.value = response.data.data
      fetchAuthorStats()
      checkLikeStatus()
    }
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('获取文章详情失败')
  }
}

// 获取作者统计信息
const fetchAuthorStats = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:5000/api/users/${article.value.author_id}/stats`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      authorStats.value = response.data.data
    }
  } catch (error) {
    console.error('获取作者统计信息失败:', error)
  }
}

// 检查点赞状态
const checkLikeStatus = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:5000/api/articles/${route.params.id}/like`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      isLiked.value = response.data.data.liked
    }
  } catch (error) {
    console.error('获取点赞状态失败:', error)
  }
}

// 处理点赞
const handleLike = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`http://localhost:5000/api/articles/${route.params.id}/like`, {}, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      isLiked.value = !isLiked.value
      article.value.likes = response.data.data.likes
      ElMessage.success(isLiked.value ? '点赞成功' : '取消点赞')
    }
  } catch (error) {
    console.error('点赞操作失败:', error)
    ElMessage.error('点赞操作失败')
  }
}

// 处理编辑
const handleEdit = () => {
  router.push(`/articles/edit/${route.params.id}`)
}

// 处理删除
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = localStorage.getItem('token')
    const response = await axios.delete(`http://localhost:5000/api/articles/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('删除成功')
      router.push('/home')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文章失败:', error)
      ElMessage.error('删除文章失败')
    }
  }
}

onMounted(() => {
  fetchArticle()
})
</script>

<style scoped>
.article-detail-container {
  min-height: 100vh;
  background: var(--bg-gradient);
  padding-top: 64px;
}

.article-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 40px 60px;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 32px;
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.article-main {
  padding: 48px;
  border-radius: 24px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
}

.article-header {
  margin-bottom: 32px;
}

.article-header h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 24px;
  line-height: 1.4;
  color: var(--text-primary);
}

.article-meta {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-item .el-icon {
  font-size: 16px;
}

.article-body {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
}

.article-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.author-card, .action-card {
  padding: 24px;
  border-radius: 20px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
}

.author-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.author-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.author-avatar-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-details h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.author-bio {
  color: var(--text-secondary);
  font-size: 14px;
}

.author-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.action-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.like-btn {
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary);
}

.like-btn:hover, .like-btn.active {
  background: var(--primary);
  color: white;
}

.edit-btn {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.edit-btn:hover {
  background: #10B981;
  color: white;
}

.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.delete-btn:hover {
  background: #EF4444;
  color: white;
}

/* 响应式布局 */
@media (max-width: 1440px) {
  .article-content {
    padding: 32px 40px;
  }
}

@media (max-width: 1024px) {
  .article-content {
    padding: 24px;
    grid-template-columns: 1fr;
  }

  .article-sidebar {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .author-card, .action-card {
    flex: 1;
    min-width: 300px;
  }
}

@media (max-width: 768px) {
  .article-content {
    padding: 16px;
  }

  .article-main {
    padding: 24px;
  }

  .article-header h1 {
    font-size: 28px;
  }

  .article-meta {
    flex-wrap: wrap;
    gap: 16px;
  }

  .author-card, .action-card {
    flex: 1 0 100%;
  }
}

.markdown-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin: 1.5em 0 0.8em;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-content :deep(h1) {
  font-size: 2em;
}

.markdown-content :deep(h2) {
  font-size: 1.75em;
}

.markdown-content :deep(h3) {
  font-size: 1.5em;
}

.markdown-content :deep(h4) {
  font-size: 1.25em;
}

.markdown-content :deep(h5) {
  font-size: 1.1em;
}

.markdown-content :deep(h6) {
  font-size: 1em;
}

.markdown-content :deep(p) {
  margin: 1em 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.markdown-content :deep(li) {
  margin: 0.5em 0;
}

.markdown-content :deep(blockquote) {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 4px solid var(--primary);
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--text-secondary);
}

.markdown-content :deep(code) {
  padding: 0.2em 0.4em;
  background: rgba(var(--primary-rgb), 0.1);
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  margin: 1em 0;
  padding: 1em;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  padding: 0;
  background: none;
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1em 0;
}

.markdown-content :deep(table) {
  width: 100%;
  margin: 1em 0;
  border-collapse: collapse;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 0.5em;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.markdown-content :deep(th) {
  background: rgba(255, 255, 255, 0.05);
}

.markdown-content :deep(a) {
  color: var(--primary);
  text-decoration: none;
  transition: all 0.3s ease;
}

.markdown-content :deep(a:hover) {
  color: var(--primary-light);
  text-decoration: underline;
}

.markdown-content :deep(hr) {
  margin: 2em 0;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style> 