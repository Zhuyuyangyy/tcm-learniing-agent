<template>
  <div class="ink-bg" :class="`ink-${currentRoute}`">
    <!-- 各页面独立水墨动画 -->
    <div class="ink-layer ink-layer-1"></div>
    <div class="ink-layer ink-layer-2"></div>
    <div class="ink-layer ink-layer-3"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => route.path.replace('/', '') || 'home')
</script>

<style scoped>
/* ===== 基础层 ===== */
.ink-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
}

.ink-layer {
  position: absolute;
  inset: 0;
  opacity: var(--ink-opacity, 0.1);
}

/* ===== 1. 首页 - 远山云雾 ===== */
.ink-home .ink-layer-1 {
  background:
    radial-gradient(ellipse 120% 60% at 50% 100%, rgba(180,160,140,0.12) 0%, transparent 70%),
    radial-gradient(ellipse 80% 40% at 20% 90%, rgba(160,145,130,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 90% 35% at 80% 85%, rgba(170,155,140,0.06) 0%, transparent 55%);
  animation: mountainFloat 20s ease-in-out infinite;
}

.ink-home .ink-layer-2 {
  background:
    radial-gradient(ellipse 60% 30% at 30% 88%, rgba(140,130,120,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 70% 25% at 70% 90%, rgba(145,135,125,0.05) 0%, transparent 50%);
  animation: mountainFloat2 25s ease-in-out infinite;
}

.ink-home .ink-layer-3 {
  background: radial-gradient(ellipse 100% 50% at 50% 95%, rgba(200,190,175,0.04) 0%, transparent 65%);
  animation: mistDrift 18s ease-in-out infinite;
}

/* ===== 2. 辨证论治 - 笔墨书卷 ===== */
.ink-chat .ink-layer-1 {
  background:
    radial-gradient(ellipse 70% 50% at 15% 50%, rgba(100,90,80,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 85% 30%, rgba(95,88,80,0.04) 0%, transparent 50%);
  animation: scrollFloat 22s ease-in-out infinite;
}

.ink-chat .ink-layer-2 {
  background:
    radial-gradient(ellipse 40% 60% at 50% 80%, rgba(110,98,88,0.05) 0%, transparent 55%),
    linear-gradient(160deg, transparent 40%, rgba(130,118,108,0.03) 50%, transparent 60%);
  animation: scrollFloat2 28s ease-in-out infinite;
}

.ink-chat .ink-layer-3 {
  background:
    radial-gradient(ellipse 30% 20% at 25% 35%, rgba(120,108,98,0.04) 0%, transparent 50%),
    radial-gradient(ellipse 20% 30% at 75% 65%, rgba(115,105,95,0.03) 0%, transparent 45%);
  animation: brushFade 30s ease-in-out infinite;
}

/* ===== 3. 体质测评 - 竹影清墨 ===== */
.ink-quiz .ink-layer-1 {
  background:
    repeating-linear-gradient(88deg, transparent 0px, transparent 80px, rgba(100,110,90,0.025) 80px, rgba(100,110,90,0.025) 82px),
    repeating-linear-gradient(92deg, transparent 0px, transparent 120px, rgba(95,105,85,0.018) 120px, rgba(95,105,85,0.018) 122px);
  animation: bambooSway 18s ease-in-out infinite;
}

.ink-quiz .ink-layer-2 {
  background:
    radial-gradient(ellipse 50% 30% at 20% 40%, rgba(90,100,80,0.05) 0%, transparent 55%),
    radial-gradient(ellipse 40% 50% at 80% 60%, rgba(85,95,75,0.04) 0%, transparent 50%);
  animation: bambooSway2 24s ease-in-out infinite;
}

.ink-quiz .ink-layer-3 {
  background: radial-gradient(ellipse 80% 40% at 50% 20%, rgba(110,118,100,0.03) 0%, transparent 60%);
  animation: mistFloat 20s ease-in-out infinite;
}

/* ===== 4. 知识库 - 烟雨山水 ===== */
.ink-kb .ink-layer-1 {
  background:
    radial-gradient(ellipse 90% 50% at 50% 80%, rgba(140,150,165,0.1) 0%, transparent 65%),
    radial-gradient(ellipse 60% 30% at 20% 70%, rgba(135,145,160,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 50% 35% at 80% 75%, rgba(130,142,158,0.06) 0%, transparent 50%);
  animation: rainDrift 25s ease-in-out infinite;
}

.ink-kb .ink-layer-2 {
  background:
    radial-gradient(ellipse 40% 25% at 35% 60%, rgba(150,158,170,0.06) 0%, transparent 50%),
    radial-gradient(ellipse 55% 20% at 65% 65%, rgba(145,155,168,0.05) 0%, transparent 45%);
  animation: rainDrift2 32s ease-in-out infinite;
}

.ink-kb .ink-layer-3 {
  background:
    radial-gradient(ellipse 100% 40% at 50% 90%, rgba(160,168,178,0.04) 0%, transparent 60%),
    radial-gradient(ellipse 70% 30% at 50% 95%, rgba(155,165,175,0.03) 0%, transparent 50%);
  animation: mistFloat 22s ease-in-out infinite;
}

/* ===== 5. 外治疗法 - 藤蔓淡墨 ===== */
.ink-therapy .ink-layer-1 {
  background:
    radial-gradient(ellipse 60% 80% at 10% 50%, rgba(100,95,88,0.05) 0%, transparent 60%),
    radial-gradient(ellipse 40% 60% at 90% 40%, rgba(95,90,84,0.04) 0%, transparent 50%);
  animation: vineFloat 26s ease-in-out infinite;
}

.ink-therapy .ink-layer-2 {
  background:
    radial-gradient(ellipse 50% 40% at 30% 70%, rgba(105,98,90,0.04) 0%, transparent 50%),
    radial-gradient(ellipse 35% 50% at 70% 30%, rgba(100,95,88,0.03) 0%, transparent 45%);
  animation: vineFloat2 30s ease-in-out infinite;
}

.ink-therapy .ink-layer-3 {
  background: radial-gradient(ellipse 80% 50% at 50% 50%, rgba(115,108,100,0.03) 0%, transparent 55%);
  animation: mistFloat 24s ease-in-out infinite;
}

/* ===== 6. 学习看板 - 印章闲墨 ===== */
.ink-dashboard .ink-layer-1 {
  background:
    radial-gradient(ellipse 20% 20% at 15% 25%, rgba(160,80,60,0.05) 0%, transparent 60%),
    radial-gradient(ellipse 15% 15% at 85% 75%, rgba(155,75,55,0.04) 0%, transparent 55%),
    radial-gradient(ellipse 18% 18% at 75% 20%, rgba(158,78,58,0.03) 0%, transparent 50%);
  animation: stampFloat 28s ease-in-out infinite;
}

.ink-dashboard .ink-layer-2 {
  background:
    radial-gradient(ellipse 30% 30% at 25% 80%, rgba(100,90,82,0.04) 0%, transparent 50%),
    radial-gradient(ellipse 25% 25% at 60% 40%, rgba(98,88,80,0.03) 0%, transparent 45%);
  animation: inkFloat 22s ease-in-out infinite;
}

.ink-dashboard .ink-layer-3 {
  background: radial-gradient(ellipse 60% 40% at 50% 50%, rgba(110,100,92,0.02) 0%, transparent 55%);
  animation: mistFloat 26s ease-in-out infinite;
}

/* ===== 动画关键帧 ===== */
@keyframes mountainFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: var(--ink-opacity, 0.1); }
  50% { transform: translateY(-8px) scale(1.01); opacity: calc(var(--ink-opacity, 0.1) * 0.8); }
}

@keyframes mountainFloat2 {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-5px) scale(1.005); }
}

@keyframes mistDrift {
  0%, 100% { transform: translateX(0) translateY(0); opacity: var(--ink-opacity, 0.1); }
  33% { transform: translateX(12px) translateY(-4px); opacity: calc(var(--ink-opacity, 0.1) * 0.7); }
  66% { transform: translateX(-8px) translateY(-6px); opacity: calc(var(--ink-opacity, 0.1) * 0.85); }
}

@keyframes scrollFloat {
  0%, 100% { transform: translateY(0) scaleX(1); opacity: var(--ink-opacity, 0.1); }
  50% { transform: translateY(-6px) scaleX(1.02); opacity: calc(var(--ink-opacity, 0.1) * 0.75); }
}

@keyframes scrollFloat2 {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(10px); }
}

@keyframes brushFade {
  0%, 100% { opacity: var(--ink-opacity, 0.1); }
  50% { opacity: calc(var(--ink-opacity, 0.1) * 0.6); }
}

@keyframes bambooSway {
  0%, 100% { transform: translateX(0) skewX(0deg); opacity: var(--ink-opacity, 0.1); }
  25% { transform: translateX(4px) skewX(0.3deg); }
  75% { transform: translateX(-3px) skewX(-0.2deg); }
}

@keyframes bambooSway2 {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4px) scale(1.01); }
}

@keyframes rainDrift {
  0%, 100% { transform: translateX(0) translateY(0); opacity: var(--ink-opacity, 0.1); }
  40% { transform: translateX(15px) translateY(-5px); opacity: calc(var(--ink-opacity, 0.1) * 0.7); }
  70% { transform: translateX(-10px) translateY(-3px); opacity: calc(var(--ink-opacity, 0.1) * 0.85); }
}

@keyframes rainDrift2 {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(-8px); }
}

@keyframes vineFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: var(--ink-opacity, 0.1); }
  33% { transform: translateY(-5px) rotate(0.5deg); opacity: calc(var(--ink-opacity, 0.1) * 0.75); }
  66% { transform: translateY(-8px) rotate(-0.3deg); opacity: calc(var(--ink-opacity, 0.1) * 0.9); }
}

@keyframes vineFloat2 {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(6px); }
}

@keyframes stampFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: var(--ink-opacity, 0.1); }
  50% { transform: translateY(-4px) scale(1.02); opacity: calc(var(--ink-opacity, 0.1) * 0.8); }
}

@keyframes inkFloat {
  0%, 100% { transform: translateY(0) translateX(0); }
  33% { transform: translateY(-3px) translateX(4px); }
  66% { transform: translateY(-5px) translateX(-3px); }
}

@keyframes mistFloat {
  0%, 100% { transform: translateX(0) translateY(0); opacity: var(--ink-opacity, 0.1); }
  50% { transform: translateX(8px) translateY(-5px); opacity: calc(var(--ink-opacity, 0.1) * 0.65); }
}
</style>
