<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">九种体质测评</h1>
      <p class="page-desc">依据《中医体质分类与判定》国家标准</p>
    </div>

    <!-- 测评流程 -->
    <div class="quiz-container">
      <!-- 未开始 -->
      <div v-if="phase === 'intro'" class="quiz-intro">
        <div class="intro-visual">
          <div class="constitution-display">
            <div class="display-emoji">☯</div>
            <div class="display-label">九种体质</div>
          </div>
        </div>
        <div class="intro-info card">
          <h2>体质测评</h2>
          <p>依据《中医体质分类与判定》国家标准</p>

          <div class="mode-card quick-mode" @click="startQuiz('quick')">
            <div class="mode-header">
              <div class="mode-title">⚡ 快速测评</div>
              <div class="mode-badge">推荐</div>
            </div>
            <div class="mode-desc">10道题，约30秒</div>
            <div class="mode-cta">开始测评 →</div>
          </div>

          <div class="mode-card" @click="startQuiz('full')">
            <div class="mode-header">
              <div class="mode-title">📋 完整测评</div>
              <div class="mode-badge secondary">深度</div>
            </div>
            <div class="mode-desc">45道题，约5分钟</div>
            <div class="mode-note">含雷达图、养生方案、食疗建议</div>
          </div>

          <ul class="intro-list">
            <li>根据近一年身体状况作答</li>
            <li>选择最符合您的选项</li>
            <li>结果仅供学习参考</li>
          </ul>
        </div>
      </div>

      <!-- 答题中 -->
      <div v-else-if="phase === 'quiz'" class="quiz-active">
        <div class="quiz-progress">
          <div class="progress-info">
            <span>第 {{ currentQuestion + 1 }} / {{ activeQuestions.length }} 题</span>
            <span class="progress-constitution">{{ currentConstitution }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar-fill" :style="{ width: `${((currentQuestion + 1) / activeQuestions.length) * 100}%` }"></div>
          </div>
        </div>

        <div class="question-card card">
          <div class="question-num">{{ String(currentQuestion + 1).padStart(2, '0') }}</div>
          <div class="question-text">{{ activeQuestions[currentQuestion].text }}</div>
          <div class="question-options">
            <div class="option" v-for="(opt, i) in activeQuestions[currentQuestion].options" :key="i"
                 :class="{ selected: answers[currentQuestion] === i }"
                 @click="selectAnswer(i)">
              <div class="option-letter">{{ String.fromCharCode(65 + i) }}</div>
              <div class="option-text">{{ opt }}</div>
            </div>
          </div>
        </div>

        <div class="quiz-nav">
          <button class="btn btn-outline" v-if="currentQuestion > 0" @click="prevQuestion">← 上一题</button>
          <button class="btn btn-primary" v-if="currentQuestion < activeQuestions.length - 1" @click="nextQuestion"
                  :disabled="answers[currentQuestion] === null">下一题 →</button>
          <button class="btn btn-primary" v-else @click="submitQuiz"
                  :disabled="answers.slice(0, activeQuestions.length).includes(null)">完成测评 →</button>
        </div>
      </div>

      <!-- 结果 -->
      <div v-else-if="phase === 'result'" class="quiz-result">
        <div v-if="quizMode === 'quick'" class="quick-result-banner card">
          <span class="banner-icon">{{ primaryResult.emoji }}</span>
          <div class="banner-info">
            <div class="banner-title">体质倾向：<strong :style="{ color: primaryResult.color }">{{ primaryResult.name }}</strong></div>
            <div class="banner-desc">{{ primaryResult.description }}</div>
          </div>
        </div>

        <div v-if="quizMode === 'full'" class="result-chart card">
          <h3 class="result-section-title">体质雷达图</h3>
          <div ref="radarChart" class="radar-chart"></div>
        </div>

        <div class="result-primary card">
          <div class="primary-badge" :style="{ borderColor: primaryResult.color }">
            <span class="primary-emoji">{{ primaryResult.emoji }}</span>
            <div class="primary-info">
              <div class="primary-label">您的体质类型</div>
              <div class="primary-name" :style="{ color: primaryResult.color }">{{ primaryResult.name }}</div>
              <div class="primary-percent">{{ primaryResult.percent }}分</div>
            </div>
          </div>
          <p class="primary-desc">{{ primaryResult.description }}</p>
        </div>

        <div class="result-detail card">
          <h3 class="result-section-title">体质详细得分</h3>
          <div class="detail-grid">
            <div class="detail-item" v-for="r in allResults" :key="r.name"
                 :class="{ highlight: r.isPrimary }">
              <div class="detail-name" :style="r.isPrimary ? { color: r.color } : {}">
                {{ r.emoji }} {{ r.name }}
              </div>
              <div class="detail-bar">
                <div class="detail-bar-fill" :style="{ width: r.percent + '%', background: r.color }"></div>
              </div>
              <div class="detail-score">{{ r.percent }}分</div>
            </div>
          </div>
        </div>

        <div class="result-advice">
          <div class="advice-card card" v-for="advice in primaryResult.advice" :key="advice.type">
            <span class="advice-icon">{{ advice.icon }}</span>
            <div class="advice-content">
              <div class="advice-type">{{ advice.type }}</div>
              <div class="advice-text">{{ advice.text }}</div>
            </div>
          </div>
        </div>

        <div class="result-actions">
          <button v-if="quizMode === 'quick'" class="btn btn-primary" @click="$router.push('/chat')">
            带着体质结果去学习 →
          </button>
          <template v-else>
            <button class="btn btn-outline" @click="resetQuiz">重新测评</button>
            <button class="btn btn-primary" @click="$router.push('/chat')">开始辨证学习 →</button>
          </template>
        </div>
        <div v-if="quizMode === 'quick'" class="full-mode-link">
          <span>想获得更精准的分析？</span>
          <button class="link-btn" @click="startQuiz('full')">做完整45题测评 →</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const constitutions = [
  { name: '平和质', emoji: '☯', color: '#6B8E23', desc: '阴阳气血调和，体态适中，面色润泽' },
  { name: '气虚质', emoji: '🫁', color: '#60a5fa', desc: '元气不足，容易疲乏，气短懒言' },
  { name: '阳虚质', emoji: '❄', color: '#a78bfa', desc: '阳气不足，畏寒怕冷，手足不温' },
  { name: '阴虚质', emoji: '♨', color: '#ff6b6b', desc: '阴液亏少，口燥咽干，手足心热' },
  { name: '痰湿质', emoji: '💧', color: '#34d399', desc: '痰湿凝聚，体形肥胖，腹部肥满' },
  { name: '湿热质', emoji: '🔥', color: '#f59e0b', desc: '湿热内蕴，面垢油光，口苦苔黄' },
  { name: '血瘀质', emoji: '🩸', color: '#ef4444', desc: '血行不畅，肤色晦黯，舌质紫黯' },
  { name: '气郁质', emoji: '🌙', color: '#8b5cf6', desc: '气机郁滞，神情抑郁，忧虑脆弱' },
  { name: '特禀质', emoji: '✿', color: '#ec4899', desc: '先天失常，以过敏反应为主' },
]

const quickQuestions = [
  { text: '您容易疲乏、气短、乏力吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气虚质' },
  { text: '您手脚发凉、畏寒怕冷吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阳虚质' },
  { text: '您口燥咽干、手足心热吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阴虚质' },
  { text: '您感到胸闷、腹部胀满、身体沉重吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '痰湿质' },
  { text: '您面部或鼻部油腻、易生痤疮吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '湿热质' },
  { text: '您肤色晦黯、容易出现瘀斑吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '血瘀质' },
  { text: '您感到闷闷不乐、情绪低沉吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气郁质' },
  { text: '您精力充沛、睡眠质量好吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
  { text: '您容易过敏吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '特禀质' },
  { text: '您大便规律正常吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
]

const questions = [
  { text: '您容易疲乏吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气虚质' },
  { text: '您容易气短吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气虚质' },
  { text: '您容易心慌吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气虚质' },
  { text: '您容易头晕吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气虚质' },
  { text: '您比别人容易感冒吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气虚质' },
  { text: '您手脚发凉吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阳虚质' },
  { text: '您胃脘部怕冷吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阳虚质' },
  { text: '您感到怕冷吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阳虚质' },
  { text: '您比别人受不了寒凉吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阳虚质' },
  { text: '您吃凉东西会不舒服吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阳虚质' },
  { text: '您感到手脚心发热吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阴虚质' },
  { text: '您感觉身体发热吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阴虚质' },
  { text: '您皮肤或口唇干吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阴虚质' },
  { text: '您口唇的颜色比一般人红吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阴虚质' },
  { text: '您容易便秘或大便干燥吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '阴虚质' },
  { text: '您感到胸闷、腹部胀满吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '痰湿质' },
  { text: '您的身体沉重不轻松吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '痰湿质' },
  { text: '您的腹部肥满松软吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '痰湿质' },
  { text: '您额头油脂分泌过多吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '痰湿质' },
  { text: '您上眼睑比一般人肿吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '痰湿质' },
  { text: '您面部或鼻部油腻吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '湿热质' },
  { text: '您易生痤疮吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '湿热质' },
  { text: '您感到口苦吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '湿热质' },
  { text: '您大便粘滞吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '湿热质' },
  { text: '您小便时尿道有发热感吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '湿热质' },
  { text: '您的皮肤出现青紫瘀斑吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '血瘀质' },
  { text: '您两颧部有细微红丝吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '血瘀质' },
  { text: '您身体上有哪里疼痛吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '血瘀质' },
  { text: '您面色晦黯吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '血瘀质' },
  { text: '您容易有黑眼圈吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '血瘀质' },
  { text: '您感到闷闷不乐、情绪低沉吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气郁质' },
  { text: '您容易精神紧张吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气郁质' },
  { text: '您多愁善感吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气郁质' },
  { text: '您容易感到害怕吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气郁质' },
  { text: '您胁肋部胀痛吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '气郁质' },
  { text: '您没有感冒也会打喷嚏吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '特禀质' },
  { text: '您没有感冒也会鼻塞吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '特禀质' },
  { text: '您有因季节变化咳喘吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '特禀质' },
  { text: '您容易过敏吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '特禀质' },
  { text: '您的皮肤容易起荨麻疹吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '特禀质' },
  { text: '您精力充沛吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
  { text: '您声音洪亮吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
  { text: '您入睡快、睡眠质量高吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
  { text: '您平时说话声音洪亮吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
  { text: '您大小便规律正常吗？', options: ['从不', '很少', '有时', '经常', '总是'], type: '平和质' },
]

const phase = ref('intro')
const currentQuestion = ref(0)
const quizMode = ref('full')
const savedQuizMode = ref('full')

const activeQuestions = computed(() => quizMode.value === 'quick' ? quickQuestions : questions)
const answers = ref(Array(quickQuestions.length).fill(null))

const currentConstitution = computed(() => activeQuestions.value[currentQuestion.value]?.type || '')

function startQuiz(mode) {
  savedQuizMode.value = mode
  quizMode.value = mode
  phase.value = 'quiz'
  currentQuestion.value = 0
  const len = mode === 'quick' ? quickQuestions.length : questions.length
  answers.value = Array(len).fill(null)
}

function selectAnswer(i) {
  answers.value[currentQuestion.value] = i
}

function nextQuestion() {
  if (currentQuestion.value < activeQuestions.value.length - 1) currentQuestion.value++
}

function prevQuestion() {
  if (currentQuestion.value > 0) currentQuestion.value--
}

function submitQuiz() {
  phase.value = 'result'
  if (quizMode.value === 'full') {
    setTimeout(initRadar, 300)
  }
}

function resetQuiz() {
  phase.value = 'intro'
  quizMode.value = savedQuizMode.value
  const len = savedQuizMode.value === 'quick' ? quickQuestions.length : questions.length
  answers.value = Array(len).fill(null)
  currentQuestion.value = 0
}

const allResults = computed(() => {
  const types = [...new Set(activeQuestions.value.map(q => q.type))]
  const qlen = quizMode.value === 'quick' ? quickQuestions.length : questions.length
  return types.map(type => {
    const indices = activeQuestions.value.map((q, i) => q.type === type ? i : -1).filter(i => i >= 0)
    const score = indices.reduce((sum, i) => {
      if (i < qlen && answers.value[i] !== null) return sum + answers.value[i] + 1
      return sum
    }, 0)
    const maxScore = indices.length * 5
    const percent = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0
    const c = constitutions.find(c => c.name === type) || constitutions[0]
    return { name: type, percent, color: c.color, emoji: c.emoji }
  }).sort((a, b) => b.percent - a.percent)
})

const primaryResult = computed(() => {
  const r = allResults.value[0]
  const c = constitutions.find(c => c.name === r.name) || constitutions[0]
  const adviceMap = {
    '平和质': [
      { icon: '🍃', type: '饮食调养', text: '饮食均衡，多吃五谷杂粮、蔬菜水果。' },
      { icon: '🏃', type: '运动养生', text: '适度运动，保持规律作息。' },
      { icon: '🌙', type: '情志调摄', text: '保持心情愉悦，乐观开朗。' },
    ],
    '气虚质': [
      { icon: '🍲', type: '饮食调养', text: '多吃山药、黄芪、党参等补气食物。' },
      { icon: '🧘', type: '运动养生', text: '宜做柔缓运动，如散步、太极拳。' },
      { icon: '😴', type: '作息建议', text: '注意休息，避免劳累过度。' },
    ],
    '阳虚质': [
      { icon: '🌞', type: '饮食调养', text: '多吃羊肉、桂圆、生姜等温阳食物。' },
      { icon: '☀️', type: '运动养生', text: '多做户外运动，晒太阳为宜。' },
      { icon: '🛌', type: '作息建议', text: '注意保暖，热水泡脚有益。' },
    ],
    '阴虚质': [
      { icon: '🥤', type: '饮食调养', text: '多吃银耳、百合、麦冬等滋阴食物。' },
      { icon: '🌙', type: '作息建议', text: '保证睡眠，避免熬夜。' },
      { icon: '🧘', type: '情志调摄', text: '宁心静神，避免急躁。' },
    ],
  }
  return {
    ...r,
    color: c.color,
    emoji: c.emoji,
    description: c.desc,
    advice: adviceMap[r.name] || adviceMap['平和质'],
  }
})

const radarChart = ref(null)
let radarInstance = null

function initRadar() {
  if (!radarChart.value) return
  radarInstance = echarts.init(radarChart.value)

  const option = {
    backgroundColor: 'transparent',
    radar: {
      indicator: allResults.value.map(r => ({ name: r.name, max: 100 })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#2B2B2B',
        fontSize: 12,
        fontFamily: 'Noto Serif SC',
      },
      splitLine: { lineStyle: { color: 'rgba(107, 142, 35, 0.15)' } },
      splitArea: { areaStyle: { color: ['rgba(107, 142, 35, 0.02)', 'rgba(107, 142, 35, 0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(107, 142, 35, 0.2)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: allResults.value.map(r => r.percent),
        name: '体质得分',
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { offset: 0, color: 'rgba(107, 142, 35, 0.6)' },
            { offset: 1, color: 'rgba(107, 142, 35, 0.1)' },
          ])
        },
        lineStyle: { color: '#6B8E23', width: 2 },
        itemStyle: { color: '#6B8E23' },
        symbol: 'circle',
        symbolSize: 6,
      }],
    }],
  }

  radarInstance.setOption(option)
}

watch(phase, (val) => {
  if (val === 'result') {
    setTimeout(initRadar, 100)
  }
})

onMounted(() => {
  window.addEventListener('resize', () => radarInstance?.resize())
})
</script>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
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

/* Intro */
.quiz-intro {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}

.constitution-display {
  text-align: center;
  padding: 40px;
}

.display-emoji {
  font-size: 80px;
  margin-bottom: 16px;
}

.display-label {
  font-size: 18px;
  font-family: var(--font-serif);
  color: var(--primary-brown);
}

.intro-info h2 {
  font-size: 20px;
  color: var(--primary-brown);
  margin-bottom: 8px;
}

.intro-info > p {
  color: var(--text-secondary);
  margin-bottom: 20px;
  font-size: 13px;
}

.mode-card {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-card:hover {
  background: var(--bg-soft);
  border-color: var(--primary-brown);
}

.quick-mode {
  background: var(--bg-soft);
  border-color: var(--border-medium);
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.mode-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.mode-badge {
  font-size: 10px;
  padding: 2px 8px;
  background: var(--primary-red);
  color: #fff;
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
}

.mode-badge.secondary {
  background: var(--bg-soft);
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
}

.mode-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.mode-cta {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-red);
}

.mode-note {
  font-size: 11px;
  color: var(--text-muted);
}

.intro-list {
  list-style: none;
  padding: 16px;
  background: var(--bg-soft);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--primary-brown);
  margin-top: 20px;
}

.intro-list li {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 4px 0;
}

/* Quiz */
.quiz-progress {
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-constitution {
  color: var(--primary-brown);
  font-weight: 500;
}

.progress-bar {
  height: 4px;
  background: var(--bg-soft);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--primary-brown);
  transition: width 0.3s;
}

.question-card {
  max-width: 600px;
  margin: 0 auto 24px;
  padding: 28px;
}

.question-num {
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin-bottom: 16px;
}

.question-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 24px;
  line-height: 1.5;
}

.question-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover {
  background: var(--bg-soft);
  border-color: var(--border-medium);
}

.option.selected {
  background: var(--accent-light);
  border-color: var(--primary-red);
}

.option-letter {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bg-soft);
  color: var(--primary-brown);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.option.selected .option-letter {
  background: var(--primary-red);
  color: #fff;
}

.option-text {
  font-size: 14px;
  color: var(--text-secondary);
}

.option.selected .option-text {
  color: var(--primary-red);
}

.quiz-nav {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* Result */
.quiz-result {
  max-width: 700px;
  margin: 0 auto;
}

.quick-result-banner {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  margin-bottom: 20px;
}

.banner-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.banner-title {
  font-size: 15px;
  color: var(--text-main);
  margin-bottom: 4px;
}

.banner-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.result-chart {
  margin-bottom: 24px;
  padding: 20px;
}

.result-section-title {
  font-size: 15px;
  color: var(--primary-brown);
  margin-bottom: 16px;
  text-align: center;
}

.radar-chart {
  width: 100%;
  height: 350px;
}

.result-primary {
  margin-bottom: 24px;
  padding: 24px;
  text-align: center;
}

.primary-badge {
  display: inline-flex;
  align-items: center;
  gap: 20px;
  padding: 20px 32px;
  border: 2px solid;
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
}

.primary-emoji {
  font-size: 40px;
}

.primary-label {
  font-size: 11px;
  color: var(--text-muted);
}

.primary-name {
  font-size: 24px;
  font-weight: 700;
  margin: 4px 0;
}

.primary-percent {
  font-size: 18px;
  font-weight: 600;
}

.primary-desc {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.result-detail {
  margin-bottom: 24px;
  padding: 20px;
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: var(--bg-main);
  border-radius: var(--radius-md);
}

.detail-item.highlight {
  background: var(--bg-soft);
}

.detail-name {
  font-size: 13px;
  color: var(--text-secondary);
}

.detail-bar {
  height: 6px;
  background: var(--bg-soft);
  border-radius: 3px;
  overflow: hidden;
}

.detail-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.detail-score {
  font-size: 12px;
  color: var(--text-muted);
  text-align: right;
}

.result-advice {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.advice-card {
  display: flex;
  gap: 12px;
  padding: 16px;
}

.advice-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.advice-type {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 4px;
}

.advice-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.full-mode-link {
  text-align: center;
  margin-top: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.link-btn {
  background: none;
  border: none;
  color: var(--primary-red);
  cursor: pointer;
  font-size: 12px;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .quiz-intro {
    grid-template-columns: 1fr;
  }

  .constitution-display {
    padding: 20px;
  }

  .question-options {
    grid-template-columns: 1fr;
  }

  .result-advice {
    grid-template-columns: 1fr;
  }
}
</style>
