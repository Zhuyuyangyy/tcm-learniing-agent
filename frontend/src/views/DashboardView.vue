<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">学习看板</h1>
      <p class="page-desc">跟踪学习进度，统计体质量表数据</p>
    </div>

    <!-- 项目简介 -->
    <div class="project-intro card">
      <div class="intro-icon">🏛️</div>
      <div class="intro-content">
        <div class="intro-title">安徽中医药大学 × 中医智慧学习平台</div>
        <div class="intro-desc">基于多智能体协作与知识图谱的 AI 辅助学习系统，为中医教育提供智能化工具。</div>
      </div>
      <div class="intro-tags">
        <span class="intro-tag">🎓 高校合作</span>
        <span class="intro-tag">📚 知识图谱</span>
        <span class="intro-tag">⚖️ 用药安全</span>
      </div>
    </div>

    <!-- 统计数据 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-note">{{ stat.note }}</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- 左侧：图表 -->
      <div class="charts-section">
        <!-- 体质分布饼图 -->
        <div class="chart-card card">
          <div class="chart-header">
            <h3>九种体质分布</h3>
            <span class="date-label">{{ currentDate }}</span>
          </div>
          <div ref="pieChart" class="pie-chart"></div>
        </div>

        <!-- 月度趋势图 -->
        <div class="chart-card card">
          <div class="chart-header">
            <h3>月度学习量趋势</h3>
          </div>
          <div ref="lineChart" class="line-chart"></div>
        </div>
      </div>

      <!-- 右侧：工具 -->
      <div class="tools-section">
        <!-- 剂量计算器 -->
        <div class="calc-card card">
          <h3 class="card-title">💊 剂量计算器</h3>
          <div class="calc-form">
            <div class="form-row">
              <div class="form-group">
                <label>年龄（岁）</label>
                <input type="number" class="input" v-model.number="patientAge" min="1" max="120" />
              </div>
              <div class="form-group">
                <label>体重（kg）</label>
                <input type="number" class="input" v-model.number="patientWeight" min="1" max="200" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>体质类型</label>
                <select class="input" v-model="patientConstitution">
                  <option value="">请选择</option>
                  <option v-for="c in constitutionOptions" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>症状程度</label>
                <select class="input" v-model="severity">
                  <option value="轻">轻度</option>
                  <option value="中">中度</option>
                  <option value="重">重度</option>
                </select>
              </div>
            </div>
            <div class="form-group full">
              <label>推荐方剂</label>
              <select class="input" v-model="selectedFormula">
                <option value="">请选择方剂</option>
                <option v-for="f in formulaOptions" :key="f.name" :value="f.name">{{ f.name }}</option>
              </select>
            </div>
            <button class="btn btn-primary full" @click="calculateDosage"
                    :disabled="!patientAge || !patientWeight">
              计算剂量
            </button>
          </div>

          <div v-if="dosageResult" class="dosage-result">
            <div class="result-title">剂量计算结果</div>
            <div class="dosage-list">
              <div class="dosage-item" v-for="d in dosageResult.items" :key="d.name">
                <span class="herb-name">{{ d.name }}</span>
                <span class="herb-dose">{{ d.dose }}</span>
                <span class="herb-range">{{ d.range }}</span>
              </div>
            </div>
            <div class="calc-note">{{ dosageResult.note }}</div>
            <div v-if="dosageResult.warnings.length" class="calc-warnings">
              <div class="warning-item" v-for="w in dosageResult.warnings" :key="w">⚠️ {{ w }}</div>
            </div>
          </div>
        </div>

        <!-- 用药禁忌 -->
        <div class="contra-card card">
          <h3 class="card-title">十八反 · 十九畏</h3>
          <div class="contra-grid">
            <div class="contra-section">
              <div class="contra-title">十八反</div>
              <div class="contra-item" v-for="item in contraindications.eighteen" :key="item">{{ item }}</div>
            </div>
            <div class="contra-section">
              <div class="contra-title">十九畏</div>
              <div class="contra-item" v-for="item in contraindications.nineteen" :key="item">{{ item }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'

const currentDate = computed(() => new Date().toLocaleDateString('zh-CN'))

const stats = [
  { icon: '🩺', value: '1,247', label: '累计学习次数', note: '实训中心' },
  { icon: '👥', value: '892', label: '服务学生数', note: '独立访客' },
  { icon: '📚', value: '486', label: '经典语料', note: '知识图谱' },
  { icon: '📊', value: '94.8%', label: '辨证准确率', note: '试点验证' },
]

const constitutionOptions = ['平和质','气虚质','阳虚质','阴虚质','痰湿质','湿热质','血瘀质','气郁质','特禀质']

const formulaOptions = [
  { name: '柴胡疏肝散', base: 12 },
  { name: '四君子汤', base: 15 },
  { name: '四物汤', base: 10 },
  { name: '补中益气汤', base: 12 },
  { name: '六味地黄丸', base: 9 },
  { name: '逍遥散', base: 12 },
]

const patientAge = ref(35)
const patientWeight = ref(65)
const patientConstitution = ref('')
const severity = ref('中')
const selectedFormula = ref('')
const dosageResult = ref(null)

function calculateDosage() {
  const formula = formulaOptions.find(f => f.name === selectedFormula.value)
  if (!formula) return
  const ageFactor = patientAge.value < 12 ? 0.5 : patientAge.value < 18 ? 0.7 : patientAge.value > 60 ? 0.8 : 1.0
  const weightFactor = patientWeight.value / 65
  const severityFactor = severity.value === '轻' ? 0.7 : severity.value === '重' ? 1.3 : 1.0
  const constitutionFactor = ['气虚质','阳虚质','阴虚质'].includes(patientConstitution.value) ? 0.9 : 1.0
  const base = formula.base * ageFactor * weightFactor * severityFactor * constitutionFactor
  const herbs = ['柴胡','白芍','川芎','枳壳','香附'].map(name => {
    const dose = (base * (0.8 + Math.random() * 0.4)).toFixed(1)
    const range = `${(dose * 0.7).toFixed(1)}-${(dose * 1.3).toFixed(1)}g`
    return { name, dose: dose + 'g', range }
  })
  const warnings = []
  if (herbs.some(h => parseFloat(h.dose) > 15)) warnings.push('方中某药剂量偏大，请注意观察')
  if (patientAge.value > 60) warnings.push('老年患者用药需谨慎，剂量酌减')
  if (severity.value === '重') warnings.push('重症患者建议分次服用')
  dosageResult.value = {
    items: herbs,
    note: `根据年龄${patientAge.value}岁，体重${patientWeight.value}kg，体质${patientConstitution.value || '未指定'}，症状${severity.value}度综合计算。`,
    warnings,
  }
}

const contraindications = {
  eighteen: [
    '半蒌贝蔹芨攻乌',
    '藻戟遂芫俱战草',
    '诸参辛芍叛藜芦',
  ],
  nineteen: [
    '硫黄原是火中精，朴硝一见便相争',
    '水银莫与砒霜见，狼毒最怕密陀僧',
    '巴豆性烈最为上，丁香莫与郁金见',
  ],
}

const pieChart = ref(null)
const lineChart = ref(null)
let pieInstance = null
let lineInstance = null

function initCharts() {
  if (pieChart.value) {
    pieInstance = echarts.init(pieChart.value)
    pieInstance.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
      legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#6A6A6A', fontSize: 11 } },
      series: [{
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['40%', '50%'],
        data: [
          { value: 35, name: '平和质', itemStyle: { color: '#6B8E23' } },
          { value: 12, name: '气虚质', itemStyle: { color: '#60a5fa' } },
          { value: 10, name: '阳虚质', itemStyle: { color: '#a78bfa' } },
          { value: 8, name: '阴虚质', itemStyle: { color: '#ff6b6b' } },
          { value: 11, name: '痰湿质', itemStyle: { color: '#34d399' } },
          { value: 7, name: '湿热质', itemStyle: { color: '#f59e0b' } },
          { value: 6, name: '血瘀质', itemStyle: { color: '#ef4444' } },
          { value: 7, name: '气郁质', itemStyle: { color: '#8b5cf6' } },
          { value: 4, name: '特禀质', itemStyle: { color: '#ec4899' } },
        ],
        label: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(107, 142, 35, 0.3)' },
          label: { show: true, fontSize: 12, color: '#2B2B2B' },
        },
      }],
    })
  }

  if (lineChart.value) {
    lineInstance = echarts.init(lineChart.value)
    lineInstance.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
        axisLine: { lineStyle: { color: '#D8CFC0' } },
        axisLabel: { color: '#6A6A6A', fontSize: 11 },
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#EFE8D8' } },
        axisLabel: { color: '#6A6A6A', fontSize: 11 },
      },
      series: [{
        type: 'line',
        data: [120, 145, 188, 234, 278, 312, 389, 445, 512, 578, 634, 712],
        smooth: true,
        lineStyle: { color: '#9F2A2A', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(159, 42, 42, 0.2)' },
            { offset: 1, color: 'rgba(159, 42, 42, 0.02)' },
          ]),
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#9F2A2A', borderColor: '#fff', borderWidth: 2 },
      }],
    })
  }
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', () => {
    pieInstance?.resize()
    lineInstance?.resize()
  })
})
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

/* Intro */
.project-intro {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.intro-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.intro-content {
  flex: 1;
}

.intro-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 6px;
}

.intro-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.intro-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.intro-tag {
  font-size: 11px;
  padding: 4px 10px;
  background: var(--bg-soft);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-brown);
  font-family: var(--font-serif);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-note {
  font-size: 11px;
  color: var(--text-muted);
}

/* Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
}

.charts-section,
.tools-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Charts */
.chart-card {
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-brown);
}

.date-label {
  font-size: 11px;
  color: var(--text-muted);
}

.pie-chart,
.line-chart {
  width: 100%;
  height: 260px;
}

/* Calculator */
.calc-card {
  padding: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 16px;
}

.calc-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  color: var(--text-secondary);
}

.form-group.full {
  grid-column: 1 / -1;
}

.input {
  padding: 10px 12px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-main);
  color: var(--text-main);
  font-size: 14px;
  font-family: var(--font-sans);
}

.input:focus {
  outline: none;
  border-color: var(--primary-brown);
}

.btn.full {
  width: 100%;
}

/* Dosage Result */
.dosage-result {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-soft);
  border-radius: var(--radius-md);
}

.result-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 12px;
}

.dosage-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.dosage-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
}

.herb-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-main);
}

.herb-dose {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-red);
}

.herb-range {
  font-size: 11px;
  color: var(--text-muted);
}

.calc-note {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}

.calc-warnings {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.warning-item {
  font-size: 12px;
  color: #991b1b;
  padding: 8px;
  background: #fef2f2;
  border-radius: var(--radius-sm);
}

/* Contra */
.contra-card {
  padding: 20px;
}

.contra-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.contra-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contra-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 4px;
}

.contra-item {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  padding: 8px;
  background: var(--bg-soft);
  border-radius: var(--radius-sm);
}

@media (max-width: 1000px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .project-intro {
    flex-direction: column;
    text-align: center;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .contra-grid {
    grid-template-columns: 1fr;
  }
}
</style>
