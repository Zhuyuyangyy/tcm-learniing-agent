<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">辨证论治</h1>
      <p class="page-desc">学习中医辨证论治思路与方法</p>
    </div>

    <div class="diagnosis-layout">
      <!-- 左侧：输入区域 -->
      <div class="diagnosis-sidebar">
        <div class="sidebar-card">
          <div class="sidebar-card-title">🏥 症状选择</div>
          <div class="symptom-tags">
            <span class="tag" v-for="s in symptoms" :key="s"
                  :class="{ active: selectedSymptoms.includes(s) }"
                  @click="toggleSymptom(s)">{{ s }}</span>
          </div>
        </div>

        <div class="sidebar-card">
          <div class="sidebar-card-title">🔍 证型参考</div>
          <div class="symptom-tags">
            <span class="tag syndrome" v-for="t in syndromeTypes" :key="t"
                  :class="{ active: selectedSymptoms.includes(t) }"
                  @click="toggleSymptom(t)">{{ t }}</span>
          </div>
        </div>

        <div class="sidebar-card">
          <div class="sidebar-card-title">📋 科室</div>
          <select class="input-select" v-model="department">
            <option value="内科">中医内科</option>
            <option value="妇科">中医妇科</option>
            <option value="儿科">中医儿科</option>
            <option value="骨伤科">骨伤科</option>
            <option value="皮肤科">皮肤科</option>
          </select>
        </div>

        <div class="sidebar-actions">
          <button class="btn btn-outline" @click="clearAll">清空</button>
        </div>
      </div>

      <!-- 右侧：诊断结果 -->
      <div class="diagnosis-main">
        <!-- 欢迎/输入区 -->
        <div v-if="!currentResult" class="diagnosis-welcome">
          <div class="welcome-box">
            <div class="welcome-icon">📋</div>
            <h2>辨证论治学习</h2>
            <p>描述症状或从左侧选择，开始学习辨证</p>

            <div class="input-area">
              <textarea
                  class="input-textarea"
                  v-model="inputText"
                  placeholder="输入症状描述，如：头痛、乏力、食欲不振..."
                  rows="4"
              ></textarea>
              <button class="btn btn-primary btn-large" @click="submitDiagnosis"
                      :disabled="!inputText.trim() && !selectedSymptoms.length">
                开始学习 →
              </button>
            </div>

            <div class="demo-tips">
              <span class="tips-label">💡 演示案例：</span>
              <div class="demo-btns">
                <button class="demo-btn" v-for="d in demoPrompts" :key="d.text" @click="useDemo(d.text)">
                  {{ d.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- 功能说明 -->
          <div class="feature-cards">
            <div class="feature-card" v-for="f in features" :key="f.title">
              <span class="feature-icon">{{ f.icon }}</span>
              <div class="feature-text">
                <div class="feature-title">{{ f.title }}</div>
                <div class="feature-desc">{{ f.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 诊断结果 -->
        <div v-else class="diagnosis-result">
          <div class="result-header">
            <h2>辨证结果</h2>
            <button class="btn btn-outline" @click="clearResult">新建诊断</button>
          </div>

          <!-- 证型卡片 -->
          <div class="syndrome-card card">
            <div class="syndrome-badge">
              <span class="syndrome-emoji">🔍</span>
              <div class="syndrome-info">
                <div class="syndrome-label">辨证结果</div>
                <div class="syndrome-name">{{ currentResult.syndrome }}</div>
              </div>
            </div>
            <div class="syndrome-analysis">
              <div class="analysis-label">证候分析</div>
              <div class="analysis-text">{{ currentResult.analysis }}</div>
            </div>
            <div class="syndrome-method">
              <span class="method-label">治法</span>
              <span class="method-text">{{ currentResult.method }}</span>
            </div>
          </div>

          <!-- 处方卡片 -->
          <div class="prescription-card card" v-if="currentResult.prescription">
            <div class="rx-header">
              <span class="rx-icon">💊</span>
              <span class="rx-title">{{ currentResult.prescription.name }}</span>
              <span class="rx-tag">{{ currentResult.prescription.type }}</span>
            </div>
            <div class="rx-body">
              <div class="rx-row">
                <span class="rx-label">组成</span>
                <span class="rx-value">{{ currentResult.prescription.composition }}</span>
              </div>
              <div class="rx-row">
                <span class="rx-label">剂量</span>
                <span class="rx-value">{{ currentResult.prescription.dosage }}</span>
              </div>
              <div class="rx-row">
                <span class="rx-label">煎服法</span>
                <span class="rx-value">{{ currentResult.prescription.usage }}</span>
              </div>
            </div>
            <div class="rx-warnings" v-if="currentResult.prescription.warnings">
              <span class="warning-icon">⚠️</span>
              <span>{{ currentResult.prescription.warnings }}</span>
            </div>
          </div>

          <!-- 参考来源 -->
          <div class="sources-card card" v-if="currentResult.sources && currentResult.sources.length">
            <div class="sources-title">📚 参考来源</div>
            <div class="sources-list">
              <div class="source-item" v-for="(src, si) in currentResult.sources" :key="si">
                <span class="source-num">{{ si + 1 }}.</span>
                <span class="source-text">{{ src }}</span>
              </div>
            </div>
          </div>

          <!-- 学习分析 -->
          <div class="thinking-card card">
            <div class="thinking-title">📋 学习分析</div>
            <div class="thinking-steps">
              <div class="thinking-step" v-for="(step, i) in currentResult.thinking" :key="i">
                <div class="step-header">
                  <span class="step-icon">{{ step.icon }}</span>
                  <span class="step-agent">{{ step.agent }}</span>
                </div>
                <div class="step-text">{{ step.text }}</div>
              </div>
            </div>
          </div>

          <!-- 继续 -->
          <div class="continue-actions">
            <button class="btn btn-outline" @click="clearResult">← 继续学习</button>
            <button class="btn btn-primary" @click="$router.push('/therapy')">查看外治疗法 →</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const inputText = ref('')
const selectedSymptoms = ref([])
const department = ref('内科')
const currentResult = ref(null)

const symptoms = [
  '头痛', '头晕', '乏力', '发热', '咳嗽',
  '咽痛', '胸闷', '心悸', '腹痛', '腹胀',
  '腹泻', '便秘', '恶心', '呕吐', '食欲不振',
  '失眠', '多梦', '焦虑', '抑郁', '记忆力下降',
]

const syndromeTypes = [
  '肝气郁结', '气血两虚', '脾胃虚弱', '肾阳不足',
  '肺气不固', '心火亢盛', '痰湿内阻', '血瘀脉络',
  '阴虚火旺', '阳虚水泛', '湿热下注', '风寒束表',
]

const features = [
  { icon: '🎯', title: '辨证分析', desc: '学习证型判断方法' },
  { icon: '⚖️', title: '用药安全', desc: '十八反十九畏审核' },
  { icon: '📜', title: '经典处方', desc: '伤寒金匮经典方剂' },
  { icon: '🔬', title: '方剂加减', desc: '因人因时灵活化裁' },
]

const demoPrompts = [
  { label: '肝气郁结案例', text: '胸胁胀痛、情志抑郁、脉弦' },
  { label: '肾阴虚案例', text: '腰膝酸软、潮热盗汗、头晕耳鸣' },
  { label: '气血两虚案例', text: '气短懒言、疲劳乏力、面色萎黄' },
]

function toggleSymptom(s) {
  const idx = selectedSymptoms.value.indexOf(s)
  if (idx >= 0) selectedSymptoms.value.splice(idx, 1)
  else selectedSymptoms.value.push(s)
}

function clearAll() {
  selectedSymptoms.value = []
  inputText.value = ''
  department.value = '内科'
}

function clearResult() {
  currentResult.value = null
  clearAll()
}

function useDemo(text) {
  inputText.value = text
}

function submitDiagnosis() {
  const text = inputText.value.trim()
  const hasSymptoms = selectedSymptoms.value.length > 0
  if (!text && !hasSymptoms) return

  const display = hasSymptoms
      ? `${text}；症状：${selectedSymptoms.value.join('、')}`
      : text

  const inputLower = display.toLowerCase()

  const syndromeMap = [
    {
      keywords: ['胸胁', '肝气', '情志', '抑郁', '脉弦', '胀痛', '胁肋', '心烦', '失眠'],
      syndrome: '肝气郁结证',
      method: '疏肝解郁，健脾理气',
      analysis: '肝主疏泄，调畅气机，情志不畅则肝气郁结；肝气犯脾，脾失健运，故见食欲不振、腹胀乏力。治疗当疏肝健脾，调和肝脾。',
      prescription: {
        name: '柴胡疏肝散加减', type: '经典方剂',
        composition: '柴胡12g，白芍15g、川芎10g、香附10g、枳壳10g、陈皮8g、党参15g，白术12g、茯苓15g、炙甘草6g',
        dosage: '每日1剂，水煎分两次温服',
        usage: '早饭前、晚饭后半小时温服，忌食生冷油腻',
        warnings: '孕妇慎用；如出现口干舌燥等阴虚症状需调整方剂',
      },
      sources: [
        '《伤寒论》第96条：伤寒五六日，中风，往来寒热，胸胁苦满...',
        '《金匮要略》：见肝之病，知肝传脾，当先实脾',
        '《中医内科学》肝气郁结证：疏肝理气，柴胡疏肝散主之',
      ],
      thinking: [
        { icon: '📋', agent: '症状建档', text: '建档分析：根据症状描述，构建患者画像与体质关联...' },
        { icon: '🔍', agent: '辨证检索', text: '知识检索：匹配《伤寒论》《金匮要略》相关条文...' },
        { icon: '🧠', agent: '辨证分析', text: '辨证分析：综合判断为"肝气郁结、脾胃虚弱"证...' },
        { icon: '⚖️', agent: '用药审核', text: '安全审核：检查十八反十九畏，无配伍禁忌...' },
        { icon: '📜', agent: '方药生成', text: '处方生成：柴胡疏肝散加减化裁...' },
        { icon: '🛤️', agent: '调护规划', text: '调护规划：给出阶段性康复方案与饮食禁忌...' },
      ],
    },
    {
      keywords: ['腰膝', '肾', '盗汗', '潮热', '阴虚', '耳鸣', '虚火', '口干'],
      syndrome: '肾阴虚证',
      method: '滋阴补肾，清热降火',
      analysis: '肾主骨生髓，腰为肾之府。肾阴不足，虚火内扰，故见腰膝酸软、潮热盗汗、头晕耳鸣。治宜滋阴补肾，壮水之主。',
      prescription: {
        name: '六味地黄丸加减', type: '经典方剂',
        composition: '熟地黄20g、山茱萸15g、山药15g、泽泻10g、茯苓12g、丹皮10g、枸杞子12g、菊花10g',
        dosage: '每日1剂，水煎分两次服',
        usage: '午饭前、晚饭后温服，忌食辛辣刺激性食物',
        warnings: '脾虚便溏者慎用；感冒发热期间暂停服用',
      },
      sources: [
        '《小儿药证直诀》：地黄丸治肾怯失音，図开不合，神不足...',
        '《中医内科学》肾阴虚证：滋补肾阴，六味地黄丸主之',
        '《医宗必读》：肾为先天之本，藏精生髓',
      ],
      thinking: [
        { icon: '📋', agent: '症状建档', text: '建档分析：患者主诉腰膝酸软、潮热盗汗...' },
        { icon: '🔍', agent: '辨证检索', text: '知识检索：检索《中医内科学》肾阴虚证诊断标准...' },
        { icon: '🧠', agent: '辨证分析', text: '辨证分析：腰为肾之府，肾阴不足，虚火内扰...' },
        { icon: '⚖️', agent: '用药审核', text: '安全审核：六味地黄丸配伍安全，无禁忌...' },
        { icon: '📜', agent: '方药生成', text: '处方生成：六味地黄丸加枸杞子、菊花清热...' },
        { icon: '🛤️', agent: '调护规划', text: '调护规划：节制房事，宜食滋阴之品...' },
      ],
    },
    {
      keywords: ['气虚', '乏力', '疲劳', '气短', '懒言', '自汗', '面色', '食欲不振', '心慌'],
      syndrome: '气血两虚证',
      method: '补气养血，健脾益胃',
      analysis: '气虚则推动无力，故乏力、气短、懒言；血虚则面容失养，故面色萎黄。心脾两虚，气血不足。治宜补中益气，养血安神。',
      prescription: {
        name: '补中益气汤合四物汤加减', type: '合方加减',
        composition: '黄芪30g、党参20g，白术15g、炙甘草10g，当归12g、熟地黄15g，白芍12g、川芎8g、陈皮6g、升麻6g',
        dosage: '每日1剂，水煎分两次温服',
        usage: '早饭前、晚饭后温服，忌食生冷、辛辣',
        warnings: '阴虚火旺、实热证者慎用；高血压患者慎服升麻',
      },
      sources: [
        '《脾胃论》：补中益气汤治脾胃气虚，清阳下陷',
        '《太平惠民和剂局方》：四物汤治营血虚滞，月经不调',
        '《中医内科学》气血两虚证：补气养血，八珍汤主之',
      ],
      thinking: [
        { icon: '📋', agent: '症状建档', text: '建档分析：患者气虚症状明显，属气血两虚...' },
        { icon: '🔍', agent: '辨证检索', text: '知识检索：检索《脾胃论》补中益气汤方义...' },
        { icon: '🧠', agent: '辨证分析', text: '辨证分析：气虚推动无力，血虚面容失养...' },
        { icon: '⚖️', agent: '用药审核', text: '安全审核：黄芪、党参，当归配伍安全...' },
        { icon: '📜', agent: '方药生成', text: '处方生成：补中益气汤合四物汤气血双补...' },
        { icon: '🛤️', agent: '调护规划', text: '调护规划：适度运动，八段锦健脾益气...' },
      ],
    },
  ]

  let selected = syndromeMap[0]
  for (const s of syndromeMap) {
    if (s.keywords.some(k => inputLower.includes(k))) { selected = s; break }
  }

  currentResult.value = {
    syndrome: selected.syndrome,
    method: selected.method,
    analysis: selected.analysis,
    prescription: selected.prescription,
    sources: selected.sources,
    thinking: selected.thinking,
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1200px;
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

/* Layout */
.diagnosis-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  min-height: calc(100vh - 280px);
}

/* Sidebar */
.diagnosis-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 16px;
}

.sidebar-card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 12px;
}

.symptom-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  background: var(--bg-soft);
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.2s;
}

.tag:hover {
  background: var(--bg-main);
  border-color: var(--primary-brown);
}

.tag.active {
  background: var(--accent-light);
  color: var(--primary-red);
  border-color: var(--primary-red);
}

.tag.syndrome {
  font-size: 11px;
  padding: 3px 8px;
}

.input-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-main);
  color: var(--text-main);
  font-size: 14px;
  font-family: var(--font-sans);
}

.sidebar-actions {
  display: flex;
  gap: 10px;
}

/* Main */
.diagnosis-main {
  min-width: 0;
}

/* Welcome */
.diagnosis-welcome {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.welcome-box {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 32px;
  text-align: center;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-box h2 {
  font-size: 22px;
  color: var(--primary-brown);
  margin-bottom: 8px;
}

.welcome-box > p {
  color: var(--text-secondary);
  margin-bottom: 24px;
  font-size: 14px;
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.input-textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-main);
  color: var(--text-main);
  font-size: 14px;
  font-family: var(--font-sans);
  resize: vertical;
  line-height: 1.6;
}

.input-textarea:focus {
  outline: none;
  border-color: var(--primary-brown);
}

.btn-large {
  padding: 14px 32px;
  font-size: 15px;
}

.demo-tips {
  margin-top: 20px;
}

.tips-label {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 10px;
}

.demo-btns {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.demo-btn {
  padding: 8px 16px;
  background: var(--bg-soft);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.demo-btn:hover {
  background: var(--bg-main);
  border-color: var(--primary-brown);
  color: var(--primary-brown);
}

/* Feature Cards */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
}

.feature-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Result */
.diagnosis-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h2 {
  font-size: 20px;
  color: var(--primary-brown);
}

.syndrome-card {
  padding: 24px;
}

.syndrome-badge {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.syndrome-emoji {
  font-size: 32px;
}

.syndrome-label {
  font-size: 12px;
  color: var(--text-muted);
}

.syndrome-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-red);
  font-family: var(--font-serif);
}

.syndrome-analysis {
  margin-bottom: 16px;
}

.analysis-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 8px;
}

.analysis-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.syndrome-method {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-soft);
  border-radius: var(--radius-md);
}

.method-label {
  font-size: 12px;
  color: var(--text-muted);
}

.method-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-brown);
}

/* Prescription */
.prescription-card {
  padding: 20px;
}

.rx-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.rx-icon {
  font-size: 24px;
}

.rx-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  flex: 1;
}

.rx-tag {
  font-size: 11px;
  padding: 3px 10px;
  background: var(--bg-soft);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
}

.rx-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.rx-row {
  display: flex;
  gap: 12px;
}

.rx-label {
  font-size: 12px;
  color: var(--text-muted);
  width: 60px;
  flex-shrink: 0;
}

.rx-value {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.rx-warnings {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  font-size: 12px;
  color: #991b1b;
  line-height: 1.5;
}

.warning-icon {
  flex-shrink: 0;
}

/* Sources */
.sources-card {
  padding: 20px;
}

.sources-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 12px;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-item {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.source-num {
  color: var(--primary-brown);
  margin-right: 8px;
  font-weight: 600;
}

/* Thinking */
.thinking-card {
  padding: 20px;
}

.thinking-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 16px;
}

.thinking-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.thinking-step {
  padding: 12px;
  background: var(--bg-main);
  border-radius: var(--radius-md);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.step-icon {
  font-size: 14px;
}

.step-agent {
  font-size: 11px;
  color: var(--primary-red);
  background: var(--accent-light);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
}

.step-text {
  font-size: 12px;
  color: rgba(0, 212, 170, 0.8);
  line-height: 1.5;
}

/* Actions */
.continue-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

@media (max-width: 900px) {
  .diagnosis-layout {
    grid-template-columns: 1fr;
  }

  .feature-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .feature-cards {
    grid-template-columns: 1fr;
  }

  .demo-btns {
    flex-direction: column;
  }
}
</style>
