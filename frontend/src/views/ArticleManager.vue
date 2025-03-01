<template>
  <div class="article-manager">
    <!-- 文章列表 -->
    <div class="article-list" v-if="!showEditor">
      <div class="list-header">
        <div class="search-bar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文章..."
            prefix-icon="el-icon-search"
            clearable
          />
        </div>
        <el-button type="primary" @click="createNewArticle">
          <i class="el-icon-plus"></i>
          写文章
        </el-button>
      </div>
      
      <el-table 
        :data="filteredArticles" 
        style="width: 100%"
        :header-cell-style="{
          background: '#ffffff',
          color: '#0f172a',
          fontWeight: '600'
        }"
      >
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <div class="article-title" @click="editArticle(row)">
              <span class="title-text">{{ row.title }}</span>
              <span class="word-count">{{ getWordCount(row.content) }}字</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="摘要" min-width="300">
          <template #default="{ row }">
            <div class="article-summary">{{ row.summary || '暂无摘要' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="article-actions">
              <el-button 
                size="small" 
                type="text"
                @click="editArticle(row)"
              >
                <i class="el-icon-edit"></i>
                编辑
              </el-button>
              <el-button 
                size="small" 
                type="text"
                class="delete-btn"
                @click="deleteArticle(row)"
              >
                <i class="el-icon-delete"></i>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- Markdown编辑器 -->
    <div class="article-editor" v-else>
      <div class="editor-header">
        <el-input
          v-model="currentArticle.title"
          placeholder="请输入文章标题"
          class="title-input"
        />
        <div class="editor-actions">
          <el-button @click="showEditor = false">
            <i class="el-icon-back"></i>
            返回
          </el-button>
          <el-button 
            type="info" 
            @click="saveArticle('draft')"
            :loading="saving"
          >
            <i class="el-icon-document"></i>
            保存草稿
          </el-button>
          <el-button 
            type="primary" 
            @click="saveArticle('published')"
            :loading="saving"
          >
            <i class="el-icon-upload2"></i>
            发布文章
          </el-button>
        </div>
      </div>
      
      <div class="editor-container">
        <div class="markdown-editor">
          <div class="editor-toolbar">
            <el-button-group>
              <el-button size="small" @click="insertMarkdown('bold')" title="粗体 (Ctrl+B)">
                <i class="el-icon-bold">B</i>
              </el-button>
              <el-button size="small" @click="insertMarkdown('italic')" title="斜体 (Ctrl+I)">
                <i class="el-icon-italic">I</i>
              </el-button>
              <el-button size="small" @click="insertMarkdown('header')" title="标题">
                <i class="el-icon-header">H</i>
              </el-button>
            </el-button-group>
            <el-divider direction="vertical" />
            <el-button-group>
              <el-button size="small" @click="insertMarkdown('link')" title="链接 (Ctrl+K)">
                <i class="el-icon-link"></i>
              </el-button>
              <el-button size="small" @click="insertMarkdown('image')" title="图片">
                <i class="el-icon-picture"></i>
              </el-button>
            </el-button-group>
            <el-divider direction="vertical" />
            <el-button-group>
              <el-button size="small" @click="insertMarkdown('quote')" title="引用">
                <i class="el-icon-quote">『』</i>
              </el-button>
              <el-button size="small" @click="insertMarkdown('code')" title="代码">
                <i class="el-icon-code">{}</i>
              </el-button>
              <el-button size="small" @click="insertMarkdown('list')" title="列表">
                <i class="el-icon-list">•</i>
              </el-button>
            </el-button-group>
          </div>
          <el-input
            v-model="currentArticle.content"
            type="textarea"
            :rows="20"
            placeholder="请输入文章内容（支持Markdown格式）"
            @input="updatePreview"
            ref="markdownInput"
            @keydown.ctrl.b.prevent="insertMarkdown('bold')"
            @keydown.ctrl.i.prevent="insertMarkdown('italic')"
            @keydown.ctrl.k.prevent="insertMarkdown('link')"
            @keydown.ctrl.z.prevent="undo"
            @keydown.ctrl.y.prevent="redo"
          />
        </div>
        <div class="markdown-preview markdown-body" v-html="previewHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const articles = ref([])
const showEditor = ref(false)
const currentArticle = ref({
  id: null,
  title: '',
  content: '',
  status: 'draft'
})
const previewHtml = ref('')
const saving = ref(false)
const searchQuery = ref('')
const markdownInput = ref(null)

// 编辑历史管理
const history = ref({
  past: [],
  future: [],
  ignoreNextChange: false
})

// 监听内容变化
watch(() => currentArticle.value.content, (newContent, oldContent) => {
  if (history.value.ignoreNextChange) {
    history.value.ignoreNextChange = false
    return
  }
  
  history.value.past.push(oldContent || '')
  history.value.future = []
  
  // 限制历史记录数量，避免内存占用过大
  if (history.value.past.length > 50) {
    history.value.past.shift()
  }
}, { deep: true })

// 撤销操作
const undo = () => {
  if (history.value.past.length === 0) return
  
  const currentContent = currentArticle.value.content
  const previousContent = history.value.past.pop()
  
  history.value.future.push(currentContent)
  history.value.ignoreNextChange = true
  currentArticle.value.content = previousContent
  updatePreview()
}

// 重做操作
const redo = () => {
  if (history.value.future.length === 0) return
  
  const currentContent = currentArticle.value.content
  const nextContent = history.value.future.pop()
  
  history.value.past.push(currentContent)
  history.value.ignoreNextChange = true
  currentArticle.value.content = nextContent
  updatePreview()
}

// 重置历史记录
const resetHistory = () => {
  history.value = {
    past: [],
    future: [],
    ignoreNextChange: false
  }
}

// 获取文章列表
const fetchArticles = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/articles', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      articles.value = response.data.data
    }
  } catch (error) {
    console.error('获取文章列表失败:', error)
    ElMessage.error('获取文章列表失败')
  }
}

// 创建新文章
const createNewArticle = () => {
  currentArticle.value = {
    id: null,
    title: '',
    content: '',
    status: 'draft'
  }
  resetHistory()
  showEditor.value = true
}

// 编辑文章
const editArticle = async (article) => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://localhost:5000/api/articles/${article.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      currentArticle.value = response.data.data
      resetHistory()
      updatePreview()
      showEditor.value = true
    }
  } catch (error) {
    console.error('获取文章详情失败:', error)
    ElMessage.error('获取文章详情失败')
  }
}

// 删除文章
const deleteArticle = async (article) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const token = localStorage.getItem('token')
    const response = await axios.delete(`http://localhost:5000/api/articles/${article.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      ElMessage.success('删除成功')
      fetchArticles()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文章失败:', error)
      ElMessage.error('删除文章失败')
    }
  }
}

// 保存文章
const saveArticle = async (status) => {
  if (!currentArticle.value.title.trim()) {
    ElMessage.warning('请输入文章标题')
    return
  }
  
  if (!currentArticle.value.content.trim()) {
    ElMessage.warning('请输入文章内容')
    return
  }
  
  saving.value = true
  try {
    const token = localStorage.getItem('token')
    const url = currentArticle.value.id
      ? `http://localhost:5000/api/articles/${currentArticle.value.id}`
      : 'http://localhost:5000/api/articles'
    const method = currentArticle.value.id ? 'put' : 'post'
    
    const response = await axios[method](url, {
      ...currentArticle.value,
      status
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      ElMessage.success(status === 'published' ? '发布成功' : '保存成功')
      showEditor.value = false
      fetchArticles()
    }
  } catch (error) {
    console.error('保存文章失败:', error)
    ElMessage.error('保存文章失败')
  } finally {
    saving.value = false
  }
}

// 更新预览
const updatePreview = () => {
  const html = marked(currentArticle.value.content || '')
  previewHtml.value = DOMPurify.sanitize(html)
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文章字数
const getWordCount = (content) => {
  if (!content) return 0
  // 移除 Markdown 语法标记
  const text = content.replace(/[#*`~>]/g, '').trim()
  return text.length
}

// 过滤文章列表
const filteredArticles = computed(() => {
  if (!searchQuery.value) return articles.value
  const query = searchQuery.value.toLowerCase()
  return articles.value.filter(article => 
    article.title.toLowerCase().includes(query) ||
    article.summary?.toLowerCase().includes(query)
  )
})

// 插入 Markdown 语法
const insertMarkdown = async (type) => {
  const textarea = markdownInput.value.$el.querySelector('textarea')
  const { selectionStart, selectionEnd } = textarea
  const selectedText = currentArticle.value.content.substring(selectionStart, selectionEnd)
  let insertion = ''
  let cursorOffset = 0

  switch (type) {
    case 'bold':
      insertion = `**${selectedText || '粗体文本'}**`
      cursorOffset = selectedText ? 0 : -2
      break
    case 'italic':
      insertion = `*${selectedText || '斜体文本'}*`
      cursorOffset = selectedText ? 0 : -1
      break
    case 'header':
      insertion = `\n## ${selectedText || '标题'}\n`
      cursorOffset = selectedText ? 0 : -1
      break
    case 'link':
      insertion = `[${selectedText || '链接文本'}](url)`
      cursorOffset = selectedText ? -1 : -4
      break
    case 'image':
      insertion = `![${selectedText || '图片描述'}](图片链接)`
      cursorOffset = selectedText ? -1 : -4
      break
    case 'quote':
      insertion = `\n> ${selectedText || '引用文本'}\n`
      cursorOffset = selectedText ? 0 : -1
      break
    case 'code':
      insertion = selectedText.includes('\n')
        ? `\n\`\`\`\n${selectedText || '代码块'}\n\`\`\`\n`
        : `\`${selectedText || '代码'}\``
      cursorOffset = selectedText ? 0 : -1
      break
    case 'list':
      insertion = `\n- ${selectedText || '列表项'}\n`
      cursorOffset = selectedText ? 0 : -1
      break
  }

  const newContent = 
    currentArticle.value.content.substring(0, selectionStart) +
    insertion +
    currentArticle.value.content.substring(selectionEnd)

  currentArticle.value.content = newContent
  
  await nextTick()
  textarea.focus()
  const newPosition = selectionEnd + insertion.length + cursorOffset
  textarea.setSelectionRange(newPosition, newPosition)
  
  updatePreview()
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.article-manager {
  height: 100%;
  animation: fadeIn 0.3s ease-out;
}

.article-list {
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.list-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.search-bar {
  flex: 1;
  max-width: 400px;
}

.search-bar :deep(.el-input__inner) {
  border-radius: 8px;
  border-color: #e2e8f0;
}

.search-bar :deep(.el-input__inner:focus) {
  border-color: #2563eb;
}

:deep(.el-table) {
  --el-table-border-color: #e2e8f0;
  --el-table-header-background-color: #ffffff;
}

:deep(.el-table__row) {
  transition: all 0.2s ease;
}

:deep(.el-table__row:hover) {
  background-color: #f8fafc !important;
}

.article-title {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.title-text {
  color: #2563eb;
  font-weight: 500;
}

.word-count {
  font-size: 12px;
  color: #64748b;
  background-color: #f1f5f9;
  padding: 2px 8px;
  border-radius: 12px;
}

.article-summary {
  color: #64748b;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-actions {
  display: flex;
  gap: 16px;
}

.article-actions .delete-btn {
  color: #ef4444;
}

.article-editor {
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

.editor-header {
  padding: 24px;
  display: flex;
  gap: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.title-input {
  flex: 1;
}

.title-input :deep(.el-input__inner) {
  font-size: 18px;
  border: none;
  padding: 8px 0;
  border-radius: 0;
  border-bottom: 2px solid transparent;
}

.title-input :deep(.el-input__inner:focus) {
  border-bottom-color: #2563eb;
}

.editor-container {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 24px;
  overflow: hidden;
}

.markdown-editor,
.markdown-preview {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  border-radius: 8px;
}

.markdown-editor {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
}

.markdown-editor :deep(.el-textarea__inner) {
  height: 100%;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #0f172a;
  background-color: transparent;
  border: none;
  resize: none;
}

.markdown-preview {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
}

/* Markdown 预览样式 */
.markdown-preview :deep(h1) {
  font-size: 2em;
  margin-bottom: 0.8em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #e2e8f0;
}

.markdown-preview :deep(h2) {
  font-size: 1.5em;
  margin: 1em 0 0.8em;
}

.markdown-preview :deep(p) {
  margin-bottom: 1.2em;
  line-height: 1.8;
}

.markdown-preview :deep(code) {
  background-color: #f1f5f9;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 0.9em;
  color: #2563eb;
}

.markdown-preview :deep(pre) {
  background-color: #f8fafc;
  padding: 1.2em;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1.2em 0;
  border: 1px solid #e2e8f0;
}

.markdown-preview :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: #0f172a;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #2563eb;
  margin: 1.2em 0;
  padding: 0.8em 1.2em;
  background-color: #f8fafc;
  color: #64748b;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1.2em;
}

.markdown-preview :deep(table) {
  width: 100%;
  margin: 1.2em 0;
  border-collapse: collapse;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  padding: 0.8em;
  border: 1px solid #e2e8f0;
}

.markdown-preview :deep(th) {
  background-color: #f8fafc;
  font-weight: 600;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 自定义滚动条 */
.markdown-editor,
.markdown-preview {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.markdown-editor::-webkit-scrollbar,
.markdown-preview::-webkit-scrollbar {
  width: 6px;
}

.markdown-editor::-webkit-scrollbar-track,
.markdown-preview::-webkit-scrollbar-track {
  background: transparent;
}

.markdown-editor::-webkit-scrollbar-thumb,
.markdown-preview::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
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

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.editor-toolbar {
  padding: 8px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  gap: 8px;
  align-items: center;
  background-color: #ffffff;
  border-radius: 8px 8px 0 0;
  position: relative;
}

.editor-toolbar :deep(.el-button) {
  padding: 6px 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.editor-toolbar :deep(.el-button i) {
  font-style: normal;
  font-weight: 600;
}

.editor-toolbar :deep(.el-divider--vertical) {
  margin: 0;
  height: 20px;
}

.editor-toolbar :deep(.el-button[disabled]) {
  cursor: not-allowed;
  opacity: 0.5;
}

.markdown-editor :deep(.el-textarea__inner) {
  border-radius: 0 0 8px 8px;
}
</style> 