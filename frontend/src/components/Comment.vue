<template>
  <div class="comment-list">
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <div class="comment-header">
        <el-avatar :src="comment.avatar" size="32" />
        <span class="nickname">{{ comment.nickname }}</span>
        <span class="floor">{{ comment.floor }}楼</span>
      </div>
      <div class="comment-content">
        <span v-if="comment.parent_id && comment.reply_nickname">回复 <b>{{ comment.reply_nickname }}</b>：</span>
        {{ comment.content }}
      </div>
      <div class="comment-actions">
        <el-button size="small" type="text" @click="handleLike(comment)">
          <i :class="['el-icon-thumb', { liked: comment.liked }]" />
          <span>{{ comment.liked ? '已赞' : '点赞' }}</span>
        </el-button>
        <el-button size="small" type="text" @click="showReplyBox(comment)">回复</el-button>
      </div>
      <!-- 回复框 -->
      <div v-if="replyingTo === comment.id" class="reply-box">
        <el-input v-model="replyContent" placeholder="回复内容..." size="small" />
        <el-button size="small" type="primary" @click="submitReply(comment)">发送</el-button>
        <el-button size="small" @click="cancelReply">取消</el-button>
      </div>
      <!-- 子评论递归 -->
      <div class="child-comments" v-if="comment.children && comment.children.length">
        <Comment :comments="comment.children" :article-id="articleId" @refresh="refresh" />
      </div>
    </div>
    <!-- 发表评论框（仅顶层） -->
    <div v-if="showInput" class="comment-input-box">
      <el-input v-model="newComment" placeholder="说点什么..." />
      <el-button type="primary" @click="submitComment">发表评论</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  comments: Array,
  articleId: Number,
  showInput: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['refresh'])

const replyingTo = ref(null)
const replyContent = ref('')
const newComment = ref('')

const showReplyBox = (comment) => {
  replyingTo.value = comment.id
  replyContent.value = ''
}
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}
const submitReply = async (comment) => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  try {
    const token = localStorage.getItem('token')
    await axios.post(`http://localhost:5000/api/articles/${props.articleId}/comments`, {
      content: replyContent.value,
      parent_id: comment.id
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    ElMessage.success('回复成功')
    cancelReply()
    emit('refresh')
  } catch (e) {
    ElMessage.error('回复失败')
  }
}
const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  try {
    const token = localStorage.getItem('token')
    await axios.post(`http://localhost:5000/api/articles/${props.articleId}/comments`, {
      content: newComment.value
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    ElMessage.success('评论成功')
    newComment.value = ''
    emit('refresh')
  } catch (e) {
    ElMessage.error('评论失败')
  }
}
const handleLike = async (comment) => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post(`http://localhost:5000/api/comments/${comment.id}/like`, {}, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    ElMessage.success(res.data.message)
    emit('refresh')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}
</script>

<style scoped>
.comment-list {
  margin-top: 24px;
}
.comment-item {
  border-bottom: 1px solid #eee;
  padding: 16px 0;
  margin-left: 0;
}
.child-comments {
  margin-left: 32px;
  border-left: 2px solid #f0f0f0;
  padding-left: 16px;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nickname {
  font-weight: 600;
  color: #2563eb;
}
.floor {
  color: #aaa;
  margin-left: 8px;
}
.comment-content {
  margin: 8px 0 4px 0;
  font-size: 15px;
}
.comment-actions {
  display: flex;
  gap: 12px;
}
.reply-box {
  margin: 8px 0 0 0;
  display: flex;
  gap: 8px;
}
.comment-input-box {
  margin-top: 24px;
  display: flex;
  gap: 8px;
}
.el-icon-thumb.liked {
  color: #f59e42;
}
</style>
