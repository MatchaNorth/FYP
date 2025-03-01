<template>
  <div class="analytics-container">
    <div class="analytics-header">
      <h2>文章统计</h2>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="refreshData">
          <i class="el-icon-refresh"></i>
          刷新数据
        </el-button>
      </div>
    </div>

    <div class="analytics-grid">
      <!-- 阅读量趋势图 -->
      <div class="chart-card" ref="viewsChart">
        <div class="chart-header">
          <h3>阅读量趋势</h3>
          <p>近30天阅读量变化</p>
        </div>
        <div class="chart-content" ref="viewsChartContent"></div>
      </div>

      <!-- 点赞数趋势图 -->
      <div class="chart-card" ref="likesChart">
        <div class="chart-header">
          <h3>点赞数趋势</h3>
          <p>近30天点赞数变化</p>
        </div>
        <div class="chart-content" ref="likesChartContent"></div>
      </div>

      <!-- 文章状态分布 -->
      <div class="chart-card" ref="statusChart">
        <div class="chart-header">
          <h3>文章状态分布</h3>
          <p>已发布vs草稿箱</p>
        </div>
        <div class="chart-content" ref="statusChartContent"></div>
      </div>

      <!-- 热门文章排行 -->
      <div class="chart-card popular-articles">
        <div class="chart-header">
          <h3>热门文章排行</h3>
          <p>按阅读量排序</p>
        </div>
        <div class="chart-content">
          <transition-group name="list" tag="ul" class="popular-list">
            <li v-for="(article, index) in popularArticles" :key="article.title" class="popular-item">
              <div class="rank">{{ index + 1 }}</div>
              <div class="article-info">
                <h4>{{ article.title }}</h4>
                <p>{{ article.created_at }} · {{ article.views }}次阅读 · {{ article.likes }}个点赞</p>
              </div>
            </li>
          </transition-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import gsap from 'gsap'

const viewsChartContent = ref(null)
const likesChartContent = ref(null)
const statusChartContent = ref(null)
const popularArticles = ref([])

let viewsChart = null
let likesChart = null
let statusChart = null

// 初始化图表
const initCharts = () => {
  viewsChart = echarts.init(viewsChartContent.value)
  likesChart = echarts.init(likesChartContent.value)
  statusChart = echarts.init(statusChartContent.value)
  
  // 设置响应式
  window.addEventListener('resize', handleResize)
}

// 处理窗口大小变化
const handleResize = () => {
  viewsChart?.resize()
  likesChart?.resize()
  statusChart?.resize()
}

// 获取统计数据
const fetchAnalytics = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/articles/analytics', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.code === 200) {
      const { daily_views, daily_likes, article_status, popular_articles } = response.data.data
      
      // 更新热门文章列表（带动画）
      gsap.to(popularArticles, {
        duration: 0.5,
        opacity: 0,
        onComplete: () => {
          popularArticles.value = popular_articles
          gsap.to(popularArticles, {
            duration: 0.5,
            opacity: 1,
            stagger: 0.1
          })
        }
      })
      
      // 更新阅读量趋势图
      updateViewsChart(daily_views)
      
      // 更新点赞数趋势图
      updateLikesChart(daily_likes)
      
      // 更新文章状态分布图
      updateStatusChart(article_status)
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 更新阅读量趋势图
const updateViewsChart = (data) => {
  const dates = data.map(item => item.date)
  const views = data.map(item => item.views)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '阅读量',
      type: 'line',
      smooth: true,
      data: views,
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64,158,255,0.3)' },
          { offset: 1, color: 'rgba(64,158,255,0.1)' }
        ])
      },
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicInOut'
    }]
  }
  
  viewsChart.setOption(option)
}

// 更新点赞数趋势图
const updateLikesChart = (data) => {
  const dates = data.map(item => item.date)
  const likes = data.map(item => item.likes)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '点赞数',
      type: 'bar',
      data: likes,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ff9a9e' },
          { offset: 1, color: '#fad0c4' }
        ])
      },
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicInOut'
    }]
  }
  
  likesChart.setOption(option)
}

// 更新文章状态分布图
const updateStatusChart = (data) => {
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '文章状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '20',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: data.map(item => ({
        name: item.status === 'published' ? '已发布' : '草稿',
        value: item.count,
        itemStyle: {
          color: item.status === 'published' ? '#67C23A' : '#909399'
        }
      })),
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicInOut'
    }]
  }
  
  statusChart.setOption(option)
}

// 刷新数据
const refreshData = () => {
  fetchAnalytics()
}

onMounted(() => {
  initCharts()
  fetchAnalytics()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  viewsChart?.dispose()
  likesChart?.dispose()
  statusChart?.dispose()
})
</script>

<style scoped>
.analytics-container {
  padding: 24px;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.analytics-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.chart-header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.chart-content {
  height: 300px;
}

.popular-articles .chart-content {
  height: auto;
  max-height: 300px;
  overflow-y: auto;
}

.popular-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.popular-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: rgba(var(--primary-rgb), 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.popular-item:hover {
  transform: translateX(8px);
  background: rgba(var(--primary-rgb), 0.1);
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 12px;
}

.article-info {
  flex: 1;
}

.article-info h4 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.article-info p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 列表动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}
</style> 