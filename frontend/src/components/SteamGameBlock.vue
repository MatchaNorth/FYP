<template>
  <div class="steam-game-block">
    <div class="simple-info">
      <h2 class="game-title">{{ title }}</h2>
      <div class="game-rating">
        <p>近期评价：{{ latest_rating }}</p>
        <p>全部评价：{{ all_rating }}</p>
      </div>
    </div>
    <div class="game-info">
      <img :src="imageUrl || '/src/assets/loading.gif'" alt="Game Image" class="game-image" />
      <p class="game-description">{{ description }}</p>
      <div class="detail-info">
        <div class="game-price" v-html="price"></div>
        <a :href="gameurl" target="_blank" class="game-button">查看详情</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  gameurl: {
    type: String,
    required: true
  }
})

const imageUrl = ref('')
const title = ref('')
const description = ref('')
const latest_rating = ref('')
const all_rating = ref('')
const price = ref('')

const fetchGameDetails = async () => {
  try {
    console.log('正在获取游戏详情...', props.gameurl)
    const proxyUrl = 'https://api.allorigins.win/get?url='
    const encodedUrl = encodeURIComponent(props.gameurl)
    console.log('编码后的URL:', proxyUrl + encodedUrl)
    
    const response = await axios.get(proxyUrl + encodedUrl)
    console.log('游戏详情获取成功', response.data)

    if (!response.data.contents) {
      throw new Error('无法获取游戏内容')
    }

    const parser = new DOMParser()
    const doc = parser.parseFromString(response.data.contents, 'text/html')

    // 获取游戏图片
    const imgElement = doc.querySelector('.game_header_image_full')
    if (imgElement) {
      imageUrl.value = imgElement.src
      console.log('获取到游戏图片:', imageUrl.value)
    } else {
      console.warn('未找到游戏图片')
    }

    // 获取游戏标题
    const titleElement = doc.querySelector('#appHubAppName')
    if (titleElement) {
      title.value = titleElement.textContent.trim()
      console.log('获取到游戏标题:', title.value)
    } else {
      console.warn('未找到游戏标题')
    }

    // 获取游戏简介
    const descriptionElement = doc.querySelector('.game_description_snippet')
    if (descriptionElement) {
      description.value = descriptionElement.textContent.trim()
      console.log('获取到游戏简介:', description.value)
    } else {
      console.warn('未找到游戏简介')
    }

    // 获取最新评分
    const latestRatingElement = doc.querySelector('.game_review_summary')
    if (latestRatingElement) {
      latest_rating.value = latestRatingElement.textContent.trim()
      console.log('获取到最新评分:', latest_rating.value)
    } else {
      console.warn('未找到最新评分')
    }

    // 获取所有评分
    const allRatingElements = doc.querySelectorAll('.game_review_summary')
    if (allRatingElements.length > 1) {
      all_rating.value = allRatingElements[1].textContent.trim()
      console.log('获取到总体评分:', all_rating.value)
    } else {
      console.warn('未找到总体评分')
    }

    // 获取价格
    const priceElement = doc.querySelector('.game_purchase_discount')
    if (priceElement) {
      price.value = priceElement.outerHTML.trim()
      console.log('获取到折扣价格')
    } else {
      const regularPriceElement = doc.querySelector('.game_purchase_price')
      if (regularPriceElement) {
        price.value = regularPriceElement.outerHTML.trim()
        console.log('获取到常规价格')
      } else {
        console.warn('未找到价格信息')
      }
    }
  } catch (error) {
    console.error('获取游戏详情失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      gameUrl: props.gameurl
    })
    
    // 设置默认值
    title.value = '加载失败'
    description.value = '无法获取游戏信息'
    latest_rating.value = '暂无评分'
    all_rating.value = '暂无评分'
    price.value = '获取失败'
  }
}

onMounted(() => {
  console.log('SteamGameBlock mounted with URL:', props.gameurl)
  fetchGameDetails()
})
</script>

<style scoped>
@keyframes gradientBackground {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.steam-game-block {
  display: flex;
  flex-direction: column;
  background: linear-gradient(145deg, #1b2838, #f49a66, #33a6bb);
  justify-content: space-between;
  background-size: 600% 600%;
  animation: gradientBackground 10s ease infinite;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s;
  width: 100%;
  min-height: 300px;
  margin: 1rem 0;
  padding: 1rem;
}

.steam-game-block:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.simple-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 1rem;
  background-color: rgba(204, 209, 214, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  color: whitesmoke;
  margin-bottom: 1rem;
}

.game-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.game-rating {
  text-align: right;
}

.game-rating p {
  margin: 0.25rem 0;
}

.game-info {
  display: grid;
  grid-template-columns: 324px 1fr;
  gap: 1rem;
  align-items: start;
}

.game-image {
  width: 324px;
  height: 151px;
  border-radius: 10px;
  object-fit: cover;
}

.game-description {
  font-size: 0.9rem;
  line-height: 1.5;
  color: #c7d5e0;
  margin: 0;
}

.detail-info {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.game-price {
  font-size: 1.2rem;
  font-weight: bold;
}

.game-button {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background-color: #66a4f4;
  color: #fff;
  text-decoration: none;
  text-align: center;
  border-radius: 5px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.game-button:hover {
  background-color: #4a9fd1;
  transform: translateY(-2px);
}

:deep(.discount_original_price) {
  text-decoration: line-through;
  color: #6f777c;
  font-size: 0.9rem;
}

:deep(.discount_pct) {
  color: #1ac028;
  font-weight: bold;
  margin: 0 0.5rem;
}

:deep(.discount_prices) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

:deep(.discount_final_price) {
  font-size: 1.3rem;
  font-weight: bold;
  color: #fff;
}
</style> 