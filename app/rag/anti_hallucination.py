"""
============================================
防幻觉校验模块（系统可信度核心）
============================================
功能：
  1. 对AI生成内容进行中医知识准确性校验
  2. 计算生成内容与RAG检索源的语义重合度
  3. 结合知识图谱三元组做事实核查
  4. 输出置信度评分和校验报告

设计理念：
  所有Agent生成的内容都必须经过防幻觉校验，
  这是多智能体系统区别于"单模型生成"的核心壁垒。

⚠️ 基于讯飞星火 v3.5/4.0 驱动的严谨性校验
⚠️ 免责声明：校验结果仅供参考，不构成医疗建议
============================================
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger


# ============================================================
# 数据模型
# ============================================================

@dataclass
class HallucinationCheckResult:
    """
    防幻觉校验结果

    Attributes:
        passed: 是否通过校验（置信度 >= 阈值）
        confidence: 综合置信度（0-1）
        semantic_overlap: 语义重合度得分（0-1）
        graph_consistency: 图谱一致性得分（0-1）
        keyword_coverage: 关键词覆盖率（0-1）
        warnings: 警告信息列表
        rejected_claims: 被拒绝的断言列表
        verified_claims: 已验证的断言列表
        disclaimer: 免责声明
    """
    passed: bool = False
    confidence: float = 0.0
    semantic_overlap: float = 0.0
    graph_consistency: float = 0.0
    keyword_coverage: float = 0.0
    warnings: List[str] = None
    rejected_claims: List[str] = None
    verified_claims: List[str] = None
    cold_start: bool = False  # 冷启动标记：本地知识库为空或匹配极低时为True
    disclaimer: str = ""

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.rejected_claims is None:
            self.rejected_claims = []
        if self.verified_claims is None:
            self.verified_claims = []
        self.disclaimer = "⚠️ 本内容由AI生成，基于中医教材知识库检索，仅供教育学习参考，非医疗建议。如有健康问题请咨询专业中医师。"
        self.cold_start = False  # 默认非冷启动

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "confidence": round(self.confidence, 3),
            "semantic_overlap": round(self.semantic_overlap, 3),
            "graph_consistency": round(self.graph_consistency, 3),
            "keyword_coverage": round(self.keyword_coverage, 3),
            "warnings": self.warnings,
            "rejected_claims": self.rejected_claims,
            "verified_claims": self.verified_claims,
            "disclaimer": self.disclaimer,
        }


# ============================================================
# 核心函数：医学一致性校验
# ============================================================

def check_medical_consistency(
    generated_text: str,
    retrieval_sources: List[Dict[str, Any]],
    graph_service: Optional[Any] = None,
    confidence_threshold: float = 0.7,
    tcm_keywords: Optional[List[str]] = None,
) -> HallucinationCheckResult:
    """
    中医知识一致性校验（防幻觉核心函数）

    计算生成内容与RAG检索源的语义重合度得分，
    并结合知识图谱进行事实核查。

    校验流程：
      1. 关键词提取：从生成文本中提取中医术语
      2. 语义重合度：计算生成文本与检索源的关键词重叠率
      3. 图谱一致性：对关键断言进行知识图谱验证
      4. 综合评分：加权计算最终置信度
      5. 判定：置信度 >= 阈值 → PASS，否则 → WARN/REJECT

    Args:
        generated_text: AI生成的文本内容
        retrieval_sources: RAG检索源列表，每项含 {"content": "...", "similarity": 0.xx}
        graph_service: 知识图谱服务实例（TcmGraphService），可选
        confidence_threshold: 置信度阈值（默认0.7）
        tcm_keywords: 预定义的中医关键词列表（用于提升提取准确率）

    Returns:
        HallucinationCheckResult: 校验结果
    """
    result = HallucinationCheckResult()

    if not generated_text or not generated_text.strip():
        result.warnings.append("生成内容为空")
        return result

    # ---- 第1步：关键词提取 ----
    generated_keywords = _extract_tcm_keywords(generated_text, tcm_keywords)
    source_keywords = set()
    for src in retrieval_sources:
        src_kw = _extract_tcm_keywords(src.get("content", ""), tcm_keywords)
        source_keywords.update(src_kw)

    # ---- 第2步：语义重合度 ----
    semantic_overlap = _calculate_semantic_overlap(
        generated_text, retrieval_sources
    )
    result.semantic_overlap = semantic_overlap

    # ---- 第3步：关键词覆盖率 ----
    if generated_keywords and source_keywords:
        coverage = len(generated_keywords & source_keywords) / len(generated_keywords)
        result.keyword_coverage = coverage
    else:
        result.keyword_coverage = 0.0

    # ---- 第4步：图谱一致性校验（权重提升为核心判定标准）----
    graph_consistency = 0.0
    if graph_service and graph_service._loaded:
        graph_consistency, verified, rejected = _check_graph_consistency(
            generated_text, graph_service
        )
        result.graph_consistency = graph_consistency
        result.verified_claims = verified
        result.rejected_claims = rejected
    else:
        # 无图谱时，用关键词覆盖率作为图谱一致性代理
        result.graph_consistency = result.keyword_coverage

    # ---- 第3.5步：冷启动检测 ----
    # 当本地知识库为空或匹配度极低时，标记冷启动模式
    cold_start = False
    if not retrieval_sources or semantic_overlap < 0.1:
        cold_start = True
        result.cold_start = True
        result.warnings.append(
            "⚠️ 本地中医知识库匹配度极低，正在切换至讯飞星火大模型通用中医知识库"
            "进行初步回答。严谨性评分已标注，建议后续补充本地知识库数据。"
        )
        logger.warning("🧊 冷启动模式: 本地知识库为空或匹配极低，降级为星火通用知识回答")

    # ---- 第5步：综合置信度（权重优化：图谱验证为核心判定标准）----
    # 调整权重：图谱一致性50% + 语义重合度30% + 关键词覆盖率20%
    # verify_fact（图谱验证）权重提升为最高，作为防幻觉的核心判定标准
    if graph_service and graph_service._loaded and graph_consistency > 0:
        # 有图谱验证结果时：图谱权重最高
        result.confidence = (
            graph_consistency * 0.5    # 图谱验证为核心（提升权重）
            + semantic_overlap * 0.3   # 语义重合度
            + result.keyword_coverage * 0.2  # 关键词覆盖率
        )
    elif cold_start:
        # 冷启动模式：大幅降低置信度，提示用户
        result.confidence = semantic_overlap * 0.3 + result.keyword_coverage * 0.1
    else:
        # 无图谱时：语义重合度为主
        result.confidence = (
            semantic_overlap * 0.5
            + result.keyword_coverage * 0.3
            + 0.2  # 基础分（有检索源就给一定信任）
        )

    # ---- 第6步：判定 ----
    result.passed = result.confidence >= confidence_threshold

    # 生成警告
    if result.confidence < confidence_threshold:
        result.warnings.append(
            f"⚠️ 置信度({result.confidence:.2f})低于阈值({confidence_threshold})，"
            f"内容可能包含不准确信息，请对照教材核实"
        )

    if result.rejected_claims:
        result.warnings.append(
            f"🚫 以下断言未通过图谱验证: {', '.join(result.rejected_claims[:3])}"
        )

    logger.info(
        f"🛡️ 防幻觉校验 | "
        f"置信度={result.confidence:.3f} | "
        f"语义重合={result.semantic_overlap:.3f} | "
        f"图谱一致={result.graph_consistency:.3f} | "
        f"关键词覆盖={result.keyword_coverage:.3f} | "
        f"{'✅ PASS' if result.passed else '⚠️ WARN'}"
    )

    return result


# ============================================================
# 辅助函数
# ============================================================

def _extract_tcm_keywords(
    text: str,
    predefined_keywords: Optional[List[str]] = None,
) -> set:
    """
    从文本中提取中医术语关键词

    提取策略：
      1. 优先匹配预定义关键词列表
      2. 补充提取"X虚""X实""X气"等中医命名模式

    Args:
        text: 待提取文本
        predefined_keywords: 预定义关键词列表

    Returns:
        匹配到的关键词集合
    """
    keywords = set()

    # 预定义关键词匹配
    if predefined_keywords:
        for kw in predefined_keywords:
            if kw in text:
                keywords.add(kw)

    # 中医术语模式匹配
    tcm_patterns = [
        r'[阴阳][^\s，。]{0,4}(虚|实|亢|衰|亏|盛)',  # 阴虚、阳亢、阴阳两虚等
        r'[心肝脾肺肾][^\s，。]{0,4}(气|血|阴|阳)(虚|实|亏|盛)',  # 肝阴虚、心气虚等
        r'[风寒暑湿燥火][^\s，。]{0,2}(邪|气)',  # 风邪、寒气等
        r'[\u4e00-\u9fff]{2,6}汤[^\s，。]{0,4}',  # XX汤（方剂）
        r'[\u4e00-\u9fff]{2,6}丸[^\s，。]{0,4}',  # XX丸（方剂）
        r'[\u4e00-\u9fff]{2,4}经',  # XX经（经络）
        r'(藏象|气血|津液|经络|六淫|七情|八纲|卫气|营气)',  # 核心术语
    ]

    for pattern in tcm_patterns:
        matches = re.findall(pattern, text)
        keywords.update(matches)

    return keywords


def _calculate_semantic_overlap(
    generated_text: str,
    retrieval_sources: List[Dict[str, Any]],
) -> float:
    """
    计算生成内容与检索源的语义重合度得分

    方法：基于n-gram重叠率（简化版，无需额外模型）
    - 将文本分词后计算2-gram重叠率
    - 加权：与相似度高的检索源的重叠贡献更大

    后续优化：可替换为基于讯飞星火Embedding的余弦相似度

    Args:
        generated_text: 生成文本
        retrieval_sources: 检索源列表

    Returns:
        语义重合度得分（0-1）
    """
    if not retrieval_sources:
        return 0.0

    # 简单分词（中文按字/词切分）
    def to_ngrams(text: str, n: int = 2) -> set:
        """将文本转为n-gram集合"""
        chars = [c for c in text if c.strip()]
        return set(''.join(chars[i:i+n]) for i in range(len(chars) - n + 1))

    gen_ngrams = to_ngrams(generated_text)

    if not gen_ngrams:
        return 0.0

    # 加权重叠率
    total_overlap = 0.0
    total_weight = 0.0

    for src in retrieval_sources:
        src_text = src.get("content", "")
        src_similarity = src.get("similarity", src.get("score", 0.5))

        src_ngrams = to_ngrams(src_text)

        if src_ngrams:
            overlap = len(gen_ngrams & src_ngrams) / len(gen_ngrams)
        else:
            overlap = 0.0

        # 用检索相似度作为权重
        weight = max(src_similarity, 0.1)
        total_overlap += overlap * weight
        total_weight += weight

    return total_overlap / total_weight if total_weight > 0 else 0.0


def _check_graph_consistency(
    generated_text: str,
    graph_service: Any,
) -> Tuple[float, List[str], List[str]]:
    """
    知识图谱一致性校验

    从生成文本中提取可能的实体对，
    在知识图谱中验证其关系是否存在。

    Args:
        generated_text: 生成文本
        graph_service: TcmGraphService 实例

    Returns:
        (一致性得分, 已验证断言列表, 被拒绝断言列表)
    """
    verified = []
    rejected = []
    total_checks = 0

    # 从图谱中提取出现在生成文本中的实体
    entities_in_text = []
    for entity in graph_service.graph.nodes():
        if entity in generated_text and len(entity) >= 2:
            entities_in_text.append(entity)

    # 对每对实体验证关系
    checked_pairs = set()
    for i, e1 in enumerate(entities_in_text):
        for e2 in entities_in_text[i+1:]:
            if (e1, e2) in checked_pairs:
                continue
            checked_pairs.add((e1, e2))

            # 在图谱中查找关系
            relations = graph_service.get_relations_between(e1, e2)
            if relations:
                for rel in relations:
                    verified.append(f"{e1}—[{rel}]→{e2}")
                    total_checks += 1
            else:
                # 检查反向
                reverse_relations = graph_service.get_relations_between(e2, e1)
                if reverse_relations:
                    for rel in reverse_relations:
                        verified.append(f"{e2}—[{rel}]→{e1}")
                        total_checks += 1
                elif graph_service.graph.has_node(e1) and graph_service.graph.has_node(e2):
                    # 两实体都在图谱中但无直接关系——需要额外审查
                    # 不直接判为reject，但降低置信度
                    total_checks += 1

    # 计算一致性得分
    if total_checks > 0:
        consistency = len(verified) / total_checks
    elif entities_in_text:
        # 有实体出现但无明确关系可验证——中性
        consistency = 0.5
    else:
        # 生成文本中无图谱实体——无法验证
        consistency = 0.3

    return consistency, verified, rejected
