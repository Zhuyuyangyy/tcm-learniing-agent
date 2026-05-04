<template>
  <div class="bzlz-page">
    <div class="page-bg"></div>
    <div class="bg-mountain"></div>
    <div class="bg-ink left"></div>
    <div class="bg-ink right"></div>
    <div class="bg-bamboo left"></div>
    <div class="bg-bamboo right"></div>

    <section class="title-area">
      <h1 class="title">辨证论治</h1>
      <div class="title-subline">
        <span class="subline"></span>
        <span class="subline-mark">⟡</span>
        <span class="subtitle">学习中医辨证论治思路与方法</span>
        <span class="cloud-icon">
          <svg viewBox="0 0 64 28" aria-hidden="true">
            <path d="M14 21h30a8 8 0 0 0 1.5-15.8 11 11 0 0 0-20.9 2.3A7.2 7.2 0 0 0 14 21z" />
            <path d="M8 21c-3.2 0-5.7-2.3-5.7-5.3S4.8 10.5 8 10.5c1.5 0 2.8.5 3.9 1.4" />
            <path d="M44 7.6c1.6-1.6 3.6-2.4 6-2.4 4.9 0 8.8 3.8 8.8 8.6 0 3.9-2.8 7.2-6.7 8.1" />
          </svg>
        </span>
      </div>
    </section>

    <section class="main-layout">
      <aside class="left-panel">
        <div class="side-card">
          <div class="side-title">
            <i class="fa-solid fa-notes-medical"></i>
            <span>症状选择</span>
          </div>
          <div class="chip-list">
            <button
              v-for="item in symptoms"
              :key="item"
              type="button"
              class="chip"
              :class="{ active: selectedSymptoms.includes(item), ghost: item === '...' }"
              @click="toggleSymptom(item)"
            >
              {{ item }}
            </button>
          </div>
        </div>

        <div class="side-card">
          <div class="side-title">
            <i class="fa-solid fa-magnifying-glass"></i>
            <span>证型参考</span>
          </div>
          <div class="chip-list">
            <button
              v-for="item in syndromeTypes"
              :key="item"
              type="button"
              class="chip chip-soft"
              :class="{ active: selectedSymptoms.includes(item), ghost: item === '...' }"
              @click="toggleSymptom(item)"
            >
              {{ item }}
            </button>
          </div>
        </div>

        <div class="side-card department-card">
          <div class="side-title">
            <i class="fa-regular fa-clipboard"></i>
            <span>科室</span>
          </div>
          <div class="select-box">
            <select v-model="department" class="dept-select">
              <option value="内科">中医内科</option>
              <option value="妇科">中医妇科</option>
              <option value="儿科">中医儿科</option>
              <option value="骨伤科">骨伤科</option>
              <option value="皮肤科">皮肤科</option>
            </select>
          </div>
        </div>

        <button type="button" class="clear-button" @click="clearAll">清空</button>
      </aside>

      <div class="content-panel">
        <div class="study-card">
          <div class="floating-cloud cloud-left">
            <svg viewBox="0 0 64 28" aria-hidden="true">
              <path d="M14 21h30a8 8 0 0 0 1.5-15.8 11 11 0 0 0-20.9 2.3A7.2 7.2 0 0 0 14 21z" />
              <path d="M8 21c-3.2 0-5.7-2.3-5.7-5.3S4.8 10.5 8 10.5c1.5 0 2.8.5 3.9 1.4" />
            </svg>
          </div>

          <div class="intro-grid">
            <div class="taiji-box">
              <img src="/bianzhenglunzhi-taiji.png" alt="太极图" class="taiji-image" />
            </div>

            <div class="input-panel">
              <div class="study-icon">
                <i class="fa-regular fa-clipboard"></i>
              </div>
              <h2>辨证论治学习</h2>
              <div class="mini-subtitle">
                <span class="mini-line"></span>
                <span>描述症状或从左侧选择，开始学习辨证</span>
                <span class="mini-line"></span>
              </div>

              <div class="textarea-wrap">
                <textarea
                  v-model="inputText"
                  maxlength="200"
                  rows="5"
                  class="symptom-textarea"
                  placeholder="输入症状描述，如：头痛、乏力、食欲不振..."
                ></textarea>
                <span class="counter">{{ inputText.length }}/200</span>
              </div>

              <button
                type="button"
                class="start-button"
                :disabled="!inputText.trim() && !selectedSymptoms.length"
                @click="submitDiagnosis"
              >
                开始学习 →
              </button>

              <div class="demo-area">
                <span class="demo-label">
                  <i class="fa-solid fa-lightbulb"></i>
                  演示案例：
                </span>
                <div class="demo-list">
                  <button
                    v-for="item in demoPrompts"
                    :key="item.text"
                    type="button"
                    class="demo-chip"
                    @click="useDemo(item.text)"
                  >
                    {{ item.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="feature-grid">
          <button
            v-for="item in features"
            :key="item.title"
            type="button"
            class="feature-card"
          >
            <span class="feature-icon">
              <i :class="item.icon"></i>
            </span>
            <span class="feature-text">
              <strong>{{ item.title }}</strong>
              <em>{{ item.desc }}</em>
            </span>
            <span class="feature-arrow">›</span>
          </button>
        </div>

        <section v-if="currentResult" class="result-card-wrap">
          <div class="result-header">
            <h3>辨证结果</h3>
            <div class="result-actions">
              <button type="button" class="result-button" @click="clearResult">重新学习</button>
              <button type="button" class="result-button primary" @click="$router.push('/therapy')">查看外治疗法</button>
            </div>
          </div>

          <div class="result-grid">
            <article class="result-card highlight">
              <div class="result-tag">辨证结果</div>
              <h4>{{ currentResult.syndrome }}</h4>
              <p>{{ currentResult.analysis }}</p>
              <div class="method-row">
                <span>治法</span>
                <strong>{{ currentResult.method }}</strong>
              </div>
            </article>

            <article v-if="currentResult.prescription" class="result-card">
              <div class="result-tag">经典处方</div>
              <h4>{{ currentResult.prescription.name }}</h4>
              <p>{{ currentResult.prescription.composition }}</p>
              <p>剂量：{{ currentResult.prescription.dosage }}</p>
              <p>煎服法：{{ currentResult.prescription.usage }}</p>
              <p v-if="currentResult.prescription.warnings" class="warning">
                注意：{{ currentResult.prescription.warnings }}
              </p>
            </article>

            <article class="result-card">
              <div class="result-tag">参考来源</div>
              <ul class="result-list">
                <li v-for="(item, index) in currentResult.sources" :key="index">{{ item }}</li>
              </ul>
            </article>

            <article class="result-card">
              <div class="result-tag">学习分析</div>
              <ul class="result-list">
                <li v-for="(item, index) in currentResult.thinking" :key="index">
                  <strong>{{ item.agent }}</strong>：{{ item.text }}
                </li>
              </ul>
            </article>
          </div>
        </section>
      </div>
    </section>
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
  '失眠', '多梦', '焦虑', '抑郁', '记忆力下降', '...'
]

const syndromeTypes = [
  '肝气郁结', '气血两虚', '脾胃虚弱', '肾阳不足',
  '肺气不固', '心火亢盛', '痰湿内阻', '血瘀脉络',
  '阴虚火旺', '阳虚水泛', '湿热下注', '风寒束表', '...'
]

const features = [
  { icon: 'fa-solid fa-bullseye', title: '辨证分析', desc: '学习证型判断方法' },
  { icon: 'fa-solid fa-scale-balanced', title: '用药安全', desc: '十八反十九畏审核' },
  { icon: 'fa-regular fa-note-sticky', title: '经典处方', desc: '伤寒金匮经典方剂' },
  { icon: 'fa-solid fa-mortar-pestle', title: '方剂加减', desc: '因人因时灵活化裁' }
]

const demoPrompts = [
  { label: '肝气郁结案例', text: '胸胁胀痛、情志抑郁、脉弦' },
  { label: '肾阴虚案例', text: '腰膝酸软、潮热盗汗、头晕耳鸣' },
  { label: '气血两虚案例', text: '气短懒言、疲劳乏力、面色萎黄' }
]

function toggleSymptom(item) {
  if (item === '...') return
  const index = selectedSymptoms.value.indexOf(item)
  if (index >= 0) {
    selectedSymptoms.value.splice(index, 1)
  } else {
    selectedSymptoms.value.push(item)
  }
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

  const display = hasSymptoms ? `${text}；症状：${selectedSymptoms.value.join('、')}` : text
  const inputLower = display.toLowerCase()

  const syndromeMap = [
    {
      keywords: ['胸胁', '肝气', '情志', '抑郁', '脉弦', '胀痛', '胁肋', '心烦', '失眠'],
      syndrome: '肝气郁结证',
      method: '疏肝解郁，健脾理气',
      analysis: '肝主疏泄，调畅气机，情志不畅则肝气郁结；肝气犯脾，脾失健运，故见食欲不振、腹胀乏力。治疗当疏肝健脾，调和肝脾。',
      prescription: {
        name: '柴胡疏肝散加减',
        type: '经典方剂',
        composition: '柴胡12g，白芍15g、川芎10g、香附10g、枳壳10g、陈皮8g、党参15g，白术12g、茯苓15g、炙甘草6g',
        dosage: '每日1剂，水煎分两次温服',
        usage: '早饭前、晚饭后半小时温服，忌食生冷油腻',
        warnings: '孕妇慎用；如出现口干舌燥等阴虚症状需调整方剂'
      },
      sources: [
        '《伤寒论》第96条：伤寒五六日，中风，往来寒热，胸胁苦满...',
        '《金匮要略》：见肝之病，知肝传脾，当先实脾',
        '《中医内科学》肝气郁结证：疏肝理气，柴胡疏肝散主之'
      ],
      thinking: [
        { agent: '症状建档', text: '建档分析：根据症状描述，构建患者画像与体质关联...' },
        { agent: '辨证检索', text: '知识检索：匹配《伤寒论》《金匮要略》相关条文...' },
        { agent: '辨证分析', text: '辨证分析：综合判断为“肝气郁结、脾胃虚弱”证...' },
        { agent: '用药审核', text: '安全审核：检查十八反十九畏，无配伍禁忌...' },
        { agent: '方药生成', text: '处方生成：柴胡疏肝散加减化裁...' },
        { agent: '调护规划', text: '调护规划：给出阶段性康复方案与饮食禁忌...' }
      ]
    },
    {
      keywords: ['腰膝', '肾', '盗汗', '潮热', '阴虚', '耳鸣', '虚火', '口干'],
      syndrome: '肾阴虚证',
      method: '滋阴补肾，清热降火',
      analysis: '肾主骨生髓，腰为肾之府。肾阴不足，虚火内扰，故见腰膝酸软、潮热盗汗、头晕耳鸣。治宜滋阴补肾，壮水之主。',
      prescription: {
        name: '六味地黄丸加减',
        type: '经典方剂',
        composition: '熟地黄20g、山茱萸15g、山药15g、泽泻10g、茯苓12g、丹皮10g、枸杞子12g、菊花10g',
        dosage: '每日1剂，水煎分两次服',
        usage: '午饭前、晚饭后温服，忌食辛辣刺激性食物',
        warnings: '脾虚便溏者慎用；感冒发热期间暂停服用'
      },
      sources: [
        '《小儿药证直诀》：地黄丸治肾怯失音，囟开不合，神不足...',
        '《中医内科学》肾阴虚证：滋补肾阴，六味地黄丸主之',
        '《医宗必读》：肾为先天之本，藏精生髓'
      ],
      thinking: [
        { agent: '症状建档', text: '建档分析：患者主诉腰膝酸软、潮热盗汗...' },
        { agent: '辨证检索', text: '知识检索：检索《中医内科学》肾阴虚证诊断标准...' },
        { agent: '辨证分析', text: '辨证分析：腰为肾之府，肾阴不足，虚火内扰...' },
        { agent: '用药审核', text: '安全审核：六味地黄丸配伍安全，无禁忌...' },
        { agent: '方药生成', text: '处方生成：六味地黄丸加枸杞子、菊花清热...' },
        { agent: '调护规划', text: '调护规划：节制房事，宜食滋阴之品...' }
      ]
    },
    {
      keywords: ['气虚', '乏力', '疲劳', '气短', '懒言', '自汗', '面色', '食欲不振', '心慌'],
      syndrome: '气血两虚证',
      method: '补气养血，健脾益胃',
      analysis: '气虚则推动无力，故乏力、气短、懒言；血虚则面容失养，故面色萎黄。心脾两虚，气血不足。治宜补中益气，养血安神。',
      prescription: {
        name: '补中益气汤合四物汤加减',
        type: '合方加减',
        composition: '黄芪30g、党参20g，白术15g、炙甘草10g，当归12g、熟地黄15g，白芍12g、川芎8g、陈皮6g、升麻6g',
        dosage: '每日1剂，水煎分两次温服',
        usage: '早饭前、晚饭后温服，忌食生冷、辛辣',
        warnings: '阴虚火旺、实热证者慎用；高血压患者慎服升麻'
      },
      sources: [
        '《脾胃论》：补中益气汤治脾胃气虚，清阳下陷',
        '《太平惠民和剂局方》：四物汤治营血虚滞，月经不调',
        '《中医内科学》气血两虚证：补气养血，八珍汤主之'
      ],
      thinking: [
        { agent: '症状建档', text: '建档分析：患者气虚症状明显，属气血两虚...' },
        { agent: '辨证检索', text: '知识检索：检索《脾胃论》补中益气汤方义...' },
        { agent: '辨证分析', text: '辨证分析：气虚推动无力，血虚面容失养...' },
        { agent: '用药审核', text: '安全审核：黄芪、党参、当归配伍安全...' },
        { agent: '方药生成', text: '处方生成：补中益气汤合四物汤气血双补...' },
        { agent: '调护规划', text: '调护规划：适度运动，八段锦健脾益气...' }
      ]
    }
  ]

  let selected = syndromeMap[0]
  for (const item of syndromeMap) {
    if (item.keywords.some((keyword) => inputLower.includes(keyword))) {
      selected = item
      break
    }
  }

  currentResult.value = {
    syndrome: selected.syndrome,
    method: selected.method,
    analysis: selected.analysis,
    prescription: selected.prescription,
    sources: selected.sources,
    thinking: selected.thinking
  }
}
</script>

<style scoped>
.bzlz-page {
  position: relative;
  max-width: 1280px;
  margin: 0 auto;
  padding: 20px 18px 34px;
  min-height: calc(100vh - 60px);
}

.page-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 0%, rgba(211, 185, 145, 0.16), transparent 26%),
    radial-gradient(circle at 50% 42%, rgba(255, 255, 255, 0.88), transparent 34%),
    linear-gradient(180deg, rgba(252, 249, 243, 0.98), rgba(245, 239, 229, 0.94));
  z-index: -5;
}

.bg-mountain,
.bg-ink,
.bg-bamboo {
  pointer-events: none;
  position: absolute;
  z-index: -4;
}

.bg-mountain {
  left: 10px;
  top: 40px;
  width: 240px;
  height: 110px;
  opacity: 0.18;
  background:
    radial-gradient(ellipse at 18% 92%, rgba(145, 149, 140, 0.75) 0 16%, transparent 17%),
    radial-gradient(ellipse at 42% 95%, rgba(173, 177, 168, 0.62) 0 18%, transparent 19%),
    radial-gradient(circle at 76% 18%, rgba(190, 170, 128, 0.5) 0 9%, transparent 10%);
}

.bg-ink {
  width: 240px;
  height: 220px;
  opacity: 0.18;
}

.bg-ink.left {
  left: -18px;
  bottom: 6px;
  background:
    radial-gradient(circle at 18% 78%, rgba(128, 136, 118, 0.32), transparent 36%),
    radial-gradient(circle at 44% 94%, rgba(160, 165, 149, 0.34), transparent 34%);
}

.bg-ink.right {
  right: -18px;
  bottom: 44px;
  background:
    radial-gradient(circle at 68% 74%, rgba(130, 138, 122, 0.3), transparent 34%),
    radial-gradient(circle at 34% 92%, rgba(166, 168, 153, 0.32), transparent 30%);
}

.bg-bamboo {
  width: 176px;
  height: 176px;
  opacity: 0.26;
}

.bg-bamboo::before,
.bg-bamboo::after {
  content: '';
  position: absolute;
  background: rgba(132, 151, 126, 0.75);
  border-radius: 999px;
}

.bg-bamboo.left {
  left: -10px;
  bottom: 204px;
}

.bg-bamboo.left::before {
  width: 2px;
  height: 114px;
  left: 26px;
  bottom: 14px;
  transform: rotate(16deg);
}

.bg-bamboo.left::after {
  width: 58px;
  height: 16px;
  left: 2px;
  bottom: 84px;
  transform: rotate(-26deg);
  box-shadow:
    16px 18px 0 rgba(132, 151, 126, 0.55),
    4px 42px 0 rgba(132, 151, 126, 0.46);
}

.bg-bamboo.right {
  top: 8px;
  right: -4px;
}

.bg-bamboo.right::before {
  width: 2px;
  height: 126px;
  right: 40px;
  top: 0;
  transform: rotate(14deg);
}

.bg-bamboo.right::after {
  width: 70px;
  height: 16px;
  right: 0;
  top: 24px;
  transform: rotate(22deg);
  box-shadow:
    -12px 24px 0 rgba(132, 151, 126, 0.52),
    -20px 48px 0 rgba(132, 151, 126, 0.44);
}

.title-area {
  text-align: center;
  margin-bottom: 12px;
}

.title {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 58px;
  line-height: 1.06;
  letter-spacing: 4px;
  color: #2f5c4f;
  text-shadow: 0 4px 14px rgba(47, 92, 79, 0.08);
}

.title-subline {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #c6a06a;
}

.subline {
  width: 90px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(198, 160, 106, 0.9), transparent);
}

.subline-mark {
  font-size: 14px;
}

.subtitle {
  font-size: 15px;
  color: #737168;
}

.cloud-icon {
  display: inline-flex;
  align-items: center;
}

.cloud-icon svg {
  width: 38px;
  height: 18px;
  fill: none;
  stroke: #d9b27b;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.main-layout {
  display: grid;
  grid-template-columns: 292px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.side-card,
.study-card,
.feature-card,
.result-card-wrap {
  background: rgba(255, 252, 247, 0.88);
  border: 1px solid rgba(223, 212, 196, 0.86);
  box-shadow:
    0 14px 36px rgba(162, 139, 104, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.side-card {
  border-radius: 10px;
  padding: 14px 14px 14px;
}

.department-card {
  padding-bottom: 14px;
}

.side-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #2f5d50;
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 700;
}

.side-title i {
  font-size: 14px;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.chip {
  height: 26px;
  padding: 0 13px;
  border-radius: 8px;
  border: 1px solid rgba(231, 224, 214, 0.95);
  background: #f2eee8;
  color: #736d62;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip-soft {
  background: #f4efe8;
}

.chip:hover,
.chip.active {
  background: #2f6959;
  border-color: #2f6959;
  color: #fff;
}

.chip.ghost {
  min-width: 36px;
}

.select-box {
  position: relative;
}

.select-box::after {
  content: '⌄';
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #93897b;
  pointer-events: none;
}

.dept-select {
  width: 100%;
  height: 34px;
  padding: 0 34px 0 12px;
  border-radius: 8px;
  border: 1px solid rgba(226, 216, 202, 0.96);
  background: rgba(255, 253, 249, 0.96);
  color: #665f55;
  font-size: 14px;
  appearance: none;
}

.clear-button {
  width: 66px;
  height: 34px;
  border-radius: 6px;
  border: 1px solid #7a9c89;
  background: rgba(255, 255, 255, 0.7);
  color: #2f6959;
  font-size: 14px;
  cursor: pointer;
}

.content-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.study-card {
  position: relative;
  border-radius: 14px;
  padding: 18px 18px 16px;
  overflow: hidden;
}

.study-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 22% 36%, rgba(224, 209, 184, 0.28), transparent 18%),
    radial-gradient(circle at 74% 40%, rgba(255, 255, 255, 0.85), transparent 32%);
  pointer-events: none;
}

.floating-cloud {
  position: absolute;
  left: 16px;
  top: 56px;
  opacity: 0.58;
}

.floating-cloud svg {
  width: 62px;
  height: 26px;
  fill: none;
  stroke: #e2c495;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.intro-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  min-height: 372px;
}

.taiji-box {
  display: flex;
  align-items: center;
  justify-content: center;
}

.taiji-image {
  width: 292px;
  max-width: 100%;
  object-fit: contain;
  filter: drop-shadow(0 12px 18px rgba(117, 113, 93, 0.14));
}

.input-panel {
  text-align: center;
}

.study-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 14px;
  color: #2f6959;
  font-size: 40px;
}

.input-panel h2 {
  margin: 8px 0 8px;
  font-family: var(--font-serif);
  font-size: 30px;
  letter-spacing: 2px;
  color: #2f5d50;
}

.mini-subtitle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
  color: #878177;
  font-size: 14px;
}

.mini-line {
  width: 74px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(208, 174, 120, 0.84), transparent);
}

.textarea-wrap {
  position: relative;
  max-width: 490px;
  margin: 0 auto;
}

.symptom-textarea {
  width: 100%;
  min-height: 110px;
  padding: 16px 18px 30px;
  border-radius: 10px;
  border: 1px solid rgba(221, 210, 196, 0.94);
  background: rgba(255, 255, 255, 0.86);
  color: #6b665b;
  font-size: 14px;
  line-height: 1.8;
  resize: none;
}

.symptom-textarea:focus {
  outline: none;
  border-color: rgba(47, 105, 89, 0.42);
  box-shadow: 0 0 0 3px rgba(47, 105, 89, 0.08);
}

.counter {
  position: absolute;
  right: 12px;
  bottom: 10px;
  color: #aca394;
  font-size: 12px;
}

.start-button {
  margin-top: 12px;
  width: 100%;
  max-width: 490px;
  height: 38px;
  border: none;
  border-radius: 4px;
  background: linear-gradient(180deg, #2f6b5a, #2a5e4f);
  color: #fff;
  font-size: 16px;
  letter-spacing: 1px;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(47, 105, 89, 0.18);
}

.start-button:disabled {
  opacity: 0.56;
  cursor: not-allowed;
  box-shadow: none;
}

.demo-area {
  margin-top: 14px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.demo-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #837a6d;
  font-size: 13px;
  line-height: 32px;
}

.demo-label i {
  color: #efbb4d;
}

.demo-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.demo-chip {
  height: 30px;
  padding: 0 14px;
  border-radius: 7px;
  border: 1px solid rgba(230, 220, 206, 0.96);
  background: rgba(245, 240, 232, 0.95);
  color: #756c5f;
  font-size: 13px;
  cursor: pointer;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.feature-card {
  min-height: 78px;
  border-radius: 10px;
  padding: 16px 18px 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
  cursor: pointer;
}

.feature-icon {
  width: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #cf9c35;
  font-size: 30px;
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.feature-text strong {
  font-family: var(--font-serif);
  font-size: 20px;
  color: #2f5d50;
}

.feature-text em {
  font-style: normal;
  font-size: 12px;
  color: #82796d;
}

.feature-arrow {
  color: #356957;
  font-size: 20px;
}

.result-card-wrap {
  border-radius: 14px;
  padding: 18px;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.result-header h3 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 30px;
  color: #2f5d50;
}

.result-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.result-button {
  height: 34px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px solid rgba(124, 157, 140, 0.76);
  background: rgba(255, 255, 255, 0.78);
  color: #2f6959;
  cursor: pointer;
}

.result-button.primary {
  background: #2f6959;
  color: #fff;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.result-card {
  border-radius: 12px;
  border: 1px solid rgba(225, 214, 199, 0.94);
  background: rgba(255, 255, 255, 0.76);
  padding: 18px;
}

.result-card.highlight {
  background: linear-gradient(145deg, rgba(248, 244, 236, 0.96), rgba(255, 253, 249, 0.96));
}

.result-tag {
  color: #bb9360;
  font-size: 12px;
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.result-card h4 {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 24px;
  color: #2f5d50;
}

.result-card p,
.result-list li {
  color: #6d665b;
  font-size: 14px;
  line-height: 1.8;
}

.method-row {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(241, 236, 229, 0.96);
}

.method-row span {
  color: #8d8578;
  font-size: 12px;
  margin-right: 10px;
}

.method-row strong {
  color: #2f6959;
  font-size: 15px;
}

.warning {
  color: #995646;
}

.result-list {
  margin: 0;
  padding-left: 18px;
}

.result-list strong {
  color: #2f5d50;
}

@media (max-width: 1080px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .intro-grid {
    grid-template-columns: 1fr;
  }

  .feature-grid,
  .result-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .bzlz-page {
    padding: 22px 14px 34px;
  }

  .title {
    font-size: 40px;
  }

  .subtitle {
    font-size: 13px;
  }

  .subline,
  .mini-line {
    width: 38px;
  }

  .study-card {
    padding: 18px 14px 16px;
  }

  .taiji-image {
    width: 210px;
  }

  .feature-grid,
  .result-grid {
    grid-template-columns: 1fr;
  }

  .result-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
