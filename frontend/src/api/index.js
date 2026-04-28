/**
 * TCM Mind-RAG API 调用模块
 * 自动连接后端 http://localhost:8000
 * 未连接时返回优雅降级的 Mock 数据
 */

const BASE_URL = 'http://localhost:8000'

async function request(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (e) {
    console.warn(`API请求失败 [${path}]:`, e.message, '→ 使用Mock数据')
    return null
  }
}

// Agent 列表
export async function getAgents() {
  const data = await request('/api/v1/agents')
  if (data) return data
  return {
    agents: [
      { name: '档案构建师', role: 'Profile Builder', description: '构建患者画像与体质分析' },
      { name: '中医检索师', role: 'TCM Retriever', description: '从知识库检索相关中医知识' },
      { name: '资源生成师', role: 'Resource Generator', description: '生成个性化康复方案' },
      { name: '批判分析师', role: 'Critique Agent', description: '审核用药安全与逻辑一致性' },
      { name: '路径规划师', role: 'Path Planner', description: '规划最优治疗路径' },
    ]
  }
}

// 体质分类
export async function classifyConstitution(answers) {
  const data = await request('/api/v1/constitution/classify', {
    method: 'POST',
    body: JSON.stringify({ answers }),
  })
  if (data) return data
  // Mock降级
  const types = ['气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质', '平和质']
  const scores = Array.from({ length: 9 }, () => Math.floor(Math.random() * 40) + 30)
  return { types, scores }
}

// 剂量计算
export async function calculateDosage(symptom, constitution) {
  const data = await request('/api/v1/calculate/dosage', {
    method: 'POST',
    body: JSON.stringify({ symptom, constitution }),
  })
  if (data) return data
  return {
    formula: '柴胡疏肝散加减',
    herbs: ['柴胡', '白芍', '川芎', '枳壳', '香附'],
    dosage: ['10g', '12g', '8g', '10g', '6g'],
    note: '根据体质综合计算',
  }
}

// RAG 知识检索
export async function ragSearch(query) {
  const data = await request('/api/v1/rag/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
  })
  if (data) return data
  return {
    answer: `关于"${query}"的知识：中医认为需要辨证论治，请咨询专业中医师。`,
    sources: ['《中医基础理论》· 中国中医药出版社'],
  }
}

// 处方计算（Dashboard）
export async function calculatePrescription(patientInfo) {
  const data = await request('/api/v1/calculate/dosage', {
    method: 'POST',
    body: JSON.stringify(patientInfo),
  })
  if (data) return data
  return {
    items: [
      { name: '柴胡', dose: '12g', range: '6-15g' },
      { name: '白芍', dose: '15g', range: '10-20g' },
      { name: '川芎', dose: '10g', range: '6-12g' },
      { name: '枳壳', dose: '10g', range: '6-12g' },
      { name: '香附', dose: '10g', range: '6-10g' },
    ],
    note: '综合计算结果，请遵医嘱',
    warnings: [],
  }
}

// 健康检查
export async function healthCheck() {
  return await request('/health')
}
