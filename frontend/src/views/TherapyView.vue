<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">中医外治疗法</h1>
      <p class="page-desc">学习刮痧、拔罐、艾灸等传统外治方法</p>
    </div>

    <!-- 疗法分类 -->
    <div class="therapy-section">
      <div class="section-header">
        <div class="section-tag">六大经典疗法</div>
        <h2 class="section-title">外治疗法学习</h2>
      </div>
      <div class="therapy-grid">
        <div class="therapy-card" v-for="t in therapies" :key="t.name"
             @click="selectTherapy(t)">
          <div class="therapy-icon-wrap" :style="{ borderColor: t.color }">
            <span class="therapy-icon">{{ t.icon }}</span>
          </div>
          <h3 class="therapy-name" :style="{ color: t.color }">{{ t.name }}</h3>
          <p class="therapy-desc">{{ t.shortDesc }}</p>
          <div class="therapy-tags">
            <span class="therapy-tag" v-for="ind in t.indications.slice(0, 3)" :key="ind">{{ ind }}</span>
          </div>
          <div class="therapy-arrow">→</div>
        </div>
      </div>
    </div>

    <!-- 疗法详情 -->
    <div v-if="selectedTherapy" class="therapy-detail card">
      <div class="detail-header">
        <div class="detail-icon-wrap" :style="{ borderColor: selectedTherapy.color }">
          <span class="detail-icon">{{ selectedTherapy.icon }}</span>
        </div>
        <div class="detail-info">
          <h3 :style="{ color: selectedTherapy.color }">{{ selectedTherapy.name }}</h3>
          <p>{{ selectedTherapy.desc }}</p>
        </div>
        <button class="close-btn" @click="selectedTherapy = null">×</button>
      </div>

      <div class="detail-content">
        <div class="detail-section">
          <h4>🏥 适应症状</h4>
          <div class="tags-grid">
            <span class="tag" v-for="s in selectedTherapy.indications" :key="s">{{ s }}</span>
          </div>
        </div>

        <div class="detail-section">
          <h4>⏱️ 操作流程</h4>
          <div class="procedure-list">
            <div class="proc-item" v-for="(step, i) in selectedTherapy.procedure" :key="i">
              <span class="proc-num">{{ i + 1 }}</span>
              <span class="proc-text">{{ step }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>⚠️ 注意事项</h4>
          <ul class="caution-list">
            <li v-for="c in selectedTherapy.cautions" :key="c">{{ c }}</li>
          </ul>
        </div>

        <div class="detail-section">
          <h4>💡 体质匹配</h4>
          <div class="const-match">
            <span class="const-badge" v-for="c in selectedTherapy.constitutionMatch" :key="c.name"
                  :style="{ background: c.color + '22', color: c.color, borderColor: c.color }">
              {{ c.emoji }} {{ c.name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 体质推荐 -->
    <div class="const-recommend-section">
      <div class="section-header">
        <div class="section-tag">体质匹配</div>
        <h2 class="section-title">根据体质选疗法</h2>
      </div>
      <div class="const-grid">
        <div class="const-card" v-for="c in constitutionTherapies" :key="c.name"
             @click="recommendTherapy(c)">
          <span class="const-emoji">{{ c.emoji }}</span>
          <span class="const-name">{{ c.name }}</span>
          <div class="const-tags">
            <span v-for="t in c.therapies" :key="t" class="const-tag">{{ t }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const selectedTherapy = ref(null)

const therapies = [
  {
    name: '刮痧疗法',
    icon: '🌿',
    color: '#6B8E23',
    shortDesc: '通过刮拭经络穴位，排除毒素，活血化瘀',
    desc: '刮痧是中医传统的自然疗法，通过特制的刮痧器具在体表反复刮拭，使皮肤局部充血，达到活血化瘀、清热解毒的目的。',
    indications: ['感冒发热', '颈肩酸痛', '肌肉劳损', '头痛头晕', '湿热体质', '空调病'],
    procedure: [
      '清洁皮肤，涂抹刮痧油或刮痧乳',
      '选择合适的刮痧板，角度保持45°',
      '沿经络走向均匀用力刮拭',
      '每个部位刮20-30次，以出痧为度',
      '刮痧后饮用温开水，注意保暖'
    ],
    cautions: [
      '饭后半小时内不宜刮痧',
      '皮肤破损、感染者禁用',
      '孕妇腰骶部禁用',
      '体质虚弱者力度宜轻',
      '刮痧后4小时内不宜洗澡'
    ],
    constitutionMatch: [
      { name: '痰湿质', emoji: '💧', color: '#34d399' },
      { name: '湿热质', emoji: '🔥', color: '#f59e0b' },
      { name: '血瘀质', emoji: '🩸', color: '#ef4444' }
    ]
  },
  {
    name: '拔罐疗法',
    icon: '🏺',
    color: '#B8860B',
    shortDesc: '负压吸引，活血通络，祛寒除湿',
    desc: '拔罐是以罐为工具，利用燃火、抽气等方法产生负压，使之吸附于体表，造成局部瘀血，达到通经活络、行气活血、消肿止痛、祛风散寒等效果。',
    indications: ['风寒感冒', '肩背疼痛', '腰肌劳损', '湿气重', '慢性疲劳', '失眠多梦'],
    procedure: [
      '选择合适体位，暴露拔罐部位',
      '使用闪火法或投火法将罐吸附',
      '留罐10-15分钟',
      '起罐时轻压罐周皮肤，使其漏气',
      '起罐后观察皮肤颜色变化'
    ],
    cautions: [
      '凝血功能障碍者禁用',
      '皮肤过敏、溃疡处禁用',
      '孕妇腹部、腰骶部禁用',
      '高热抽搐者禁用',
      '拔罐后忌受风寒'
    ],
    constitutionMatch: [
      { name: '阳虚质', emoji: '❄', color: '#a78bfa' },
      { name: '气虚质', emoji: '🫁', color: '#60a5fa' },
      { name: '痰湿质', emoji: '💧', color: '#34d399' }
    ]
  },
  {
    name: '艾灸疗法',
    icon: '🔥',
    color: '#9F2A2A',
    shortDesc: '温通经络，驱寒除湿，保健强身',
    desc: '艾灸是用艾叶制成的艾炷或艾条，点燃后产生的艾热刺激人体穴位或特定部位，通过激发经气活动来调整人体紊乱的生理生化功能。',
    indications: ['宫寒痛经', '胃脘冷痛', '慢性腹泻', '阳痿早泄', '气虚乏力', '阳虚体质'],
    procedure: [
      '选择穴位，清洁皮肤',
      '将艾炷或艾条置于穴位上',
      '用温灸盒或手持艾条悬灸',
      '每个穴位灸15-20分钟',
      '灸至皮肤潮红、患者有温热感'
    ],
    cautions: [
      '实热证、阴虚火旺者慎用',
      '面部、心脏附近慎用直接灸',
      '孕妇腰骶部、腹部禁用',
      '大血管处不宜艾灸',
      '灸后忌食生冷'
    ],
    constitutionMatch: [
      { name: '阳虚质', emoji: '❄', color: '#a78bfa' },
      { name: '气虚质', emoji: '🫁', color: '#60a5fa' },
      { name: '平和质', emoji: '☯', color: '#6B8E23' }
    ]
  },
  {
    name: '推拿按摩',
    icon: '👐',
    color: '#8B5A2B',
    shortDesc: '舒筋活络，调和气血，缓解疲劳',
    desc: '推拿是中医外治法之一，通过手法作用于人体体表的特定部位或穴位，以调节机体的生理、病理状况，达到治疗和保健目的。',
    indications: ['颈肩腰腿痛', '失眠头痛', '消化不良', '小儿疳积', '运动损伤', '慢性疲劳'],
    procedure: [
      '使用滚法、揉法放松肌肉',
      '使用点法、按法刺激穴位',
      '使用拿法、捏法舒筋活络',
      '使用抖法、摇法活动关节',
      '最后用推法、擦法结束'
    ],
    cautions: [
      '急性炎症、骨折处禁用',
      '皮肤破损、感染处禁用',
      '饭后1小时内不宜按摩',
      '按摩力度因人而异',
      '孕妇禁忌穴位勿按'
    ],
    constitutionMatch: [
      { name: '气郁质', emoji: '🌙', color: '#8b5cf6' },
      { name: '血瘀质', emoji: '🩸', color: '#ef4444' },
      { name: '平和质', emoji: '☯', color: '#6B8E23' }
    ]
  },
  {
    name: '针刺疗法',
    icon: '💉',
    color: '#60a5fa',
    shortDesc: '疏通经络，调节阴阳，扶正祛邪',
    desc: '针刺是在中医理论指导下，运用针具刺入人体特定穴位，通过经络传导，调整脏腑气血功能，达到防病治病的目的。',
    indications: ['各种痛症', '神经性疾病', '消化系统疾病', '呼吸系统疾病', '妇科疾病', '亚健康调理'],
    procedure: [
      '辨证取穴，确定治疗方案',
      '消毒针具和穴位',
      '快速进针，调节针感',
      '留针20-30分钟',
      '出针，按压针孔止血'
    ],
    cautions: [
      '必须在专业医师指导下进行',
      '凝血功能障碍者禁用',
      '孕妇禁忌穴位禁用',
      '重要脏器部位慎用',
      '严格消毒，防止感染'
    ],
    constitutionMatch: [
      { name: '气郁质', emoji: '🌙', color: '#8b5cf6' },
      { name: '血瘀质', emoji: '🩸', color: '#ef4444' },
      { name: '痰湿质', emoji: '💧', color: '#34d399' }
    ]
  },
  {
    name: '耳穴贴压',
    icon: '👂',
    color: '#ec4899',
    shortDesc: '刺激耳穴，调节脏腑，操作简便',
    desc: '耳穴贴压是用王不留行籽、磁珠等贴压在耳廓穴位上，通过按压刺激，达到治疗目的。耳为宗脉之所聚，与脏腑经络密切联系。',
    indications: ['失眠多梦', '头痛眩晕', '近视肥胖', '月经不调', '戒烟戒酒', '儿童增高'],
    procedure: [
      '清洁耳廓，寻找敏感点',
      '用探棒按压找出最痛点',
      '消毒后将药籽贴于穴位',
      '每穴适度按压1-2分钟',
      '每天按压3-5次，3-5天更换'
    ],
    cautions: [
      '耳廓皮肤破溃者禁用',
      '孕妇按压宜轻柔',
      '儿童贴压时间宜短',
      '如出现不适立即停用',
      '胶布过敏者慎用'
    ],
    constitutionMatch: [
      { name: '气郁质', emoji: '🌙', color: '#8b5cf6' },
      { name: '特禀质', emoji: '✿', color: '#ec4899' },
      { name: '阴虚质', emoji: '♨', color: '#ff6b6b' }
    ]
  }
]

const constitutionTherapies = [
  { name: '气虚质', emoji: '🫁', color: '#60a5fa', therapies: ['艾灸', '推拿'] },
  { name: '阳虚质', emoji: '❄', color: '#a78bfa', therapies: ['艾灸', '拔罐'] },
  { name: '阴虚质', emoji: '♨', color: '#ff6b6b', therapies: ['耳穴', '推拿'] },
  { name: '痰湿质', emoji: '💧', color: '#34d399', therapies: ['刮痧', '拔罐'] },
  { name: '湿热质', emoji: '🔥', color: '#f59e0b', therapies: ['刮痧', '拔罐'] },
  { name: '血瘀质', emoji: '🩸', color: '#ef4444', therapies: ['刮痧', '针刺'] },
  { name: '气郁质', emoji: '🌙', color: '#8b5cf6', therapies: ['推拿', '耳穴'] },
  { name: '特禀质', emoji: '✿', color: '#ec4899', therapies: ['耳穴', '推拿'] },
  { name: '平和质', emoji: '☯', color: '#6B8E23', therapies: ['艾灸', '推拿'] }
]

function selectTherapy(t) {
  selectedTherapy.value = t
}

function recommendTherapy(c) {
  const therapyCounts = {}
  c.therapies.forEach(tName => {
    const therapy = therapies.find(t => t.name.includes(tName) || tName.includes(t.name[0]))
    if (therapy) {
      therapyCounts[therapy.name] = (therapyCounts[therapy.name] || 0) + 1
    }
  })
  const topTherapy = Object.keys(therapyCounts)[0]
  if (topTherapy) {
    selectedTherapy.value = therapies.find(t => t.name === topTherapy)
  }
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
  margin-bottom: 48px;
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

/* Therapy Grid */
.therapy-section {
  margin-bottom: 48px;
}

.therapy-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.therapy-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.therapy-card:hover {
  background: var(--bg-soft);
  border-color: var(--primary-brown);
}

.therapy-icon-wrap {
  width: 56px;
  height: 56px;
  border: 2px solid;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  background: var(--bg-main);
}

.therapy-icon {
  font-size: 28px;
}

.therapy-name {
  font-size: 16px;
  font-weight: 600;
  font-family: var(--font-serif);
  margin-bottom: 8px;
}

.therapy-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
  font-family: var(--font-sans);
}

.therapy-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.therapy-tag {
  font-size: 10px;
  padding: 3px 8px;
  background: var(--bg-soft);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
}

.therapy-arrow {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 18px;
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.2s;
}

.therapy-card:hover .therapy-arrow {
  opacity: 1;
}

/* Detail */
.therapy-detail {
  margin-bottom: 48px;
  padding: 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 24px;
}

.detail-icon-wrap {
  width: 64px;
  height: 64px;
  border: 2px solid;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-main);
  flex-shrink: 0;
}

.detail-icon {
  font-size: 32px;
}

.detail-info {
  flex: 1;
}

.detail-info h3 {
  font-size: 20px;
  font-weight: 600;
  font-family: var(--font-serif);
  margin-bottom: 6px;
}

.detail-info p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-muted);
  font-size: 20px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--bg-soft);
  color: var(--text-main);
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-brown);
  margin-bottom: 12px;
}

.tags-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 12px;
  padding: 6px 12px;
  background: var(--bg-soft);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
}

.procedure-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.proc-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.proc-num {
  width: 22px;
  height: 22px;
  background: var(--primary-brown);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.proc-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  padding-top: 2px;
}

.caution-list {
  list-style: none;
  padding: 0;
}

.caution-list li {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
  padding-left: 20px;
  position: relative;
}

.caution-list li::before {
  content: '⚠️';
  position: absolute;
  left: 0;
}

.const-match {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.const-badge {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  border: 1px solid;
}

/* Constitution Grid */
.const-recommend-section {
  margin-bottom: 40px;
}

.const-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.const-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.const-card:hover {
  background: var(--bg-soft);
  border-color: var(--primary-brown);
}

.const-emoji {
  font-size: 32px;
}

.const-name {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-serif);
  color: var(--text-main);
}

.const-tags {
  display: flex;
  gap: 6px;
}

.const-tag {
  font-size: 11px;
  padding: 3px 8px;
  background: var(--bg-soft);
  border-radius: var(--radius-sm);
  color: var(--primary-brown);
}

@media (max-width: 900px) {
  .therapy-grid,
  .const-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .therapy-grid,
  .const-grid {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>
