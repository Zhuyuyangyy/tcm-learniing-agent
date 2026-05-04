<template>
  <div class="therapy-page">
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
        <h1>中医外治疗法</h1>
        <span class="curl">〰</span>
        <span class="line"></span>
      </div>
      <p>学习刮痧、拔罐、艾灸等传统外治方法</p>
    </section>

    <section class="therapy-overview">
      <div class="section-chip-row">
        <span class="section-chip-line"></span>
        <span class="section-chip-mark">◇</span>
        <span class="section-chip">六大经典疗法</span>
        <span class="section-chip-mark">◇</span>
        <span class="section-chip-line"></span>
      </div>

      <div class="section-title-row">
        <span class="title-line"></span>
        <span class="title-mark">◇</span>
        <h2>外治疗法学习</h2>
        <span class="title-mark">◇</span>
        <span class="title-line"></span>
      </div>

      <div class="therapy-grid">
        <button
          v-for="item in therapies"
          :key="item.name"
          type="button"
          class="therapy-card"
          :class="{ active: selectedTherapy?.name === item.name }"
          @click="selectTherapy(item)"
        >
          <span class="therapy-icon-box" :style="{ borderColor: item.color }">
            <i :class="item.icon" :style="{ color: item.color }"></i>
          </span>
          <strong :style="{ color: item.color }">{{ item.name }}</strong>
          <p>{{ item.shortDesc }}</p>
          <div class="therapy-tags">
            <span v-for="tag in item.indications.slice(0, 3)" :key="tag">{{ tag }}</span>
          </div>
        </button>
      </div>

      <transition name="detail-expand" mode="out-in">
        <section v-if="selectedTherapy && detailSection === 'therapy'" ref="therapyDetailRef" class="detail-panel inline-detail">
        <div class="detail-header">
          <div class="detail-title">
            <span class="detail-icon-box" :style="{ borderColor: selectedTherapy.color }">
              <i :class="selectedTherapy.icon" :style="{ color: selectedTherapy.color }"></i>
            </span>
            <div>
              <h3 :style="{ color: selectedTherapy.color }">{{ selectedTherapy.name }}</h3>
              <p>{{ selectedTherapy.desc }}</p>
            </div>
          </div>
          <button class="close-btn" @click="closeDetail">×</button>
        </div>

        <div class="detail-tabs">
          <button
            v-for="item in detailTabs"
            :key="item.key"
            type="button"
            class="detail-tab"
            :class="{ active: activeDetailTab === item.key }"
            @click="activeDetailTab = item.key"
          >
            {{ item.label }}
          </button>
        </div>

        <transition name="tab-fade" mode="out-in">
          <div class="detail-grid" :key="`therapy-${selectedTherapy.name}-${activeDetailTab}`">
          <article v-if="activeDetailTab === 'symptoms'" class="detail-card single-card">
            <h4>适应症状</h4>
            <div class="detail-tags">
              <span v-for="item in selectedTherapy.indications" :key="item">{{ item }}</span>
            </div>
          </article>

          <article v-else-if="activeDetailTab === 'procedure'" class="detail-card single-card">
            <h4>操作流程</h4>
            <ol class="detail-list">
              <li v-for="item in selectedTherapy.procedure" :key="item">{{ item }}</li>
            </ol>
          </article>

          <article v-else-if="activeDetailTab === 'cautions'" class="detail-card single-card">
            <h4>注意事项</h4>
            <ul class="detail-list">
              <li v-for="item in selectedTherapy.cautions" :key="item">{{ item }}</li>
            </ul>
          </article>

          <article v-else class="detail-card single-card">
            <h4>体质匹配</h4>
            <div class="detail-tags colorful">
              <button
                v-for="item in selectedTherapy.constitutionMatch"
                :key="item.name"
                type="button"
                class="constitution-link"
                :style="{ color: item.color, borderColor: item.color, background: `${item.color}12` }"
                @click="pickMatchedConstitution(item.name)"
              >
                {{ item.emoji }} {{ item.name }}
              </button>
            </div>
          </article>
          </div>
        </transition>

        <div class="detail-actions">
          <button type="button" class="pager-btn" @click="stepTherapy(-1)">上一项</button>
          <button type="button" class="pager-btn primary" @click="stepTherapy(1)">下一项</button>
        </div>
        </section>
      </transition>
    </section>

    <section class="constitution-head">
      <div class="section-chip-row small">
        <span class="section-chip-line"></span>
        <span class="section-chip-mark">◇</span>
        <span class="section-chip with-icon">
          <i class="fa-regular fa-user"></i>
          体质匹配
        </span>
        <span class="section-chip-mark">◇</span>
        <span class="section-chip-line"></span>
      </div>

      <div class="section-title-row lower">
        <span class="title-line"></span>
        <span class="title-mark">〰</span>
        <h2>根据体质选疗法</h2>
        <span class="title-mark">〰</span>
        <span class="title-line"></span>
      </div>
      <p class="constitution-desc">结合自身体质特点，选择最适合的外治疗法</p>
    </section>

    <section class="constitution-grid">
      <button
        v-for="item in constitutionTherapies"
        :key="item.name"
        type="button"
        class="constitution-card"
        :class="{ active: activeConstitution === item.name, linked: matchedConstitutionNames.includes(item.name) }"
        @click="recommendTherapy(item)"
      >
        <span class="constitution-emoji">{{ item.emoji }}</span>
        <strong>{{ item.name }}</strong>
        <div class="constitution-tags">
          <span v-for="name in item.therapies" :key="name">{{ name }}</span>
        </div>
      </button>
    </section>

    <transition name="detail-expand" mode="out-in">
      <section v-if="selectedTherapy && detailSection === 'constitution'" ref="constitutionDetailRef" class="detail-panel constitution-detail">
      <div class="detail-header">
        <div class="detail-title">
          <span class="detail-icon-box" :style="{ borderColor: selectedTherapy.color }">
            <i :class="selectedTherapy.icon" :style="{ color: selectedTherapy.color }"></i>
          </span>
          <div>
            <h3 :style="{ color: selectedTherapy.color }">{{ selectedTherapy.name }}</h3>
            <p>{{ selectedTherapy.desc }}</p>
          </div>
        </div>
        <button class="close-btn" @click="closeDetail">×</button>
      </div>

      <div class="detail-tabs">
        <button
          v-for="item in detailTabs"
          :key="item.key"
          type="button"
          class="detail-tab"
          :class="{ active: activeDetailTab === item.key }"
          @click="activeDetailTab = item.key"
        >
          {{ item.label }}
        </button>
      </div>

      <transition name="tab-fade" mode="out-in">
        <div class="detail-grid" :key="`constitution-${selectedTherapy.name}-${activeDetailTab}`">
        <article v-if="activeDetailTab === 'symptoms'" class="detail-card single-card">
          <h4>适应症状</h4>
          <div class="detail-tags">
            <span v-for="item in selectedTherapy.indications" :key="item">{{ item }}</span>
          </div>
        </article>

        <article v-else-if="activeDetailTab === 'procedure'" class="detail-card single-card">
          <h4>操作流程</h4>
          <ol class="detail-list">
            <li v-for="item in selectedTherapy.procedure" :key="item">{{ item }}</li>
          </ol>
        </article>

        <article v-else-if="activeDetailTab === 'cautions'" class="detail-card single-card">
          <h4>注意事项</h4>
          <ul class="detail-list">
            <li v-for="item in selectedTherapy.cautions" :key="item">{{ item }}</li>
          </ul>
        </article>

        <article v-else class="detail-card single-card">
          <h4>体质匹配</h4>
          <div class="detail-tags colorful">
            <button
              v-for="item in selectedTherapy.constitutionMatch"
              :key="item.name"
              type="button"
              class="constitution-link"
              :style="{ color: item.color, borderColor: item.color, background: `${item.color}12` }"
              @click="pickMatchedConstitution(item.name)"
            >
              {{ item.emoji }} {{ item.name }}
            </button>
          </div>
        </article>
        </div>
      </transition>

      <div class="detail-actions">
        <button type="button" class="pager-btn" @click="stepTherapy(-1)">上一项</button>
        <button type="button" class="pager-btn primary" @click="stepTherapy(1)">下一项</button>
      </div>
      </section>
    </transition>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'

const selectedTherapy = ref(null)
const activeConstitution = ref('')
const detailSection = ref('therapy')
const therapyDetailRef = ref(null)
const constitutionDetailRef = ref(null)
const activeDetailTab = ref('symptoms')

const detailTabs = [
  { key: 'symptoms', label: '适应症状' },
  { key: 'procedure', label: '操作流程' },
  { key: 'cautions', label: '注意事项' },
  { key: 'constitution', label: '体质匹配' }
]

const therapies = [
  {
    name: '刮痧疗法',
    icon: 'fa-solid fa-leaf',
    color: '#6b9b30',
    shortDesc: '通过刮拭经络穴位，排除毒素，活血化瘀',
    desc: '刮痧是中医传统的自然疗法，通过特制的刮痧器具在体表反复刮拭，使皮肤局部充血，达到活血化瘀、清热解毒的目的。',
    indications: ['感冒发热', '颈肩酸痛', '肌肉劳损', '头痛头晕', '湿热体质', '空调病'],
    procedure: ['清洁皮肤，涂抹刮痧油或刮痧乳', '选择合适的刮痧板，角度保持45°', '沿经络走向均匀用力刮拭', '每个部位刮20-30次，以出痧为度', '刮痧后饮用温开水，注意保暖'],
    cautions: ['饭后半小时内不宜刮痧', '皮肤破损、感染者禁用', '孕妇腰骶部禁用', '体质虚弱者力度宜轻', '刮痧后4小时内不宜洗澡'],
    constitutionMatch: [{ name: '痰湿质', emoji: '💧', color: '#34d399' }, { name: '湿热质', emoji: '🔥', color: '#f59e0b' }, { name: '血瘀质', emoji: '🩸', color: '#ef4444' }]
  },
  {
    name: '拔罐疗法',
    icon: 'fa-solid fa-jar',
    color: '#d39b17',
    shortDesc: '负压吸引，活血通络，祛寒除湿',
    desc: '拔罐是以罐为工具，利用燃火、抽气等方法产生负压，使之吸附于体表，造成局部瘀血，达到通经活络、行气活血、消肿止痛、祛风散寒等效果。',
    indications: ['风寒感冒', '肩背疼痛', '腰肌劳损', '风寒感冒', '肩背疼痛', '腰肌劳损'],
    procedure: ['选择合适体位，暴露拔罐部位', '使用闪火法或投火法将罐吸附', '留罐10-15分钟', '起罐时轻压罐周皮肤，使其漏气', '起罐后观察皮肤颜色变化'],
    cautions: ['凝血功能障碍者禁用', '皮肤过敏、溃疡处禁用', '孕妇腹部、腰骶部禁用', '高热抽搐者禁用', '拔罐后忌受风寒'],
    constitutionMatch: [{ name: '阳虚质', emoji: '❄', color: '#a78bfa' }, { name: '气虚质', emoji: '🫁', color: '#60a5fa' }, { name: '痰湿质', emoji: '💧', color: '#34d399' }]
  },
  {
    name: '艾灸疗法',
    icon: 'fa-solid fa-fire-flame-curved',
    color: '#d45a3d',
    shortDesc: '温通经络，驱寒除湿，保健强身',
    desc: '艾灸是用艾叶制成的艾炷或艾条，点燃后产生的艾热刺激人体穴位或特定部位，通过激发经气活动来调整人体紊乱的生理生化功能。',
    indications: ['宫寒痛经', '胃脘冷痛', '慢性疲劳', '气虚乏力', '阳虚体质', '慢性腹泻'],
    procedure: ['选择穴位，清洁皮肤', '将艾炷或艾条置于穴位上', '用温灸盒或手持艾条悬灸', '每个穴位灸15-20分钟', '灸至皮肤潮红、患者有温热感'],
    cautions: ['实热证、阴虚火旺者慎用', '面部、心脏附近慎用直接灸', '孕妇腰骶部、腹部禁用', '大血管处不宜艾灸', '灸后忌食生冷'],
    constitutionMatch: [{ name: '阳虚质', emoji: '❄', color: '#a78bfa' }, { name: '气虚质', emoji: '🫁', color: '#60a5fa' }, { name: '平和质', emoji: '☯', color: '#6b8e23' }]
  },
  {
    name: '推拿按摩',
    icon: 'fa-solid fa-hands',
    color: '#b68131',
    shortDesc: '舒筋活络，调和气血，缓解疲劳',
    desc: '推拿是中医外治法之一，通过手法作用于人体体表的特定部位或穴位，以调节机体的生理、病理状况，达到治疗和保健目的。',
    indications: ['颈肩腰腿痛', '失眠头痛', '消化不良', '颈肩腰腿痛', '失眠头痛', '消化不良'],
    procedure: ['使用滚法、揉法放松肌肉', '使用点法、按法刺激穴位', '使用拿法、捏法舒筋活络', '使用抖法、摇法活动关节', '最后用推法、擦法结束'],
    cautions: ['急性炎症、骨折处禁用', '皮肤破损、感染处禁用', '饭后1小时内不宜按摩', '按摩力度因人而异', '孕妇禁忌穴位勿按'],
    constitutionMatch: [{ name: '气郁质', emoji: '🌙', color: '#8b5cf6' }, { name: '血瘀质', emoji: '🩸', color: '#ef4444' }, { name: '平和质', emoji: '☯', color: '#6b8e23' }]
  },
  {
    name: '针刺疗法',
    icon: 'fa-solid fa-syringe',
    color: '#4d98ff',
    shortDesc: '疏通经络，调节阴阳，扶正祛邪',
    desc: '针刺是在中医理论指导下，运用针具刺入人体特定穴位，通过经络传导，调整脏腑气血功能，达到防病治病的目的。',
    indications: ['各种痛症', '神经性疾病', '消化系统疾病', '各种痛症', '神经性疾病', '消化系统疾病'],
    procedure: ['辨证取穴，确定治疗方案', '消毒针具和穴位', '快速进针，调节针感', '留针20-30分钟', '出针，按压针孔止血'],
    cautions: ['必须在专业医师指导下进行', '凝血功能障碍者禁用', '孕妇禁忌穴位禁用', '重要脏器部位慎用', '严格消毒，防止感染'],
    constitutionMatch: [{ name: '气郁质', emoji: '🌙', color: '#8b5cf6' }, { name: '血瘀质', emoji: '🩸', color: '#ef4444' }, { name: '痰湿质', emoji: '💧', color: '#34d399' }]
  },
  {
    name: '耳穴贴压',
    icon: 'fa-solid fa-ear-listen',
    color: '#f16eb1',
    shortDesc: '刺激耳穴，调节脏腑，操作简便',
    desc: '耳穴贴压是用王不留行籽、磁珠等贴压在耳廓穴位上，通过按压刺激，达到治疗目的。耳为宗脉之所聚，与脏腑经络密切联系。',
    indications: ['失眠多梦', '头痛眩晕', '近视肥胖', '失眠多梦', '头痛眩晕', '近视肥胖'],
    procedure: ['清洁耳廓，寻找敏感点', '用探棒按压找出最痛点', '消毒后将药籽贴于穴位', '每穴适度按压1-2分钟', '每天按压3-5次，3-5天更换'],
    cautions: ['耳廓皮肤破溃者禁用', '孕妇按压宜轻柔', '儿童贴压时间宜短', '如出现不适立即停用', '胶布过敏者慎用'],
    constitutionMatch: [{ name: '气郁质', emoji: '🌙', color: '#8b5cf6' }, { name: '特禀质', emoji: '✿', color: '#ec4899' }, { name: '阴虚质', emoji: '♨', color: '#ff6b6b' }]
  }
]

const constitutionTherapies = [
  { name: '气虚质', emoji: '🫁', therapies: ['艾灸', '推拿'] },
  { name: '阳虚质', emoji: '❄', therapies: ['艾灸', '拔罐'] },
  { name: '阴虚质', emoji: '♨', therapies: ['耳穴', '推拿'] },
  { name: '痰湿质', emoji: '💧', therapies: ['刮痧', '拔罐'] },
  { name: '湿热质', emoji: '🔥', therapies: ['刮痧', '拔罐'] },
  { name: '血瘀质', emoji: '🩸', therapies: ['刮痧', '针刺'] },
  { name: '气郁质', emoji: '🌙', therapies: ['推拿', '耳穴'] },
  { name: '特禀质', emoji: '✿', therapies: ['耳穴', '推拿'] },
  { name: '平和质', emoji: '☯', therapies: ['艾灸', '推拿'] }
]

const matchedConstitutionNames = computed(() => {
  if (!selectedTherapy.value) return []
  return selectedTherapy.value.constitutionMatch.map((item) => item.name)
})

function selectTherapy(item) {
  if (selectedTherapy.value?.name === item.name) {
    closeDetail()
    return
  }
  selectedTherapy.value = item
  activeConstitution.value = ''
  detailSection.value = 'therapy'
  activeDetailTab.value = 'symptoms'
  nextTick(() => {
    therapyDetailRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  })
}

function recommendTherapy(item) {
  if (activeConstitution.value === item.name) {
    closeDetail()
    return
  }
  activeConstitution.value = item.name
  const found = therapies.find((therapy) => item.therapies.some((name) => therapy.name.includes(name)))
  if (found) {
    selectedTherapy.value = found
    detailSection.value = 'constitution'
    activeDetailTab.value = 'constitution'
    nextTick(() => {
      constitutionDetailRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    })
  }
}

function pickMatchedConstitution(name) {
  const found = constitutionTherapies.find((item) => item.name === name)
  if (found) recommendTherapy(found)
}

function stepTherapy(offset) {
  if (!selectedTherapy.value) return
  const currentIndex = therapies.findIndex((item) => item.name === selectedTherapy.value.name)
  const nextIndex = (currentIndex + offset + therapies.length) % therapies.length
  selectedTherapy.value = therapies[nextIndex]
  if (detailSection.value === 'therapy') {
    activeConstitution.value = ''
  }
  activeDetailTab.value = 'symptoms'
  nextTick(() => {
    if (detailSection.value === 'constitution') {
      constitutionDetailRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    } else {
      therapyDetailRef.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  })
}

function closeDetail() {
  selectedTherapy.value = null
  activeConstitution.value = ''
  activeDetailTab.value = 'symptoms'
  detailSection.value = 'therapy'
}
</script>

<style scoped>
.therapy-page {
  position: relative;
  max-width: 1280px;
  margin: 0 auto;
  padding: 26px 18px 28px;
  min-height: calc(100vh - 60px);
}

.page-bg {
  position: absolute;
  inset: 0;
  z-index: -5;
  background:
    radial-gradient(circle at 50% 0%, rgba(212, 188, 153, 0.18), transparent 26%),
    radial-gradient(circle at 50% 40%, rgba(255, 255, 255, 0.9), transparent 32%),
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
  top: 54px;
  width: 370px;
  height: 360px;
  opacity: 0.18;
  background:
    radial-gradient(ellipse at 16% 26%, rgba(166, 171, 164, 0.46) 0 18%, transparent 19%),
    radial-gradient(ellipse at 34% 24%, rgba(180, 184, 176, 0.42) 0 21%, transparent 22%),
    radial-gradient(ellipse at 14% 70%, rgba(135, 145, 127, 0.36) 0 12%, transparent 13%),
    radial-gradient(ellipse at 32% 82%, rgba(154, 160, 150, 0.28) 0 17%, transparent 18%);
}

.bg-mountain.right {
  right: -12px;
  top: 170px;
  width: 340px;
  height: 440px;
  opacity: 0.16;
  background:
    radial-gradient(ellipse at 64% 24%, rgba(191, 191, 180, 0.45) 0 18%, transparent 19%),
    radial-gradient(ellipse at 78% 46%, rgba(164, 170, 160, 0.34) 0 15%, transparent 16%),
    radial-gradient(ellipse at 46% 86%, rgba(144, 152, 136, 0.32) 0 22%, transparent 23%);
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
  top: 406px;
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
  left: -4px;
  bottom: 0;
  width: 370px;
  height: 300px;
  opacity: 0.18;
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
}

.cloud-left {
  left: 350px;
  top: 138px;
}

.cloud-right {
  right: 282px;
  top: 126px;
}

.bg-bird {
  left: 198px;
  top: 98px;
  width: 152px;
  height: 88px;
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

.line,
.section-chip-line,
.title-line {
  width: 72px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(199, 164, 111, 0.9), transparent);
}

.curl,
.section-chip-mark,
.title-mark {
  color: #ccaa74;
  font-size: 22px;
  line-height: 1;
}

.therapy-overview {
  margin-top: 40px;
}

.section-chip-row,
.section-title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.section-chip {
  height: 36px;
  padding: 0 18px;
  border-radius: 6px;
  border: 1px solid rgba(202, 180, 144, 0.45);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(250, 247, 241, 0.84);
  color: #666255;
  font-size: 15px;
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

.therapy-grid {
  width: min(1000px, 100%);
  margin: 26px auto 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.therapy-card,
.constitution-card,
.detail-panel,
.detail-card {
  background: rgba(255, 252, 247, 0.9);
  border: 1px solid rgba(223, 212, 196, 0.88);
  box-shadow:
    0 14px 34px rgba(162, 139, 104, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.76);
}

.therapy-card {
  min-height: 214px;
  border-radius: 12px;
  padding: 24px 30px 18px;
  text-align: left;
  cursor: pointer;
  transition:
    transform 0.28s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.28s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.28s ease,
    background-color 0.28s ease;
}

.therapy-card:hover {
  transform: translateY(-4px) scale(1.01);
  background: rgba(255, 253, 248, 0.96);
  box-shadow:
    0 22px 44px rgba(162, 139, 104, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.76);
}

.therapy-card.active {
  border-color: rgba(36, 89, 76, 0.46);
  transform: translateY(-3px);
  background: linear-gradient(180deg, rgba(255, 253, 248, 0.98), rgba(250, 246, 239, 0.96));
  box-shadow:
    0 18px 42px rgba(36, 89, 76, 0.12),
    inset 0 0 0 1px rgba(36, 89, 76, 0.08);
}

.therapy-icon-box,
.detail-icon-box {
  width: 62px;
  height: 62px;
  border: 2px solid;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  background: rgba(255, 255, 255, 0.7);
}

.therapy-card strong {
  display: block;
  margin-top: 18px;
  font-family: var(--font-serif);
  font-size: 18px;
}

.therapy-card p {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 1.8;
  color: #70695d;
}

.therapy-tags {
  margin-top: 18px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.therapy-tags span {
  color: #9b9388;
  font-size: 12px;
}

.constitution-head {
  margin-top: 18px;
  text-align: center;
}

.section-chip-row.small {
  margin-top: 8px;
}

.section-chip.with-icon {
  gap: 6px;
}

.section-title-row.lower {
  margin-top: 18px;
}

.constitution-desc {
  margin: 12px 0 0;
  color: #7a7468;
  font-size: 15px;
}

.constitution-grid {
  width: min(1000px, 100%);
  margin: 22px auto 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.constitution-card {
  border-radius: 12px;
  min-height: 122px;
  padding: 18px;
  text-align: center;
  cursor: pointer;
  transition:
    transform 0.28s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.28s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.28s ease,
    background-color 0.28s ease;
}

.constitution-card:hover {
  transform: translateY(-4px) scale(1.01);
  background: rgba(255, 253, 248, 0.96);
}

.constitution-card.active {
  border-color: rgba(36, 89, 76, 0.46);
  transform: translateY(-3px);
  background: linear-gradient(180deg, rgba(255, 253, 248, 0.98), rgba(250, 246, 239, 0.96));
  box-shadow:
    0 18px 40px rgba(36, 89, 76, 0.12),
    inset 0 0 0 1px rgba(36, 89, 76, 0.08);
}

.constitution-card.linked:not(.active) {
  border-color: rgba(212, 164, 70, 0.38);
  box-shadow:
    0 12px 30px rgba(212, 164, 70, 0.08),
    inset 0 0 0 1px rgba(212, 164, 70, 0.06);
}

.constitution-emoji {
  font-size: 32px;
}

.constitution-card strong {
  display: block;
  margin-top: 8px;
  font-family: var(--font-serif);
  font-size: 18px;
  color: #24594c;
}

.constitution-tags {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.constitution-tags span {
  font-size: 12px;
  color: #847d71;
}

.detail-panel {
  width: min(1000px, 100%);
  margin: 18px auto 0;
  border-radius: 14px;
  padding: 20px;
  transform-origin: top center;
}

.inline-detail {
  margin-top: 16px;
}

.constitution-detail {
  margin: 16px auto 0;
}

.detail-tabs {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.detail-tab,
.pager-btn,
.constitution-link {
  cursor: pointer;
}

.detail-tab {
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(212, 198, 178, 0.92);
  background: rgba(250, 247, 241, 0.88);
  color: #6b6559;
  transition:
    background-color 0.24s ease,
    color 0.24s ease,
    border-color 0.24s ease,
    transform 0.24s ease;
}

.detail-tab:hover {
  transform: translateY(-1px);
}

.detail-tab.active {
  background: #24594c;
  border-color: #24594c;
  color: #fff;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.detail-title {
  display: flex;
  gap: 16px;
}

.detail-title h3 {
  margin: 0 0 8px;
  font-family: var(--font-serif);
  font-size: 28px;
}

.detail-title p {
  margin: 0;
  color: #6d665b;
  line-height: 1.8;
}

.close-btn {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid rgba(208, 194, 174, 0.9);
  background: rgba(250, 247, 241, 0.88);
  color: #6d665b;
  font-size: 22px;
  cursor: pointer;
}

.detail-grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.single-card {
  grid-column: 1 / -1;
}

.detail-card {
  border-radius: 12px;
  padding: 16px;
}

.detail-card h4 {
  margin: 0 0 12px;
  font-family: var(--font-serif);
  font-size: 18px;
  color: #24594c;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-tags span {
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(220, 210, 194, 0.95);
  background: rgba(250, 247, 241, 0.86);
  display: inline-flex;
  align-items: center;
  color: #6f685d;
  font-size: 12px;
}

.detail-tags.colorful span {
  border-color: currentColor;
}

.constitution-link {
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid currentColor;
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    filter 0.22s ease;
}

.constitution-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(130, 120, 100, 0.12);
  filter: saturate(1.05);
}

.detail-list {
  margin: 0;
  padding-left: 18px;
  color: #6d665b;
  line-height: 1.9;
}

.detail-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.pager-btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid rgba(208, 194, 174, 0.9);
  background: rgba(250, 247, 241, 0.88);
  color: #6d665b;
  transition:
    transform 0.24s ease,
    box-shadow 0.24s ease,
    background-color 0.24s ease,
    color 0.24s ease,
    border-color 0.24s ease;
}

.pager-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(130, 120, 100, 0.1);
}

.pager-btn.primary {
  background: #24594c;
  border-color: #24594c;
  color: #fff;
}

.detail-expand-enter-active,
.detail-expand-leave-active {
  transition:
    opacity 0.32s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}

.detail-expand-enter-from,
.detail-expand-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.985);
}

.tab-fade-enter-active,
.tab-fade-leave-active {
  transition:
    opacity 0.22s ease,
    transform 0.22s ease;
}

.tab-fade-enter-from,
.tab-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@media (max-width: 1080px) {
  .therapy-grid,
  .constitution-grid,
  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .therapy-page {
    padding: 20px 12px 24px;
  }

  .hero h1 {
    font-size: 40px;
  }

  .hero p,
  .constitution-desc {
    font-size: 14px;
  }

  .line,
  .section-chip-line,
  .title-line {
    width: 36px;
  }

  .section-title-row h2 {
    font-size: 30px;
  }

  .therapy-grid,
  .constitution-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-header,
  .detail-title {
    flex-direction: column;
  }

  .detail-actions {
    justify-content: stretch;
  }
}
</style>
