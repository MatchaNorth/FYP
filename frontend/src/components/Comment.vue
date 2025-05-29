<template>
  <div class="comment-list">
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <div :class="['comment-card', { 'child-level-2': level === 2 }]">
        <div class="comment-header">
          <el-avatar :src="comment.avatar" size="44" shape="circle" />
          <div class="header-info">
            <span class="nickname">{{ comment.nickname }}</span>
            <span class="floor">{{ comment.floor }}楼</span>
            <span class="created-at">{{ comment.created_at.slice(0, 16).replace('T', ' ') }}</span>
          </div>
        </div>
        <div class="comment-content-card">
          <template v-if="level > 2 && comment.reply_nickname">
            <span class="reply-to">回复 <b>{{ comment.reply_nickname }}</b>：</span>
          </template>
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
      </div>
      <!-- 子评论递归 -->
      <div v-if="comment.children && comment.children.length"
           :class="level === 2 ? 'child-comments' : ''">
        <Comment 
          :comments="comment.children" 
          :article-id="articleId" 
          :level="level + 1" 
          @refresh="() => emit('refresh')" 
        />
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
//TODO：删除文章时删除评论
//TODO：删除评论时删除点赞
//TODO：点赞后不能点赞
//TODO: 封禁用户不能进行评论和点赞
//TODO：管理员管理评论
//TODO：评论可以被单独删除，其子评论也会被删除，点赞也会被删除但是楼号不变。自己评论会有删除按钮，其他评论只有举报功能。
import { ref, defineProps, defineEmits, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  comments: Array,
  articleId: Number,
  showInput: {
    type: Boolean,
    default: false
  },
  level: {
    type: Number,
    default: 1
  }
})
const emit = defineEmits(['refresh'])

const replyingTo = ref(null)
const replyContent = ref('')
const newComment = ref('')
const isBanned = ref(false)

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const res = await axios.get('http://localhost:5000/api/user/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.data && res.data.data) {
        isBanned.value = res.data.data.is_banned
      }
    } catch (e) {
      isBanned.value = false
    }
  }
})

const showReplyBox = (comment) => {
  replyingTo.value = comment.id
  replyContent.value = ''
}
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}
const submitReply = async (comment) => {
  if (isBanned.value) {
    ElMessage.error('您的账号已被封禁，无法进行此操作')
    return
  }
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
  if (isBanned.value) {
    ElMessage.error('您的账号已被封禁，无法进行此操作')
    return
  }
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
    // 更新评论的点赞状态
    comment.liked = res.data.liked
    emit('refresh')
  } catch (e) {
    if (e.response && e.response.status === 403) {
      ElMessage.error(e.response.data.message || '您的账号已被封禁，无法进行此操作')
    } else {
      ElMessage.error('操作失败')
    }
  }
}
</script>

<style scoped>
.comment-list {
  margin-top: 24px;
  background: transparent;
  padding: 0;
}
.comment-item {
  margin-bottom: 24px;
}
.comment-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  padding: 20px 24px 12px 24px;
  transition: box-shadow 0.2s;
}
.comment-card:hover {
  box-shadow: 0 4px 20px rgba(37,99,235,0.10);
}
.child-comments {
  margin-left: 48px;
  border-left: 2px solid #e3e8f7;
  padding-left: 20px;
  background: #f8faff;
  border-radius: 8px;
  margin-top: 12px;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 6px;
}
.header-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.nickname {
  font-weight: 700;
  color: #2563eb;
  font-size: 16px;
}
.floor {
  color: #b6b6b6;
  font-size: 14px;
}
.created-at {
  color: #c7c7c7;
  font-size: 13px;
}
.comment-content-card {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 15px;
  margin-bottom: 8px;
  word-break: break-all;
}
.comment-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-bottom: 4px;
}
.el-button[type="text"] {
  color: #8a8a8a;
  font-size: 14px;
  padding: 0 8px;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
}
.el-button[type="text"]:hover {
  color: #2563eb;
  background: #f0f4ff;
}
.el-icon-thumb.liked {
  color: #f59e42;
}
.reply-box {
  margin: 10px 0 0 0;
  display: flex;
  gap: 8px;
}
.comment-input-box {
  margin-top: 36px;
  display: flex;
  gap: 8px;
  background: #f7f8fa;
  border-radius: 10px;
  padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(37,99,235,0.04);
}
.el-button[type="primary"] {
  background: #2563eb;
  color: #fff;
  border-radius: 6px;
  font-weight: 600;
  transition: background 0.2s;
}
.el-button[type="primary"]:hover {
  background: #1d4ed8;
}
@media (max-width: 768px) {
  .comment-card {
    padding: 14px 8px 8px 8px;
  }
  .child-comments {
    margin-left: 12px;
    padding-left: 8px;
  }
  .comment-input-box {
    padding: 8px 4px;
  }
}
.comment-card.child-level-2 {
  margin-left: 48px;
  border-left: 2px solid #e3e8f7;
  background: #f8faff;
  border-radius: 8px;
  margin-top: 12px;
}
.reply-to {
  color: #2563eb;
  font-size: 14px;
  margin-right: 4px;
}
</style>
