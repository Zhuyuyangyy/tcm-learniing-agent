<template>
  <div class="kb-page">
    <div class="page-bg"></div>
    <div class="bg-mountain left"></div>
    <div class="bg-mountain right"></div>
    <div class="bg-bamboo right-top"></div>
    <div class="bg-bamboo right-mid"></div>
    <div class="bg-pavilion left-bottom"></div>
    <div class="bg-cloud cloud-left"></div>
    <div class="bg-cloud cloud-right"></div>
    <div class="bg-bird"></div>

    <section class="hero">
      <div class="hero-line">
        <span class="line"></span>
        <span class="curl">〰</span>
        <h1>中医知识库</h1>
        <span class="curl">〰</span>
        <span class="line"></span>
      </div>
      <p>经典医典检索，支持中药、方剂、经络、体质等知识查询</p>
    </section>

    <section class="search-section">
      <div class="search-card">
        <div class="search-row">
          <div class="search-input-wrap">
            <i class="fa-solid fa-magnifying-glass search-icon"></i>
            <input
              v-model="query"
              class="search-input"
              placeholder="输入您想了解的中医问题，如：肝气郁结有什么症状？"
              @keydown.enter="doSearch"
            />
          </div>
          <button class="search-btn" @click="doSearch" :disabled="!query.trim()">检索</button>
        </div>
        <div class="hot-row">
          <span class="hot-label">热门问题：</span>
          <button
            v-for="item in hotQuestions"
            :key="item"
            type="button"
            class="hot-item"
            @click="quickSearch(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>
    </section>

    <section v-if="!hasSearched" class="browse-section">
      <div class="section-chip-row">
        <span class="section-chip-line"></span>
        <span class="section-chip-mark">◇</span>
        <span class="section-chip">知识分类</span>
        <span class="section-chip-mark">◇</span>
        <span class="section-chip-line"></span>
      </div>

      <div class="section-title-row">
        <span class="title-line"></span>
        <span class="title-mark">◇</span>
        <h2>经典医典分类浏览</h2>
        <span class="title-mark">◇</span>
        <span class="title-line"></span>
      </div>

      <div class="category-grid">
        <button
          v-for="item in categories"
          :key="item.name"
          type="button"
          class="category-card"
          @click="quickSearch(item.query)"
        >
          <span class="category-icon">
            <i :class="item.icon"></i>
          </span>
          <strong>{{ item.name }}</strong>
          <span class="category-count">{{ item.count }} 条</span>
          <em>{{ item.examples }}</em>
        </button>
      </div>

      <div class="guide-card">
        <h3>
          <i class="fa-solid fa-book"></i>
          检索说明
        </h3>
        <div class="guide-grid">
          <div v-for="item in explainSteps" :key="item.text" class="guide-item">
            <span class="guide-icon">
              <i :class="item.icon"></i>
            </span>
            <strong>{{ item.text }}</strong>
            <em>{{ item.desc }}</em>
          </div>
        </div>
      </div>
    </section>

    <section v-else class="result-section">
      <div class="result-toolbar">
        <div class="filter-group">
          <button class="filter-btn" :class="{ active: activeFilter === '' }" @click="activeFilter = ''">全部</button>
          <button class="filter-btn" :class="{ active: activeFilter === '中药' }" @click="activeFilter = '中药'">中药</button>
          <button class="filter-btn" :class="{ active: activeFilter === '方剂' }" @click="activeFilter = '方剂'">方剂</button>
          <button class="filter-btn" :class="{ active: activeFilter === '体质' }" @click="activeFilter = '体质'">体质</button>
          <button class="filter-btn" :class="{ active: activeFilter === '病症' }" @click="activeFilter = '病症'">病症</button>
        </div>
        <button class="back-btn" @click="resetSearch">返回分类</button>
      </div>

      <div class="result-list">
        <article v-for="(item, index) in filteredResults" :key="index" class="result-card">
          <div class="result-head">
            <span class="result-tag" :style="{ color: item.color, borderColor: item.color, background: `${item.color}12` }">
              {{ item.category }}
            </span>
            <h3>{{ item.title }}</h3>
          </div>
          <p class="result-body">{{ item.excerpt }}</p>
          <div class="result-foot">
            <span class="result-source">📖 {{ item.source }}</span>
            <div class="result-score">
              <span>匹配度</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: `${(item.score * 100).toFixed(0)}%`, background: item.color }"></div>
              </div>
              <strong>{{ (item.score * 100).toFixed(0) }}%</strong>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const query = ref('')
const hasSearched = ref(false)
const activeFilter = ref('')
const results = ref([])

const hotQuestions = [
  '肝气郁结的症状和治法',
  '如何判断自己是哪种体质',
  '柴胡疏肝散的组成和功效',
  '湿热体质如何调理'
]

const categories = [
  { name: '中药', icon: 'fa-solid fa-seedling', count: 486, examples: '人参 · 黄芪 · 当归 · 枸杞', query: '中药功效与配伍' },
  { name: '方剂', icon: 'fa-regular fa-note-sticky', count: 328, examples: '四君子汤 · 柴胡疏肝散', query: '经典方剂组成与主治' },
  { name: '经络', icon: 'fa-solid fa-person', count: 264, examples: '足阳明胃经 · 手太阴肺经', query: '经络循行与主治' },
  { name: '体质', icon: 'fa-solid fa-microscope', count: 156, examples: '九种体质分类与判定', query: '中医体质分类标准' },
  { name: '病症', icon: 'fa-solid fa-hospital', count: 412, examples: '感冒 · 咳嗽 · 失眠 · 头痛', query: '常见病症辨证论治' },
  { name: '养生', icon: 'fa-solid fa-leaf', count: 198, examples: '食疗 · 穴位 · 运动 · 情志', query: '中医养生保健方法' }
]

const explainSteps = [
  { icon: 'fa-regular fa-comment-dots', text: '输入自然语言问题', desc: '用口语化描述更准确' },
  { icon: 'fa-solid fa-magnifying-glass', text: '检索相关知识', desc: '智能匹配中医知识库' },
  { icon: 'fa-regular fa-pen-to-square', text: '整理生成答案', desc: '结构化呈现易于理解' },
  { icon: 'fa-regular fa-book-open', text: '附文献来源', desc: '可追溯权威出处' }
]

const mockResults = [
  { category: '病症', title: '肝气郁结证', excerpt: '肝气郁结证是指肝的疏泄功能失常，气机郁滞所表现的证候。多因情志抑郁、愤怒伤肝所致。临床表现为胸胁、少腹胀痛或窜痛，症状随情绪变化而增减，脉弦等。', source: '《中医内科学》· 人民卫生出版社', score: 0.96, color: '#9F2A2A' },
  { category: '方剂', title: '柴胡疏肝散', excerpt: '柴胡疏肝散出自《景岳全书》，功用：疏肝理气，活血止痛。主治：肝气郁滞证。组成：柴胡12g，白芍15g、川芎10g、香附10g、枳壳10g、陈皮8g、炙甘草6g。', source: '《景岳全书》', score: 0.92, color: '#6B8E23' },
  { category: '体质', title: '气郁质特征与调养', excerpt: '气郁质人群特征：神情抑郁，忧虑脆弱，失眠多梦，对精神刺激适应能力较差。饮食宜疏肝理气，如玫瑰花茶、陈皮、佛手等。', source: '《中医体质分类与判定》', score: 0.88, color: '#7E6AA8' },
  { category: '中药', title: '川芎的功效与配伍', excerpt: '川芎性辛温，归肝、胆、心包经。功效：活血行气，祛风止痛。临床用于血瘀气滞痛证、头痛、风湿痹痛等。反藜芦，畏硝石、滑石，恶黄芪。', source: '《临床中药学》', score: 0.85, color: '#B8860B' }
]

const filteredResults = computed(() => {
  if (!activeFilter.value) return results.value
  return results.value.filter((item) => item.category === activeFilter.value)
})

function doSearch() {
  if (!query.value.trim()) return
  hasSearched.value = true
  activeFilter.value = ''
  results.value = mockResults.map((item) => ({ ...item }))
}

function quickSearch(text) {
  query.value = text
  doSearch()
}

function resetSearch() {
  hasSearched.value = false
  activeFilter.value = ''
  results.value = []
}
</script>

<style scoped>
.kb-page {
  position: relative;
  max-width: 1280px;
  margin: 0 auto;
  padding: 26px 18px 26px;
  min-height: calc(100vh - 60px);
}

.page-bg {
  position: absolute;
  inset: 0;
  z-index: -5;
  background:
    radial-gradient(circle at 50% 0%, rgba(212, 188, 153, 0.18), transparent 26%),
    radial-gradient(circle at 50% 42%, rgba(255, 255, 255, 0.9), transparent 32%),
    linear-gradient(180deg, rgba(251, 248, 242, 0.98), rgba(244, 238, 227, 0.96));
}

.bg-mountain,
.bg-bamboo,
.bg-pavilion,
.bg-cloud,
.bg-bird {
  position: absolute;
  pointer-events: none;
  z-index: -4;
}

.bg-mountain.left {
  left: -30px;
  top: 48px;
  width: 360px;
  height: 330px;
  opacity: 0.18;
  background:
    radial-gradient(ellipse at 18% 25%, rgba(166, 171, 164, 0.45) 0 18%, transparent 19%),
    radial-gradient(ellipse at 36% 22%, rgba(180, 184, 176, 0.42) 0 20%, transparent 21%),
    radial-gradient(ellipse at 14% 64%, rgba(134, 145, 127, 0.36) 0 12%, transparent 13%),
    radial-gradient(ellipse at 38% 72%, rgba(160, 166, 156, 0.3) 0 18%, transparent 19%);
}

.bg-mountain.right {
  right: -12px;
  top: 170px;
  width: 340px;
  height: 440px;
  opacity: 0.16;
  background:
    radial-gradient(ellipse at 68% 28%, rgba(191, 191, 180, 0.45) 0 18%, transparent 19%),
    radial-gradient(ellipse at 80% 46%, rgba(164, 170, 160, 0.34) 0 15%, transparent 16%),
    radial-gradient(ellipse at 44% 84%, rgba(144, 152, 136, 0.32) 0 22%, transparent 23%);
}

.bg-bamboo {
  opacity: 0.26;
}

.bg-bamboo::before,
.bg-bamboo::after {
  content: '';
  position: absolute;
  background: rgba(126, 145, 120, 0.72);
  border-radius: 999px;
}

.bg-bamboo.right-top {
  right: -2px;
  top: -2px;
  width: 230px;
  height: 180px;
}

.bg-bamboo.right-top::before {
  width: 2px;
  height: 138px;
  right: 88px;
  top: 0;
  transform: rotate(14deg);
}

.bg-bamboo.right-top::after {
  width: 94px;
  height: 18px;
  right: 12px;
  top: 22px;
  transform: rotate(20deg);
  box-shadow:
    -24px 26px 0 rgba(126, 145, 120, 0.5),
    -34px 58px 0 rgba(126, 145, 120, 0.42);
}

.bg-bamboo.right-mid {
  right: 4px;
  top: 388px;
  width: 168px;
  height: 216px;
}

.bg-bamboo.right-mid::before {
  width: 2px;
  height: 130px;
  right: 52px;
  top: 10px;
  transform: rotate(18deg);
}

.bg-bamboo.right-mid::after {
  width: 78px;
  height: 16px;
  right: 0;
  top: 58px;
  transform: rotate(-28deg);
  box-shadow:
    -18px 36px 0 rgba(126, 145, 120, 0.48),
    -28px 76px 0 rgba(126, 145, 120, 0.4);
}

.bg-pavilion.left-bottom {
  left: -2px;
  bottom: 0;
  width: 370px;
  height: 280px;
  opacity: 0.17;
  background:
    radial-gradient(ellipse at 18% 66%, rgba(145, 150, 140, 0.34) 0 24%, transparent 25%),
    radial-gradient(ellipse at 62% 86%, rgba(167, 171, 163, 0.24) 0 22%, transparent 23%),
    radial-gradient(ellipse at 14% 84%, rgba(124, 136, 118, 0.3) 0 10%, transparent 11%);
}

.bg-cloud {
  width: 120px;
  height: 48px;
  opacity: 0.52;
  background:
    radial-gradient(circle at 22% 50%, rgba(226, 196, 146, 0.9) 0 10%, transparent 11%),
    radial-gradient(circle at 36% 38%, rgba(226, 196, 146, 0.7) 0 14%, transparent 15%),
    radial-gradient(circle at 52% 48%, rgba(226, 196, 146, 0.78) 0 12%, transparent 13%),
    linear-gradient(180deg, transparent 44%, rgba(226, 196, 146, 0.72) 45%, rgba(226, 196, 146, 0.72) 48%, transparent 49%);
  filter: blur(0.2px);
}

.cloud-left {
  left: 344px;
  top: 130px;
}

.cloud-right {
  right: 248px;
  top: 122px;
}

.bg-bird {
  left: 200px;
  top: 92px;
  width: 150px;
  height: 90px;
  opacity: 0.24;
}

.bg-bird::before,
.bg-bird::after {
  content: '';
  position: absolute;
  border-top: 2px solid rgba(148, 137, 108, 0.55);
  border-radius: 50%;
}

.bg-bird::before {
  width: 58px;
  height: 24px;
  left: 18px;
  top: 18px;
  transform: rotate(18deg);
}

.bg-bird::after {
  width: 24px;
  height: 10px;
  left: 0;
  top: 42px;
}

.hero {
  text-align: center;
  padding-top: 34px;
}

.hero-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.hero h1 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 58px;
  letter-spacing: 4px;
  color: #24594c;
  text-shadow: 0 4px 16px rgba(36, 89, 76, 0.08);
}

.hero p {
  margin: 14px 0 0;
  font-size: 16px;
  color: #737167;
}

.line {
  width: 72px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(199, 164, 111, 0.9), transparent);
}

.curl {
  color: #ccaa74;
  font-size: 24px;
  line-height: 1;
}

.search-section {
  display: flex;
  justify-content: center;
  margin-top: 42px;
}

.search-card,
.guide-card,
.result-card,
.category-card {
  background: rgba(255, 252, 247, 0.9);
  border: 1px solid rgba(223, 212, 196, 0.88);
  box-shadow:
    0 14px 34px rgba(162, 139, 104, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.76);
}

.search-card {
  width: min(1010px, 100%);
  border-radius: 14px;
  padding: 22px 24px 20px;
}

.search-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 110px;
  gap: 18px;
  align-items: center;
}

.search-input-wrap {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #1f5a4a;
  font-size: 24px;
}

.search-input {
  width: 100%;
  height: 44px;
  border: none;
  background: transparent;
  padding: 0 8px 0 44px;
  color: #686257;
  font-size: 15px;
}

.search-input:focus {
  outline: none;
}

.search-btn {
  height: 44px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(180deg, #6c977f, #5b856f);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.search-btn:disabled {
  opacity: 0.56;
  cursor: not-allowed;
}

.hot-row {
  margin-top: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hot-label,
.hot-item {
  font-size: 13px;
  color: #736b60;
}

.hot-item {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0 12px 0 0;
}

.browse-section {
  margin-top: 28px;
}

.section-chip-row,
.section-title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.section-chip-row {
  margin-top: 6px;
}

.section-chip {
  height: 34px;
  padding: 0 18px;
  border-radius: 6px;
  border: 1px solid rgba(202, 180, 144, 0.45);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(250, 247, 241, 0.82);
  color: #5f6b59;
  font-size: 15px;
}

.section-chip-line,
.title-line {
  width: 86px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(208, 174, 120, 0.8), transparent);
}

.section-chip-mark,
.title-mark {
  color: #caa26c;
  font-size: 14px;
}

.section-title-row {
  margin-top: 22px;
}

.section-title-row h2 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 44px;
  letter-spacing: 3px;
  color: #24594c;
}

.category-grid {
  margin: 28px auto 0;
  width: min(1086px, 100%);
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.category-card {
  border-radius: 12px;
  min-height: 180px;
  padding: 22px 18px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
}

.category-icon {
  color: #101010;
  font-size: 54px;
  line-height: 1;
}

.category-card strong {
  margin-top: 16px;
  font-family: var(--font-serif);
  font-size: 20px;
  color: #24594c;
}

.category-count {
  margin-top: 8px;
  font-size: 15px;
  color: #666255;
}

.category-card em {
  margin-top: auto;
  font-style: normal;
  font-size: 12px;
  line-height: 1.8;
  color: #867e72;
}

.guide-card {
  width: min(1086px, 100%);
  margin: 20px auto 0;
  border-radius: 14px;
  padding: 18px 24px 24px;
}

.guide-card h3 {
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-serif);
  font-size: 24px;
  color: #24594c;
}

.guide-card h3 i {
  color: #d6a446;
}

.guide-grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.guide-item {
  padding: 10px 16px 4px;
  text-align: center;
}

.guide-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 44px;
  color: #101010;
}

.guide-item strong {
  display: block;
  margin-top: 10px;
  font-family: var(--font-serif);
  font-size: 18px;
  color: #24594c;
}

.guide-item em {
  display: block;
  margin-top: 8px;
  font-style: normal;
  font-size: 13px;
  color: #807a6f;
}

.result-section {
  width: min(1086px, 100%);
  margin: 28px auto 0;
}

.result-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-btn,
.back-btn {
  height: 34px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px solid rgba(208, 194, 174, 0.9);
  background: rgba(250, 247, 241, 0.88);
  color: #665f54;
  cursor: pointer;
}

.filter-btn.active {
  background: #24594c;
  border-color: #24594c;
  color: #fff;
}

.result-list {
  display: grid;
  gap: 14px;
}

.result-card {
  border-radius: 14px;
  padding: 18px 20px;
}

.result-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.result-tag {
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid;
  display: inline-flex;
  align-items: center;
  font-size: 12px;
}

.result-head h3 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 22px;
  color: #24594c;
}

.result-body {
  margin: 0;
  color: #6a6358;
  line-height: 1.9;
}

.result-foot {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.result-source {
  color: #7d766a;
  font-size: 13px;
}

.result-score {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6a6358;
  font-size: 13px;
}

.score-bar {
  width: 148px;
  height: 8px;
  border-radius: 999px;
  background: rgba(224, 216, 205, 0.9);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: inherit;
}

@media (max-width: 1180px) {
  .category-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .guide-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .kb-page {
    padding: 20px 12px 24px;
  }

  .hero h1 {
    font-size: 40px;
  }

  .hero p {
    font-size: 14px;
  }

  .line,
  .section-chip-line,
  .title-line {
    width: 36px;
  }

  .search-card {
    padding: 16px 14px;
  }

  .search-row {
    grid-template-columns: 1fr;
  }

  .category-grid,
  .guide-grid {
    grid-template-columns: 1fr;
  }

  .section-title-row h2 {
    font-size: 30px;
  }

  .result-toolbar,
  .result-foot {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
