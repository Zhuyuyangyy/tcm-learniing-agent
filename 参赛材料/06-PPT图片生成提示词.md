# PPT图片生成提示词
## 中医智能诊疗系统 TCM Mind-RAG | 互联网+大赛省级赛

> 版本：v1.0 | 2026年4月
> 用途：用AI绘图工具（DALL-E / Midjourney / Stable Diffusion）生成PPT配图

---

## 一、封面背景图

**用途**：第1页封面背景

**DALL-E 3 提示词**：
```
A futuristic dark blue tech background with subtle Chinese medicine elements, featuring abstract circuit board patterns intertwined with traditional Chinese meridian pathways, glowing cyan (#00d4aa) and gold (#ffd700) accent lines, subtle silhouette of ancient Chinese medicine herbs in the background, clean minimal aesthetic, high tech medical theme, 16:9 aspect ratio, no text, digital art style
```

**Midjourney 提示词**：
```
futuristic dark blue tech background, Chinese medicine elements, abstract circuit board with meridian pathways, glowing cyan and gold accent lines, minimal, clean aesthetic --ar 16:9 --v 6 --style raw
```

**风格**：深蓝黑背景 + 青色/金色光效 + 隐约的中医经络元素

---

## 二、知识图谱示意图

**用途**：展示中医脏腑经络关系的可视化图

**DALL-E 3 提示词**：
```
An elegant knowledge graph visualization showing Traditional Chinese Medicine organ relationships, nodes representing heart liver spleen lung kidney in circular layout with glowing connections, nodes styled as traditional Chinese seal stamps, cyan (#00d4aa) glow effect on edges, dark navy background (#0f1d35), medical data visualization style, clean scientific aesthetic, no text labels, digital art
```

**Midjourney 提示词**：
```
TCM knowledge graph visualization, five organ nodes in circular layout, glowing connections between nodes, Chinese medicine theme, dark navy background, cyan glow effect, scientific data visualization --ar 16:9 --v 6
```

**替代方案**：直接用项目系统的知识图谱截图，标注热点击

---

## 三、5 Agent流程图

**用途**：展示CrewAI多智能体协作流程

**draw.io 绘制建议**：
```
形状：圆形节点，5个
颜色：深靛蓝背景 (#1a2744) + 青色边框 (#00d4aa)
文字：白色，字体 Arial

布局：水平排列，用箭头连接
[档案构建师] → [中医检索师 + 资源生成师] → [批判分析师] → [路径规划师]
   (并行)
```

**DALL-E 3 提示词**：
```
A futuristic multi-agent collaboration diagram, five circular nodes arranged horizontally with glowing cyan (#00d4aa) borders on dark navy (#0f1d35) background, connected by flowing data streams, each node contains an abstract human icon, particle effects between nodes suggesting data flow, minimalist tech style, no text, digital art, 16:9 aspect ratio
```

---

## 四、用药安全审核UI图

**用途**：展示十八反十九畏审核功能

**DALL-E 3 提示词**：
```
A clean UI mockup of Traditional Chinese Medicine prescription safety review interface, showing herbal medicine icons with red warning triangles indicating drug interactions, dark theme (#0f1d35), green checkmarks for safe combinations, red alerts for contraindications (十八反十九畏), medical software aesthetic, minimal design, 16:9 aspect ratio, digital art
```

**替代方案**：截图项目系统的用药审核界面

---

## 五、技术架构图

**用途**：展示系统三层架构

**draw.io 绘制建议**：
```
三层架构，从上到下：
┌─────────────────────────────┐
│       用户界面 Vue3          │  ← 青色文字
└────────────┬────────────────┘
┌────────────▼────────────────┐
│   FastAPI + CrewAI 调度层     │  ← 青色文字
└────────────┬────────────────┘
┌────────────▼────────────────┐
│ 讯飞星火  │  Dify  │ ChromaDB│  ← 金色文字
└─────────────────────────────┘

背景：深蓝黑 (#0f1d35)
边框：青色 (#00d4aa)
文字：白色
```

**DALL-E 3 提示词**：
```
A clean system architecture diagram with three horizontal layers on dark navy background, glowing cyan (#00d4aa) borders around each layer, abstract server and cloud icons, data flow arrows between layers, technical blueprint style, no text labels, minimal futuristic aesthetic, digital art, 16:9
```

---

## 六、团队Logo

**用途**：第1页封面和第8页结尾

**DALL-E 3 提示词**：
```
A professional team logo for a Traditional Chinese Medicine AI project, featuring a stylized brain outline with integrated Chinese medicine elements (meridian lines, herbal leaf), combines ancient TCM philosophy with modern AI technology, color scheme: deep blue (#0f1d35) and cyan (#00d4aa), minimalist modern design, white background, square format, digital art
```

**Midjourney 提示词**：
```
TCM AI team logo, brain with meridian lines, modern minimalist, cyan and dark blue, professional medical tech logo --ar 1:1 --v 6
```

**Canva替代方案**：
1. 打开 Canva.com
2. 搜索 "logo" 模板
3. 选择医疗/科技风格
4. 添加文字：[团队名称]
5. 下载PNG

---

## 七、体质测评雷达图

**用途**：展示九种体质分类结果

**ECharts配置建议**（截图项目系统）：
```javascript
radarIndicator: [
  { name: '平和质', max: 100 },
  { name: '气虚质', max: 100 },
  { name: '阳虚质', max: 100 },
  { name: '阴虚质', max: 100 },
  { name: '痰湿质', max: 100 },
  { name: '湿热质', max: 100 },
  { name: '血瘀质', max: 100 },
  { name: '气郁质', max: 100 },
  { name: '特禀质', max: 100 }
]
```

**替代方案**：直接截图项目系统的体质雷达图报告页

---

## 八、痛点数据可视化

**用途**：第2页痛点，1:5000缺口数据展示

**DALL-E 3 提示词**：
```
A dramatic data visualization showing 1:5000 doctor-patient ratio, a single tiny doctor figure on the left compared to a massive crowd of 5000 patients on the right, red and white color scheme suggesting medical theme and urgency, dark background (#0f1d35), minimalist infographic style, no text, digital art, 16:9 aspect ratio
```

**Midjourney 提示词**```
massive contrast infographic, one doctor vs thousands of patients, dramatic visual ratio 1:5000, medical theme, dark navy background, red accents, minimalist data visualization --ar 16:9 --v 6
```

---

## 九、国风辅助图标

**用途**：点缀页面，体现中医文化特色

**图标风格**：
- 阴阳图标 ☯️
- 经络穴位图
- 针灸铜人剪影
- 中草药插画
- 脉诊意象

**来源**：
- 阿里巴巴矢量图标库：iconfont.cn
- 中国风素材：站酷、UI中国
- Google图片搜索："中医图标 PNG透明"

---

## 十、配色参考图

**完整配色方案**：

```
主背景：#0f1d35  (深蓝黑)
次背景：#1a2744  (深靛蓝)
主强调：#00d4aa  (青色)
辅助强调：#ffd700 (金色)
警示色：#ef4444  (红色)
文字主：#ffffff  (白色)
文字次：#94a3b8  (浅灰蓝)
```

**Pantone色卡参考**：
- 青色参考：Pantone 3262 C
- 金色参考：Pantone 109 C
- 深蓝参考：Pantone 533 C

---

## 十一、AI绘图工具使用建议

### DALL-E 3（推荐）
- 平台：ChatGPT Plus / Bing Image Creator（免费）
- 优点：生成质量高，对提示词理解好
- 缺点：需要订阅或排队

### Midjourney
- 平台：discord.gg/midjourney
- 优点：艺术感强，风格多样
- 缺点：需要Discord账号

### Stable Diffusion
- 平台：本地部署或线上（如Leonardo.ai）
- 优点：免费，可本地运行
- 缺点：需要一定的提示词技巧

### 通用技巧
1. **英文提示词效果更好**
2. **添加 "no text, digital art" 避免文字**
3. **指定比例 "16:9" 适配PPT**
4. **生成后用PowerPoint或Figma去除背景**

---

## 十二、图片处理工具

| 工具 | 用途 | 网址 |
|------|------|------|
| remove.bg | 去除背景 | remove.bg |
| TinyPNG | 压缩图片 | tinypng.com |
| Figma | 在线编辑 | figma.com |
| Canva | 图文设计 | canva.com |
| draw.io | 架构图绘制 | draw.io |

---

**文档信息**
- 版本：v1.0
- 更新日期：2026年4月
- 注意：所有提示词均为英文，中文说明仅供理解
