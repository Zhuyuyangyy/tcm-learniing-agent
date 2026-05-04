<template>
  <div class="home-container">
    <div class="content-wrapper">

      <!-- ===== 横幅 ===== -->
      <section class="hero-banner">
        <div class="banner-content">
          <div class="banner-badge">
            <i class="fa-solid fa-university banner-badge-icon"></i>
            <span>安徽中医药大学 · 实训项目</span>
          </div>
          <h1 class="banner-title">
            <span class="title-main">中医智能诊疗系统</span>
            <span class="title-sub">TCM Mind-RAG</span>
          </h1>
          <p class="banner-desc">
            融合CrewAI多智能体与中医知识图谱<br/>
            九种体质辨识 · 辨证论治训练 · 用药安全审核
          </p>
          <div class="banner-actions">
            <button class="btn btn-primary" @click="$router.push('/chat')">
              <i class="fa-solid fa-stethoscope"></i> 开始学习
            </button>
            <button class="btn btn-secondary" @click="$router.push('/quiz')">
              <i class="fa-solid fa-list-check"></i> 体质测评
            </button>
          </div>
        </div>
        <div class="banner-visual">
          <div class="visual-frame">
            <div class="frame-border"></div>
            <div class="frame-border-inner"></div>
            <div class="frame-content">
              <div class="frame-icon">
                <i class="fa-solid fa-yin-yang"></i>
              </div>
              <div class="frame-text">辨证论治</div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 功能入口 ===== -->
      <section class="section features-section">
        <div class="section-header">
          <div class="section-tag">学习模块</div>
          <h2 class="section-title">核心功能</h2>
          <p class="section-desc">选择模块开始学习</p>
        </div>
        <div class="features-grid">
          <div class="feature-card" v-for="f in features" :key="f.title"
               @click="$router.push(f.route)">
            <div class="feature-icon-wrap">
              <i :class="f.icon"></i>
            </div>
            <div class="feature-body">
              <h3 class="feature-title">{{ f.title }}</h3>
              <p class="feature-desc">{{ f.desc }}</p>
            </div>
            <div class="feature-arrow">
              <i class="fa-solid fa-chevron-right"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 学习流程 ===== -->
      <section class="section flow-section">
        <div class="section-header">
          <div class="section-tag">学习路径</div>
          <h2 class="section-title">辨证论治学习步骤</h2>
          <p class="section-desc">四步掌握辨证论治核心方法</p>
        </div>
        <div class="flow-steps">
          <div class="flow-step" v-for="(step, i) in flowSteps" :key="i">
            <div class="step-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="step-icon">
              <i :class="step.icon"></i>
            </div>
            <h4 class="step-title">{{ step.title }}</h4>
            <p class="step-desc">{{ step.desc }}</p>
          </div>
        </div>
      </section>

      <!-- ===== 体质分类 ===== -->
      <section class="section constitution-section">
        <div class="section-header">
          <div class="section-tag">体质辨识</div>
          <h2 class="section-title">九种体质分类</h2>
          <p class="section-desc">依据《中医体质分类与判定》国家标准</p>
        </div>
        <div class="constitution-grid">
          <div class="constitution-card" v-for="c in constitutions" :key="c.name"
               @click="$router.push('/quiz')">
            <div class="const-name">{{ c.name }}</div>
            <div class="const-trait">{{ c.trait }}</div>
          </div>
        </div>
      </section>

      <!-- ===== 底部CTA ===== -->
      <section class="cta-section">
        <div class="cta-box">
          <h2 class="cta-title">开始学习</h2>
          <p class="cta-desc">中医辨证论治实训系统</p>
          <button class="btn btn-primary" @click="$router.push('/chat')">
            进入学习 <i class="fa-solid fa-arrow-right"></i>
          </button>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
const features = [
  {
    icon: 'fa-solid fa-list-check',
    title: '体质测评',
    desc: '九种体质问卷测评，判定个人体质类型',
    route: '/quiz'
  },
  {
    icon: 'fa-solid fa-stethoscope',
    title: '辨证论治',
    desc: '学习中医辨证论治思路与方法',
    route: '/chat'
  },
  {
    icon: 'fa-solid fa-book-medical',
    title: '知识库',
    desc: '经典医典知识学习与检索',
    route: '/kb'
  },
  {
    icon: 'fa-solid fa-spa',
    title: '外治疗法',
    desc: '刮痧、拔罐、艾灸等传统疗法',
    route: '/therapy'
  },
  {
    icon: 'fa-solid fa-chart-line',
    title: '学习看板',
    desc: '学习进度记录与数据统计',
    route: '/dashboard'
  },
]

const flowSteps = [
  { icon: 'fa-solid fa-clipboard-list', title: '症状采集', desc: '学习收集患者症状信息' },
  { icon: 'fa-solid fa-user-check', title: '体质辨识', desc: '问卷判定患者体质类型' },
  { icon: 'fa-solid fa-brain', title: '辨证分析', desc: '完成证型判断与分析' },
  { icon: 'fa-solid fa-prescription-bottle-medical', title: '选方用药', desc: '学习经典方剂选择' },
]

const constitutions = [
  { name: '平和质', trait: '阴阳调和' },
  { name: '气虚质', trait: '元气不足' },
  { name: '阳虚质', trait: '阳气不足' },
  { name: '阴虚质', trait: '阴液亏少' },
  { name: '痰湿质', trait: '痰湿凝聚' },
  { name: '湿热质', trait: '湿热内蕴' },
  { name: '血瘀质', trait: '血行不畅' },
  { name: '气郁质', trait: '气机郁滞' },
  { name: '特禀质', trait: '先天失常' },
]
</script>

<style scoped>
/* ===== 容器 ===== */
.home-container {
  position: relative;
  min-height: 100vh;
}

/* ===== 内容包装 ===== */
.content-wrapper {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  background: transparent;
  min-height: 100vh;
}

/* ===== 横幅 ===== */
.hero-banner {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 60px;
  align-items: center;
  padding: 56px 0 72px;
}

.banner-content {
  max-width: 520px;
}

.banner-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  background: var(--bg-section);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-family: var(--font-sans);
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.banner-badge-icon {
  color: var(--primary);
  font-size: 13px;
}

.banner-title {
  margin-bottom: 20px;
}

.title-main {
  display: block;
  font-size: 42px;
  font-weight: 700;
  font-family: var(--font-serif);
  color: var(--text);
  letter-spacing: 4px;
  margin-bottom: 6px;
}

.title-sub {
  display: block;
  font-size: 18px;
  font-weight: 400;
  font-family: var(--font-sans);
  color: var(--text-secondary);
  letter-spacing: 2px;
}

.banner-desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.8;
  font-family: var(--font-sans);
  margin-bottom: 32px;
}

.banner-actions {
  display: flex;
  gap: 14px;
}

.banner-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}

.visual-frame {
  position: relative;
  width: 260px;
  height: 260px;
}

.frame-border {
  position: absolute;
  inset: 0;
  border: 1px solid var(--border-dark);
  border-radius: 50%;
}

.frame-border-inner {
  position: absolute;
  inset: 20px;
  border: 1px solid var(--border);
  border-radius: 50%;
}

.frame-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.frame-icon {
  font-size: 48px;
  color: var(--primary);
  margin-bottom: 10px;
}

.frame-text {
  font-size: 14px;
  font-family: var(--font-serif);
  color: var(--text-secondary);
  letter-spacing: 3px;
}

/* ===== Section通用 ===== */
.section {
  padding: 52px 0;
  border-top: 1px solid var(--border);
}

.section-header {
  text-align: center;
  margin-bottom: 36px;
}

.section-tag {
  display: inline-block;
  padding: 3px 12px;
  font-size: 12px;
  font-family: var(--font-sans);
  color: var(--primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  margin-bottom: 10px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  font-family: var(--font-serif);
  color: var(--text);
  margin-bottom: 8px;
}

.section-desc {
  font-size: 14px;
  color: var(--text-secondary);
  font-family: var(--font-sans);
}

/* ===== 功能卡片 ===== */
.features-section {
  background: rgba(255, 255, 255, 0.65);
  margin: 0 -20px;
  padding: 52px 40px;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  max-width: 960px;
  margin: 0 auto;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.feature-card:hover {
  border-color: var(--secondary);
}

.feature-card:hover .feature-arrow {
  color: var(--secondary);
}

.feature-icon-wrap {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}

.feature-body {
  flex: 1;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-sans);
  color: var(--text);
  margin-bottom: 3px;
}

.feature-desc {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  line-height: 1.5;
}

.feature-arrow {
  font-size: 13px;
  color: var(--text-muted);
  transition: color 0.2s ease;
}

/* ===== 流程 ===== */
.flow-section {
  background: rgba(240, 237, 230, 0.6);
  margin: 0 -20px;
  padding: 52px 40px;
}

.flow-steps {
  display: flex;
  justify-content: center;
  gap: 32px;
  max-width: 880px;
  margin: 0 auto;
}

.flow-step {
  flex: 1;
  max-width: 180px;
  text-align: center;
}

.step-num {
  font-size: 12px;
  font-family: var(--font-sans);
  color: var(--text-muted);
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.step-icon {
  font-size: 28px;
  color: var(--primary);
  margin-bottom: 14px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-sans);
  color: var(--text);
  margin-bottom: 8px;
}

.step-desc {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  line-height: 1.5;
}

/* ===== 体质 ===== */
.constitution-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-width: 720px;
  margin: 0 auto;
}

.constitution-card {
  padding: 18px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.constitution-card:hover {
  border-color: var(--primary);
}

.const-name {
  font-size: 15px;
  font-weight: 600;
  font-family: var(--font-serif);
  color: var(--text);
  margin-bottom: 4px;
}

.const-trait {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-sans);
}

/* ===== CTA ===== */
.cta-section {
  padding: 52px 0;
  border-top: 1px solid var(--border);
  text-align: center;
}

.cta-box {
  padding: 32px;
}

.cta-title {
  font-size: 22px;
  font-weight: 600;
  font-family: var(--font-serif);
  color: var(--text);
  margin-bottom: 8px;
}

.cta-desc {
  font-size: 14px;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  margin-bottom: 20px;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .hero-banner {
    grid-template-columns: 1fr;
    gap: 32px;
    padding: 40px 0 56px;
  }

  .banner-visual {
    display: none;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .flow-steps {
    gap: 16px;
  }

  .constitution-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .features-section,
  .flow-section {
    margin: 0 -20px;
    padding: 40px 20px;
  }
  
  .content-wrapper {
    padding: 0 20px;
  }
}

@media (max-width: 600px) {
  .features-grid {
    grid-template-columns: 1fr;
  }

  .constitution-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
