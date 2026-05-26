#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强启动脚本：
- 支持通过环境变量 REBUILD_VECTOR=true 强制重建向量库
- 若向量库为空则自动构建索引
- 交互模式：逐行输入问题，得到回答
- 支持命令行一次性查询：--query "问题"
"""

import os
import sys
import glob
import argparse
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()

# 导入自定义 RAG 系统
from financial_assistant import MinerURAGSystem, RAGQASystem


def ensure_vector_store(rag_system, rebuild=False):
    """
    检查向量库是否为空，或者根据 rebuild 标志决定是否重建。
    重建时重新处理 my_pdfs 下的所有 PDF，并填充向量库。
    """
    collection = rag_system.collection
    if rebuild:
        print("⚠️  强制重建向量库 (REBUILD_VECTOR=true)")
    else:
        if collection.count() > 0:
            print(f"✅ 向量库已有 {collection.count()} 个文档块，直接使用。")
            return
        else:
            print("📭 向量库为空，开始构建索引...")

    # ---------- 1. 处理 PDF 生成中间 JSON ----------
    pdf_dir = "my_pdfs"
    processed_dir = "processed"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"❌ 请将 PDF 文件放入挂载卷目录 '{pdf_dir}' 后重新运行容器。")
        sys.exit(1)

    # 检查是否已有解析好的 JSON 文件，如果没有则调用 MinerU 解析
    json_files = glob.glob(os.path.join(processed_dir, "**", "*_content_list.json"), recursive=True)
    if not json_files or rebuild:
        print("📄 开始解析 PDF 文件 (MinerU)...")
        json_files = rag_system.process_documents(pdf_directory=pdf_dir, output_dir=processed_dir)
        if not json_files:
            print("⚠️  未生成任何解析结果，请检查 PDF 文件或 MinerU 配置。")
            return
        print(f"✅ 解析完成，得到 {len(json_files)} 个 JSON 文件。")
    else:
        print(f"✅ 发现已有解析文件 {len(json_files)} 个，跳过解析步骤。")

    # ---------- 2. 分块与向量化 ----------
    print("✂️  开始文本分块...")
    documents, metadatas, ids = rag_system.chunk_and_embed(content_files=json_files)
    print(f"📦 共生成 {len(documents)} 个文档块。")

    if documents:
        print("💾 构建向量数据库...")
        rag_system.build_vector_store(documents, metadatas, ids)
        print("🎉 向量库构建完成！")
    else:
        print("⚠️  没有有效文本块，向量库为空。")


def interactive_loop(qa_system):
    """交互式问答循环"""
    print("\n" + "=" * 60)
    print("财务报告智能问答助手已启动 (输入 exit 或 quit 退出)")
    print("=" * 60)
    while True:
        try:
            question = input("\n💬 请输入问题: ").strip()
            if question.lower() in ["exit", "quit", "q"]:
                print("👋 再见！")
                break
            if not question:
                continue
            answer, _ = qa_system.ask_question(question)
            print("\n🤖 回答:")
            print(answer)
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


def main():
    parser = argparse.ArgumentParser(description="金融文档 RAG 问答系统")
    parser.add_argument("--query", type=str, help="直接提问，不进入交互模式")
    args = parser.parse_args()

    rebuild = os.getenv("REBUILD_VECTOR", "false").lower() in ["true", "1", "yes"]

    # 初始化 RAG 系统（底层使用 Chroma 持久化）
    rag_system = MinerURAGSystem(persist_directory="./my_chroma_db")

    # 确保向量库准备就绪
    ensure_vector_store(rag_system, rebuild=rebuild)

    # 初始化问答系统
    qa_system = RAGQASystem(mineru_rag_system=rag_system)

    if args.query:
        # 单次查询模式
        print(f"\n🔍 问题: {args.query}")
        answer, _ = qa_system.ask_question(args.query)
        print(f"\n📝 回答:\n{answer}")
    else:
        # 交互模式
        interactive_loop(qa_system)


if __name__ == "__main__":
    main()