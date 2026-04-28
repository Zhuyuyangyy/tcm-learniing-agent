"""
============================================
中医知识库初始化脚本
============================================
功能：
  1. 自动扫描 data/knowledge_base/ 下所有子文件夹
  2. 自动过滤非Markdown文件（仅处理 .md / .markdown）
  3. 加载知识图谱三元组（.json / .csv）
  4. 语义切分 → 向量化 → 持久化到 ChromaDB
  5. 输出初始化统计报告

使用方式：
  python scripts/init_knowledge_base.py

⚠️ 免责声明：所有加载内容仅供教育学习参考，非医疗建议。
============================================
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目根目录到sys.path，确保能导入app模块
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def scan_markdown_files(base_dir: str) -> list:
    """
    递归扫描目录下所有Markdown文件

    自动过滤非Markdown文件，仅处理 .md 和 .markdown 扩展名。
    同时忽略以 . 或 _ 开头的隐藏文件和临时文件。

    Args:
        base_dir: 扫描的根目录路径

    Returns:
        找到的Markdown文件路径列表
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"❌ 目录不存在: {base_dir}")
        return []

    md_files = []
    skipped_files = []

    for f in sorted(base_path.rglob("*")):
        # 跳过目录
        if f.is_dir():
            continue

        # 跳过隐藏文件和临时文件（以 . 或 _ 或 ~ 开头）
        if f.name.startswith((".", "_", "~")):
            skipped_files.append((str(f), "隐藏/临时文件"))
            continue

        # 仅处理Markdown文件
        if f.suffix.lower() in (".md", ".markdown"):
            md_files.append(str(f))
        else:
            # 记录跳过的非Markdown文件
            skipped_files.append((str(f), f"非Markdown文件({f.suffix})"))

    print(f"📂 扫描目录: {base_dir}")
    print(f"  ✅ 找到 {len(md_files)} 个Markdown文件")
    print(f"  ⏭️ 跳过 {len(skipped_files)} 个非Markdown文件")

    # 打印跳过的文件详情（前10个）
    if skipped_files:
        for fpath, reason in skipped_files[:10]:
            rel = os.path.relpath(fpath, base_dir)
            print(f"    ⏭️ {rel} — {reason}")
        if len(skipped_files) > 10:
            print(f"    ... 还有 {len(skipped_files) - 10} 个文件被跳过")

    return md_files


def scan_graph_files(base_dir: str) -> dict:
    """
    扫描知识图谱文件（JSON/CSV）

    Args:
        base_dir: 知识图谱目录路径

    Returns:
        {"json": [...], "csv": [...]} 文件路径列表
    """
    graph_dir = Path(base_dir)

    if not graph_dir.exists():
        print(f"⚠️ 知识图谱目录不存在: {base_dir}")
        return {"json": [], "csv": []}

    json_files = [str(f) for f in graph_dir.rglob("*.json") if not f.name.startswith(".")]
    csv_files = [str(f) for f in graph_dir.rglob("*.csv") if not f.name.startswith(".")]

    print(f"📊 知识图谱文件: {len(json_files)} JSON + {len(csv_files)} CSV")

    return {"json": json_files, "csv": csv_files}


def init_vector_store(md_files: list) -> dict:
    """
    初始化向量数据库

    将Markdown文件加载 → 语义切分 → 向量化 → 存入ChromaDB

    Args:
        md_files: Markdown文件路径列表

    Returns:
        初始化统计信息
    """
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")

    from app.rag.doc_loader import TcmDocLoader
    from app.rag.vectorstore import TcmVectorStore

    stats = {
        "files_processed": 0,
        "total_chunks": 0,
        "errors": [],
    }

    # 加载文档并切分
    config_path = str(PROJECT_ROOT / "config.yaml")
    loader = TcmDocLoader(config_path=config_path)

    all_chunks = []
    for md_file in md_files:
        try:
            chunks = loader.load_file(md_file)
            all_chunks.extend(chunks)
            stats["files_processed"] += 1
            rel_path = os.path.relpath(md_file, PROJECT_ROOT)
            print(f"  📄 {rel_path} → {len(chunks)} 个分块")
        except Exception as e:
            stats["errors"].append(f"{md_file}: {e}")
            print(f"  ❌ 加载失败: {md_file} — {e}")

    stats["total_chunks"] = len(all_chunks)
    print(f"\n📚 总计: {stats['files_processed']} 个文件, {stats['total_chunks']} 个知识分块")

    # 向量化并存储
    if all_chunks:
        print(f"\n🔄 正在向量化并存入ChromaDB...")
        store = TcmVectorStore(
            persist_dir=os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "vector_db")),
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "tcm_knowledge"),
            embedding_app_id=os.getenv("SPARK_EMBEDDING_APP_ID", ""),
            embedding_api_key=os.getenv("SPARK_EMBEDDING_API_KEY", ""),
            embedding_api_secret=os.getenv("SPARK_EMBEDDING_API_SECRET", ""),
        )

        # 批量添加
        store.add_documents(all_chunks)

        # 打印统计
        store_stats = store.get_collection_stats()
        print(f"✅ 向量库初始化完成: {store_stats}")
    else:
        print("⚠️ 没有可向量化的分块，跳过向量库初始化")

    return stats


def init_graph_store(graph_files: dict) -> dict:
    """
    初始化知识图谱

    Args:
        graph_files: {"json": [...], "csv": [...]}

    Returns:
        初始化统计信息
    """
    from app.rag.graph_service import TcmGraphService

    stats = {"triples_loaded": 0, "errors": []}

    service = TcmGraphService()

    # 加载JSON文件
    for jf in graph_files.get("json", []):
        try:
            count = service.load_from_json(jf)
            stats["triples_loaded"] += count
            print(f"  📊 {os.path.basename(jf)} → {count} 条三元组")
        except Exception as e:
            stats["errors"].append(f"{jf}: {e}")
            print(f"  ❌ 加载失败: {jf} — {e}")

    # 加载CSV文件
    for cf in graph_files.get("csv", []):
        try:
            count = service.load_from_csv(cf)
            stats["triples_loaded"] += count
            print(f"  📊 {os.path.basename(cf)} → {count} 条三元组")
        except Exception as e:
            stats["errors"].append(f"{cf}: {e}")
            print(f"  ❌ 加载失败: {cf} — {e}")

    # 打印图谱统计
    graph_stats = service.stats
    print(f"\n✅ 知识图谱初始化完成:")
    print(f"  节点数: {graph_stats['node_count']}")
    print(f"  边数: {graph_stats['edge_count']}")
    print(f"  关系类型: {graph_stats['relation_types'][:10]}...")

    return stats


def main():
    """主函数：一键初始化中医知识库"""
    print("=" * 60)
    print("🏥 中医知识库初始化脚本")
    print("   tcm-ai-learning-agent")
    print("=" * 60)

    start_time = time.time()

    # 定义路径
    kb_dir = str(PROJECT_ROOT / "data" / "knowledge_base")
    graph_dir = os.getenv("TCM_GRAPH_PATH", str(PROJECT_ROOT / "data" / "knowledge_base" / "知识图谱"))

    # ---- Step1: 扫描Markdown文件 ----
    print(f"\n📖 Step1: 扫描中医教材文件...")
    md_files = scan_markdown_files(kb_dir)

    # ---- Step2: 扫描知识图谱文件 ----
    print(f"\n📊 Step2: 扫描知识图谱文件...")
    graph_files = scan_graph_files(graph_dir)

    # ---- Step3: 初始化向量数据库 ----
    if md_files:
        print(f"\n🔄 Step3: 初始化向量数据库...")
        vector_stats = init_vector_store(md_files)
    else:
        print(f"\n⚠️ 没有找到Markdown文件，跳过向量库初始化")
        print(f"   请将中医教材Markdown文件放入: {kb_dir}")
        vector_stats = {"files_processed": 0, "total_chunks": 0, "errors": []}

    # ---- Step4: 初始化知识图谱 ----
    if graph_files.get("json") or graph_files.get("csv"):
        print(f"\n🔄 Step4: 初始化知识图谱...")
        graph_stats = init_graph_store(graph_files)
    else:
        print(f"\n⚠️ 没有找到知识图谱文件，跳过图谱初始化")
        print(f"   请将三元组文件放入: {graph_dir}")
        graph_stats = {"triples_loaded": 0, "errors": []}

    # ---- 汇总报告 ----
    elapsed = time.time() - start_time

    print(f"\n{'=' * 60}")
    print(f"📋 初始化完成报告")
    print(f"{'=' * 60}")
    print(f"  ⏱️ 耗时: {elapsed:.1f}秒")
    print(f"  📄 Markdown文件: {vector_stats.get('files_processed', 0)} 个")
    print(f"  📚 知识分块: {vector_stats.get('total_chunks', 0)} 个")
    print(f"  🔗 知识图谱三元组: {graph_stats.get('triples_loaded', 0)} 条")
    print(f"  ❌ 错误: {len(vector_stats.get('errors', [])) + len(graph_stats.get('errors', []))} 个")

    if vector_stats.get('errors') or graph_stats.get('errors'):
        print(f"\n  错误详情:")
        for e in vector_stats.get('errors', []) + graph_stats.get('errors', []):
            print(f"    ❌ {e}")

    print(f"\n⚠️ 免责声明：所有加载内容仅供教育学习参考，非医疗建议。")
    print(f"🎉 初始化脚本执行完毕！")


if __name__ == "__main__":
    main()
