<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">中医知识库</h1>
      <p class="page-desc">经典医典检索，支持中药、方剂、经络、体质等知识查询</p>
    </div>

    <!-- 搜索区 -->
    <div class="search-section">
      <div class="search-box card">
        <div class="search-row">
          <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input
                class="search-input"
                v-model="query"
                placeholder="输入您想了解的中医问题，如：肝气郁结有什么症状？"
                @keydown.enter="doSearch"
            />
          </div>
          <button class="btn btn-primary" @click="doSearch" :disabled="!query.trim()">检索</button>
        </div>
        <div class="hot-queries">
          <span class="hot-label">热门问题：</span>
          <span class="hot-item" v-for="h in hotQuestions" :key="h" @click="quickSearch(h)">{{ h }}</span>
        </div>
      </div>
    </div>

    <!-- 结果区 -->
    <div v-if="hasSearched" class="results-section">
      <div class="results-header">
        <div class="category-filters">
          <button class="filter-btn" :class="{ active: activeFilter === '' }" @click="activeFilter = ''">全部</button>
          <button class="filter-btn" :class="{ active: activeFilter === '中药' }" @click="activeFilter = '中药'">中药</button>
          <button class="filter-btn" :class="{ active: activeFilter === '方剂' }" @click="activeFilter = '方剂'">方剂</button>
          <button class="filter-btn" :class="{ active: activeFilter === '体质' }" @click="activeFilter = '体质'">体质</button>
          <button class="filter-btn" :class="{ active: activeFilter === '病症' }" @click="activeFilter = '病症'">病症</button>
        </div>
      </div>

      <div class="results-list">
        <div class="result-card card" v-for="(r, i) in filteredResults" :key="i">
          <div class="result-header">
            <span class="category-tag" :style="{ background: r.color + '22', color: r.color, borderColor: r.color }">
              {{ r.category }}
            </span>
            <h3 class="result-title">{{ r.title }}</h3>
          </div>
          <p class="result-content">{{ r.excerpt }}</p>
          <div class="result-footer">
            <span class="source-text">📖 {{ r.source }}</span>
            <div class="match-rate">
              <span>匹配度</span>
              <div class="rate-bar">
                <div class="rate-fill" :style="{ width: (r.score * 100).toFixed(0) + '%', background: r.color }"></div>
              </div>
              <span class="rate-value">{{ (r.score * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识分类 -->
    <div v-if="!hasSearched" class="categories-section">
      <div class="section-header">
        <div class="section-tag">知识分类</div>
        <h2 class="section-title">经典医典分类浏览</h2>
      </div>
      <div class="category-grid">
        <div class="cat-card card" v-for="cat in categories" :key="cat.name" @click="quickSearch(cat.query)">
          <div class="cat-icon">{{ cat.icon }}</div>
          <div class="cat-name">{{ cat.name }}</div>
          <div class="cat-count">{{ cat.count }} 条</div>
          <div class="cat-examples">{{ cat.examples }}</div>
        </div>
      </div>
    </div>

    <!-- 检索说明 -->
    <div v-if="!hasSearched" class="explain-section card">
      <h3 class="explain-title">📚 检索说明</h3>
      <div class="explain-steps">
        <div class="step-item" v-for="(s, i) in explainSteps" :key="i">
          <div class="step-num">{{ i + 1 }}</div>
          <div class="step-icon">{{ s.icon }}</div>
          <div class="step-text">{{ s.text }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const query = ref('')
const hasSearched = ref(false)
const activeFilter = ref('')

const hotQuestions = [
  '肝气郁结的症状和治法',
  '如何判断自己是哪种体质',
  '柴胡疏肝散的组成和功效',
  '湿热体质如何调理',
]

const categories = [
  { name: '中药', icon: '🌿', count: 486, examples: '人参·黄芪·当归·枸杞', query: '中药功效与配伍' },
  { name: '方剂', icon: '📜', count: 328, examples: '四君子汤·柴胡疏肝散', query: '经典方剂组成与主治' },
  { name: '经络', icon: '🧘', count: 264, examples: '足阳明胃经·手太阴肺经', query: '经络循行与主治' },
  { name: '体质', icon: '🔬', count: 156, examples: '九种体质分类与判定', query: '中医体质分类标准' },
  { name: '病症', icon: '🏥', count: 412, examples: '感冒·咳嗽·失眠·头痛', query: '常见病症辨证论治' },
  { name: '养生', icon: '🍃', count: 198, examples: '食疗·穴位·运动·情志', query: '中医养生保健方法' },
]

const explainSteps = [
  { icon: '💬', text: '输入自然语言问题' },
  { icon: '🔍', text: '检索相关知识' },
  { icon: '📝', text: '整理生成答案' },
  { icon: '📖', text: '附文献来源' },
]

const mockResults = [
  { category: '病症', title: '肝气郁结证', excerpt: '肝气郁结证是指肝的疏泄功能失常，气机郁滞所表现的证候。多因情志抑郁、愤怒伤肝所致。临床表现为胸胁、少腹胀痛或窜痛，症状随情绪变化而增减，脉弦等。', source: '《中医内科学》· 人民卫生出版社', score: 0.96, color: '#9F2A2A' },
  { category: '方剂', title: '柴胡疏肝散', excerpt: '柴胡疏肝散出自《景岳全书》，功用：疏肝理气，活血止痛。主治：肝气郁滞证。组成：柴胡12g，白芍15g、川芎10g、香附10g、枳壳10g、陈皮8g、炙甘草6g。', source: '《景岳全书》', score: 0.92, color: '#6B8E23' },
  { category: '体质', title: '气郁质特征与调养', excerpt: '气郁质人群特征：神情抑郁，忧虑脆弱，失眠多梦，对精神刺激适应能力较差。饮食宜疏肝理气，如玫瑰花茶、陈皮、佛手等。', source: '《中医体质分类与判定》', score: 0.88, color: '#8B5CF6' },
  { category: '中药', title: '川芎的功效与配伍', excerpt: '川芎性辛温，归肝、胆、心包经。功效：活血行气，祛风止痛。临床用于血瘀气滞痛证、头痛、风湿痹痛等。反藜芦，畏硝石、滑石，恶黄芪。', source: '《临床中药学》', score: 0.85, color: '#B8860B' },
  { category: '中药', title: '当归的临床应用', excerpt: '当归性甘辛温，归肝、心、脾经。功效：补血活血，调经止痛，润肠通便。为补血要药，用于血虚诸证尤宜妇科。当归分归头、归身、归尾，功能各有侧重。', source: '《临床中药学》', score: 0.81, color: '#B8860B' },
  { category: '中药', title: '黄芪的补气功效', excerpt: '黄芪性甘微温，归脾、肺经。功效：补气升阳，益卫固表，利水消肿，生津养血。用于脾肺气虚、中气下陷，气虚外感等。', source: '《临床中药学》', score: 0.80, color: '#B8860B' },
  { category: '方剂', title: '四君子汤', excerpt: '四君子汤出自《太平惠民和剂局方》，功用：益气健脾。主治：脾胃气虚证。组成：人参10g，白术9g、茯苓9g、炙甘草6g。', source: '《太平惠民和剂局方》', score: 0.75, color: '#6B8E23' },
  { category: '体质', title: '痰湿质特征与调养', excerpt: '痰湿质人群特征：形体肥胖、腹部肥满、面部皮肤油脂较多、痰多、易疲倦。饮食宜清淡、少油腻、利水渗湿，如冬瓜、薏苡仁、赤小豆等。', source: '《中医体质分类与判定》', score: 0.75, color: '#8B5CF6' },
]

const results = ref([])

const filteredResults = computed(() => {
  if (!activeFilter.value) return results.value
  return results.value.filter(r => r.category === activeFilter.value)
})

function doSearch() {
  if (!query.value.trim()) return
  hasSearched.value = true
  activeFilter.value = ''
  results.value = mockResults.map(r => ({ ...r, title: r.title }))
}

function quickSearch(q) {
  query.value = q
  doSearch()
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  font-family: var(--font-serif);
  color: var(--primary-brown);
  margin-bottom: 12px;
}

.page-desc {
  font-size: 14px;
  color: var(--text-secondary);
  font-family: var(--font-sans);
}

/* Search */
.search-section {
  margin-bottom: 32px;
}

.search-box {
  padding: 20px;
}

.search-row {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.search-input-wrap {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-main);
  color: var(--text-main);
  font-size: 14px;
  font-family: var(--font-sans);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-brown);
}

.hot-queries {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hot-label {
  font-size: 12px;
  color: var(--text-muted);
}

.hot-item {
  font-size: 12px;
  padding: 4px 10px;
  background: var(--bg-soft);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.hot-item:hover {
  background: var(--bg-main);
  color: var(--primary-brown);
}

/* Results */
.results-section {
  margin-bottom: 40px;
}

.results-header {
  margin-bottom: 20px;
}

.category-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: var(--bg-soft);
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: var(--bg-main);
  color: var(--primary-brown);
}

.filter-btn.active {
  background: var(--accent-light);
  color: var(--primary-red);
  border-color: var(--primary-red);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  padding: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.category-tag {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid;
  font-family: var(--font-sans);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.result-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 16px;
}

.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-text {
  font-size: 12px;
  color: var(--text-muted);
}

.match-rate {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.rate-bar {
  width: 80px;
  height: 4px;
  background: var(--bg-soft);
  border-radius: 2px;
  overflow: hidden;
}

.rate-fill {
  height: 100%;
  border-radius: 2px;
}

.rate-value {
  font-weight: 600;
  color: var(--text-secondary);
}

/* Categories */
.categories-section {
  margin-bottom: 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 32px;
}

.section-tag {
  display: inline-block;
  padding: 4px 12px;
  background: var(--accent-light);
  color: var(--primary-red);
  font-size: 12px;
  font-family: var(--font-sans);
  border-radius: var(--radius-sm);
  margin-bottom: 10px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  font-family: var(--font-serif);
  color: var(--text-main);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.cat-card {
  text-align: center;
  padding: 20px 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.cat-card:hover {
  background: var(--bg-soft);
  border-color: var(--primary-brown);
}

.cat-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.cat-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 6px;
}

.cat-count {
  font-size: 11px;
  color: var(--primary-brown);
  font-family: var(--font-sans);
  margin-bottom: 8px;
}

.cat-examples {
  font-size: 10px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Explain */
.explain-section {
  padding: 24px;
  text-align: center;
}

.explain-title {
  font-size: 16px;
  color: var(--primary-brown);
  margin-bottom: 20px;
}

.explain-steps {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-num {
  width: 24px;
  height: 24px;
  background: var(--primary-brown);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.step-icon {
  font-size: 24px;
}

.step-text {
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 900px) {
  .category-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .explain-steps {
    flex-wrap: wrap;
    gap: 20px;
  }
}
</style>
