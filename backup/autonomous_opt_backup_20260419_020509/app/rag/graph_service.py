"""
============================================
中医知识图谱检索服务
============================================
功能：
  1. 加载中医知识图谱三元组（CSV/JSON格式）
  2. 基于 networkx 构建图谱索引
  3. 提供实体关系查询接口（邻居查询、路径查询、子图提取）
  4. 对接 TCM_knowledge_graph 和 OpenTCM 项目的三元组逻辑

知识图谱三元组示例：
  (肝, 属于, 阴脏)
  (六味地黄丸, 包含, 熟地黄)
  (肾阳虚, 治疗, 金匮肾气丸)
  (阴阳学说, 属于, 中医哲学基础)

⚠️ 免责声明：知识图谱内容仅供教育学习参考，非医疗建议。
============================================
"""

import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

from app.core.logger import logger, log_rag_verification

import networkx as nx
from loguru import logger


# ============================================================
# 知识图谱三元组数据模型
# ============================================================

class TcmTriple:
    """
    中医知识图谱三元组

    Attributes:
        head: 头实体（如"肝"）
        relation: 关系（如"属于"）
        tail: 尾实体（如"阴脏"）
        source: 来源（如"中医基础理论教材"）
        confidence: 置信度（0-1，来自图谱构建时的评分）
    """
    def __init__(
        self,
        head: str,
        relation: str,
        tail: str,
        source: str = "",
        confidence: float = 1.0,
    ):
        self.head = head
        self.relation = relation
        self.tail = tail
        self.source = source
        self.confidence = confidence

    def to_dict(self) -> dict:
        return {
            "head": self.head,
            "relation": self.relation,
            "tail": self.tail,
            "source": self.source,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TcmTriple":
        return cls(
            head=d.get("head", ""),
            relation=d.get("relation", ""),
            tail=d.get("tail", ""),
            source=d.get("source", ""),
            confidence=d.get("confidence", 1.0),
        )


# ============================================================
# 核心类：中医知识图谱服务
# ============================================================

class TcmGraphService:
    """
    中医知识图谱检索服务

    基于 networkx 构建内存图谱索引，
    提供实体查询、关系查询、路径发现等能力。

    参考项目：
      - TCM_knowledge_graph: 中医知识图谱构建
      - OpenTCM: 开放中医知识库

    使用示例：
        >>> service = TcmGraphService()
        >>> service.load_from_json("./data/knowledge_base/知识图谱/triples.json")
        >>> # 查询"肝"的所有关系
        >>> neighbors = service.get_neighbors("肝")
        >>> # 查询"肾阳虚"到"金匮肾气丸"的路径
        >>> path = service.find_path("肾阳虚", "金匮肾气丸")
    """

    def __init__(self):
        """初始化空图谱"""
        self.graph = nx.DiGraph()  # 有向图（A→关系→B）
        self._entity_index: Dict[str, Set[str]] = {}  # 实体→节点ID索引
        self._relation_types: Set[str] = set()  # 所有关系类型
        self._loaded = False

    # ============================================================
    # 图谱加载
    # ============================================================

    def load_from_json(self, file_path: str) -> int:
        """
        从JSON文件加载三元组

        JSON格式支持两种：
          1. 列表格式: [{"head": "...", "relation": "...", "tail": "..."}, ...]
          2. 嵌套格式: {"triples": [...]}

        Args:
            file_path: JSON文件路径

        Returns:
            加载的三元组数量
        """
        if not os.path.exists(file_path):
            logger.error(f"图谱文件不存在: {file_path}")
            return 0

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 兼容两种格式
        if isinstance(data, list):
            triples_data = data
        elif isinstance(data, dict):
            triples_data = data.get("triples", data.get("data", []))
        else:
            logger.error(f"不支持的JSON格式: {file_path}")
            return 0

        count = 0
        for item in triples_data:
            triple = TcmTriple.from_dict(item)
            self._add_triple(triple)
            count += 1

        self._loaded = True
        logger.info(f"✅ 知识图谱加载完成: {count}条三元组, {self.graph.number_of_nodes()}个实体, {len(self._relation_types)}种关系")
        return count

    def load_from_csv(self, file_path: str, delimiter: str = ",") -> int:
        """
        从CSV文件加载三元组

        CSV格式：head,relation,tail[,source[,confidence]]

        Args:
            file_path: CSV文件路径
            delimiter: 分隔符

        Returns:
            加载的三元组数量
        """
        if not os.path.exists(file_path):
            logger.error(f"图谱文件不存在: {file_path}")
            return 0

        count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            # 跳过可能的表头
            first_line = f.readline()
            if first_line.strip().lower().startswith("head"):
                pass  # 有表头，已跳过
            else:
                f.seek(0)  # 无表头，重置

            for line in f:
                parts = line.strip().split(delimiter)
                if len(parts) >= 3:
                    triple = TcmTriple(
                        head=parts[0].strip(),
                        relation=parts[1].strip(),
                        tail=parts[2].strip(),
                        source=parts[3].strip() if len(parts) > 3 else "",
                        confidence=float(parts[4]) if len(parts) > 4 else 1.0,
                    )
                    self._add_triple(triple)
                    count += 1

        self._loaded = True
        logger.info(f"✅ 知识图谱CSV加载完成: {count}条三元组")
        return count

    def load_from_directory(self, dir_path: str) -> int:
        """批量加载目录下所有图谱文件"""
        total = 0
        for fname in os.listdir(dir_path):
            fpath = os.path.join(dir_path, fname)
            if fname.endswith(".json"):
                total += self.load_from_json(fpath)
            elif fname.endswith(".csv"):
                total += self.load_from_csv(fpath)
        return total

    def _add_triple(self, triple: TcmTriple) -> None:
        """向图谱中添加一条三元组"""
        self.graph.add_edge(
            triple.head,
            triple.tail,
            relation=triple.relation,
            source=triple.source,
            confidence=triple.confidence,
        )

        # 更新索引
        for entity in [triple.head, triple.tail]:
            if entity not in self._entity_index:
                self._entity_index[entity] = set()
            self._entity_index[entity].add(triple.head)
            self._entity_index[entity].add(triple.tail)

        self._relation_types.add(triple.relation)

    # ============================================================
    # 图谱查询接口
    # ============================================================

    def get_neighbors(self, entity: str, relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        查询实体的邻居节点

        Args:
            entity: 中心实体名（如"肝"）
            relation: 可选，按关系类型过滤

        Returns:
            邻居列表，每项包含 {"entity": "...", "relation": "...", "direction": "out/in"}
        """
        if entity not in self.graph:
            return []

        neighbors = []

        # 出边（entity → ?）
        for _, tail, data in self.graph.out_edges(entity, data=True):
            if relation and data.get("relation") != relation:
                continue
            neighbors.append({
                "entity": tail,
                "relation": data["relation"],
                "direction": "out",
                "confidence": data.get("confidence", 1.0),
            })

        # 入边（? → entity）
        for head, _, data in self.graph.in_edges(entity, data=True):
            if relation and data.get("relation") != relation:
                continue
            neighbors.append({
                "entity": head,
                "relation": data["relation"],
                "direction": "in",
                "confidence": data.get("confidence", 1.0),
            })

        return neighbors

    def get_relations_between(self, head: str, tail: str) -> List[str]:
        """
        查询两个实体之间的关系

        Args:
            head: 头实体
            tail: 尾实体

        Returns:
            关系列表（可能有多条边）
        """
        if not self.graph.has_edge(head, tail):
            return []

        # 可能有平行边（NetworkX用key区分）
        if isinstance(self.graph, nx.MultiDiGraph):
            return [data["relation"] for data in self.graph[head][tail].values()]
        else:
            return [self.graph[head][tail].get("relation", "")]

    def find_path(self, source: str, target: str, max_hops: int = 3) -> List[List[Dict[str, Any]]]:
        """
        查找两个实体之间的路径（最多 max_hops 跳）

        用于发现实体间的间接关联，如：
          "肾阳虚" → 治疗 → "金匮肾气丸" → 包含 → "熟地黄"

        Args:
            source: 起始实体
            target: 目标实体
            max_hops: 最大跳数

        Returns:
            路径列表，每条路径是 [{head, relation, tail}, ...] 的三元组序列
        """
        if source not in self.graph or target not in self.graph:
            return []

        try:
            # 使用networkx的简单路径查找
            simple_paths = nx.all_simple_paths(
                self.graph, source, target, cutoff=max_hops
            )
        except nx.NetworkXError:
            return []

        paths = []
        for path_nodes in simple_paths:
            # 将节点路径转换为三元组路径
            triple_path = []
            for i in range(len(path_nodes) - 1):
                h, t = path_nodes[i], path_nodes[i + 1]
                data = self.graph[h][t]
                triple_path.append({
                    "head": h,
                    "relation": data.get("relation", ""),
                    "tail": t,
                    "confidence": data.get("confidence", 1.0),
                })
            paths.append(triple_path)

            # 限制返回路径数
            if len(paths) >= 5:
                break

        return paths

    def get_subgraph(self, entity: str, depth: int = 2) -> Dict[str, Any]:
        """
        提取以某实体为中心的子图

        Args:
            entity: 中心实体
            depth: 扩展深度

        Returns:
            子图信息，包含节点和边
        """
        if entity not in self.graph:
            return {"nodes": [], "edges": []}

        # BFS扩展
        visited_nodes = {entity}
        current_level = {entity}

        for _ in range(depth):
            next_level = set()
            for node in current_level:
                for neighbor in self.graph.successors(node):
                    if neighbor not in visited_nodes:
                        next_level.add(neighbor)
                for neighbor in self.graph.predecessors(node):
                    if neighbor not in visited_nodes:
                        next_level.add(neighbor)
            visited_nodes.update(next_level)
            current_level = next_level

        # 提取子图
        subgraph = self.graph.subgraph(visited_nodes)

        nodes = [{"id": n, "label": n} for n in subgraph.nodes()]
        edges = [
            {
                "source": h,
                "target": t,
                "relation": data.get("relation", ""),
                "confidence": data.get("confidence", 1.0),
            }
            for h, t, data in subgraph.edges(data=True)
        ]

        return {"nodes": nodes, "edges": edges}

    def verify_fact(self, head: str, relation: str, tail: str) -> Dict[str, Any]:
        """
        验证一个事实是否在知识图谱中

        这是防幻觉的关键接口：CritiqueAgent 用它验证生成内容的准确性。

        验证策略：
          1. 精确匹配：head→relation→tail 完全一致
          2. 反向验证：tail→relation(反向)→head
          3. 路径验证：head 到 tail 之间是否存在短路径

        Args:
            head: 头实体
            relation: 关系
            tail: 尾实体

        Returns:
            {"found": bool, "match_type": "exact/reverse/path", "confidence": float, "evidence": [...]}
        """
        result = {
            "found": False,
            "match_type": "none",
            "confidence": 0.0,
            "evidence": [],
        }

        # ---- 记录校验开始 ----
        _entity_label = f"{head}[{relation}]{tail}"
        _edges_count = self.graph.number_of_edges()
        logger.debug(f"🔍 RAG图谱校验开始 | 实体: {_entity_label} | 图谱总边数: {_edges_count}")

        # 1. 精确匹配
        if self.graph.has_edge(head, tail):
            edge_data = self.graph[head][tail]
            if edge_data.get("relation") == relation:
                result["found"] = True
                result["match_type"] = "exact"
                result["confidence"] = edge_data.get("confidence", 1.0)
                result["evidence"] = [{"head": head, "relation": relation, "tail": tail}]
                
                # RAG 诊断埋点：精确匹配
                log_rag_verification(
                    entity=_entity_label,
                    match_type="exact",
                    confidence=result["confidence"],
                    paths=None,
                    graph_edges_checked=_edges_count,
                )
                return result

        # 2. 反向验证（如"肝属于阴脏" → "阴脏包含肝"）
        if self.graph.has_edge(tail, head):
            edge_data = self.graph[tail][head]
            result["found"] = True
            result["match_type"] = "reverse"
            result["confidence"] = edge_data.get("confidence", 0.8) * 0.8  # 反向置信度打折
            result["evidence"] = [{"head": tail, "relation": edge_data.get("relation", ""), "tail": head}]
            
            # RAG 诊断埋点：反向匹配
            log_rag_verification(
                entity=_entity_label,
                match_type="reverse",
                confidence=result["confidence"],
                paths=result["evidence"],
                graph_edges_checked=_edges_count,
            )
            return result

        # 3. 路径验证（间接关联）
        paths = self.find_path(head, tail, max_hops=2)
        if paths:
            # 取最短路径
            shortest = min(paths, key=len)
            result["found"] = True
            result["match_type"] = "path"
            result["confidence"] = 0.5 / len(shortest)  # 路径越长置信度越低
            result["evidence"] = shortest
            
            # RAG 诊断埋点：路径匹配
            log_rag_verification(
                entity=_entity_label,
                match_type="path",
                confidence=result["confidence"],
                paths=shortest,
                graph_edges_checked=_edges_count,
            )
        else:
            # RAG 诊断埋点：无匹配
            logger.debug(f"❌ RAG图谱校验 | 实体: {_entity_label} | match=none | 图谱中无此关系")

        return result

    @property
    def stats(self) -> Dict[str, Any]:
        """图谱统计信息"""
        return {
            "loaded": self._loaded,
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "relation_types": list(self._relation_types),
        }
