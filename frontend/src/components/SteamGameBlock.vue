<template>
  <div class="steam-game-block">
    <img :src="imageUrl || '/src/assets/loading.gif'" alt="Game Image" class="game-image" />
    <div class="content-wrapper">
      <div class="game-header">
        <h2 class="game-title">{{ title }}</h2>
        <div class="game-rating">
          <span class="rating-item">{{ latest_rating }}</span>
          <span class="rating-item">{{ all_rating }}</span>
        </div>
      </div>
      <p class="game-description">{{ description }}</p>
      <div class="game-footer">
        <div class="game-price" v-html="price"></div>
        <a :href="gameurl" target="_blank" class="game-button">在 Steam 上查看</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  gameurl: String
})

const imageUrl = ref('')
const title = ref('')
const description = ref('')
const latest_rating = ref('')
const all_rating = ref('')
const price = ref('')

const fetchGameDetails = async () => {
  try {
    console.log('正在获取游戏详情...')
    // 使用后端代理
    const response = await axios.get(`http://localhost:5000/api/proxy/steam?url=${encodeURIComponent(props.gameurl)}`)
    console.log('游戏详情获取成功')

    const parser = new DOMParser()
    const doc = parser.parseFromString(response.data, 'text/html')

    // 获取游戏图片
    const imgElement = doc.querySelector('.game_header_image_full')
    if (imgElement) {
      imageUrl.value = imgElement.src
    }

    // 获取游戏标题
    const titleElement = doc.querySelector('#appHubAppName')
    if (titleElement) {
      title.value = titleElement.textContent.trim()
    }

    // 获取游戏简介
    const descriptionElement = doc.querySelector('.game_description_snippet')
    if (descriptionElement) {
      description.value = descriptionElement.textContent.trim()
    }

    // 获取最新评分并翻译
    const latestRatingElement = doc.querySelector('.game_review_summary')
    if (latestRatingElement) {
      const ratingText = latestRatingElement.textContent.trim()
      const translatedRating = translateRating(ratingText)
      latest_rating.value = `近期评价：${translatedRating}`
    }

    // 获取所有评分并翻译
    const allRatingElements = doc.querySelectorAll('.game_review_summary')
    if (allRatingElements.length > 1) {
      const ratingText = allRatingElements[1].textContent.trim()
      const translatedRating = translateRating(ratingText)
      all_rating.value = `总体评价：${translatedRating}`
    }

    // 获取价格并转换为人民币
    const priceElement = doc.querySelector('.game_purchase_discount')
    if (priceElement) {
      const priceHtml = priceElement.outerHTML.trim()
      price.value = convertPriceToRMB(priceHtml)
    } else {
      const regularPriceElement = doc.querySelector('.game_purchase_price')
      if (regularPriceElement) {
        const priceHtml = regularPriceElement.outerHTML.trim()
        price.value = convertPriceToRMB(priceHtml)
      }
    }
  } catch (error) {
    console.error('获取游戏详情失败:', error)
    // 设置默认值
    title.value = '加载失败'
    description.value = '无法获取游戏信息，请稍后再试'
    latest_rating.value = '暂无评分'
    all_rating.value = '暂无评分'
    price.value = '获取失败'
  }
}

// 评分翻译函数
const translateRating = (rating) => {
  const ratingMap = {
    'Overwhelmingly Positive': '好评如潮',
    'Very Positive': '特别好评',
    'Positive': '好评',
    'Mostly Positive': '多半好评',
    'Mixed': '褒贬不一',
    'Mostly Negative': '多半差评',
    'Negative': '差评',
    'Very Negative': '特别差评',
    'Overwhelmingly Negative': '差评如潮'
  }
  
  for (const [eng, chn] of Object.entries(ratingMap)) {
    if (rating.includes(eng)) {
      return rating.replace(eng, chn)
    }
  }
  return rating
}

// 价格转换函数
const convertPriceToRMB = (priceHtml) => {
  // 替换美元符号为人民币符号
  priceHtml = priceHtml.replace(/\$/g, '¥')
  
  // 处理折扣价格
  if (priceHtml.includes('discount_pct')) {
    const discountMatch = priceHtml.match(/discount_pct[^>]*>([^<]+)/)
    if (discountMatch) {
      const discount = discountMatch[1]
      priceHtml = priceHtml.replace(discount, `-${discount}`)
    }
  }
  
  // 处理原价和折扣价
  const priceRegex = /(\d+[.,]\d{2})/g
  return priceHtml.replace(priceRegex, (match) => {
    // 将美元价格转换为人民币（简单的汇率转换，实际应该使用实时汇率）
    const usdPrice = parseFloat(match.replace(',', '.'))
    const rmbPrice = (usdPrice * 7.2).toFixed(2) // 使用固定汇率 7.2
    return rmbPrice
  })
}

onMounted(() => {
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
  position: relative;
  display: flex;
  gap: 1.5rem;
  background: rgba(23, 26, 33, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  overflow: hidden;
  min-height: 190px;
}

.steam-game-block::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #1b2838 0%, #171a21 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 0;
}

.steam-game-block:hover::before {
  opacity: 1;
}

.steam-game-block > * {
  position: relative;
  z-index: 1;
}

.game-image {
  width: 324px;
  height: auto;
  border-radius: 4px;
  object-fit: contain;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.2);
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  min-width: 0;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.game-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.game-rating {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  display: flex;
  gap: 1rem;
}

.rating-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #8f98a0;
}

.rating-item::before {
  content: '';
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #66c0f4;
}

.game-description {
  color: #8f98a0;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 1rem;
  flex-grow: 1;
}

.game-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.game-price {
  font-size: 1.1rem;
  font-weight: 500;
  color: #fff;
}

.game-button {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1.25rem;
  background: linear-gradient(to right, #66c0f4, #4b96cf);
  color: #fff;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.game-button:hover {
  background: linear-gradient(to right, #4b96cf, #3d7ba8);
  transform: translateY(-1px);
}

:deep(.discount_original_price) {
  text-decoration: line-through;
  color: #8f98a0;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

:deep(.discount_pct) {
  color: #beee11;
  background: rgba(190, 238, 17, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 2px;
  font-weight: 600;
  font-size: 0.85rem;
}

:deep(.discount_prices) {
  display: flex;
  align-items: center;
}

:deep(.discount_final_price) {
  color: #beee11;
  font-weight: 600;
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .steam-game-block {
    flex-direction: column;
    padding: 1rem;
  }

  .game-image {
    width: 100%;
    max-width: 324px;
    margin: 0 auto;
  }

  .game-header {
    flex-direction: column;
    gap: 0.75rem;
  }

  .game-rating {
    width: 100%;
    justify-content: flex-start;
  }
}
</style> 