import aisuite as ai
import arxiv
import os


# aisuite 读取 Ollama 地址
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

# 模型名称
MODEL_NAME = "llama3.1:8b"


client = ai.Client()


# ============ 工具函数：搜索 arXiv ============
def search_arxiv(query: str, max_results: int = 5) -> str:
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for paper in search.results():
            results.append({
                "title": paper.title,
                "summary": paper.summary[:300],
                "url": paper.entry_id,
                "authors": [a.name for a in paper.authors][:3]
            })
        if not results:
            return "未找到相关论文"
        output = "找到以下论文：\n"
        for i, p in enumerate(results, 1):
            output += f"\n{i}. 标题：{p['title']}\n"
            output += f"   作者：{', '.join(p['authors'])}\n"
            output += f"   摘要：{p['summary']}...\n"
            output += f"   链接：{p['url']}\n"
        return output
    except Exception as e:
        return f"搜索出错：{str(e)}"


# ============ 智能体主函数 ============
def ask_agent(question: str) -> str:
    print("正在分析问题...")

    # 第一步：生成搜索关键词
    messages_keyword = [
        {"role": "system", "content": "根据用户问题生成 arXiv 搜索关键词，只输出英文关键词。"},
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat.completions.create(
            model=f"ollama:{MODEL_NAME}",
            messages=messages_keyword
        )
        keyword = response.choices[0].message.content.strip()
        print(f" 关键词：{keyword}")
    except Exception as e:
        return f"模型调用失败：{str(e)}\n请确保 Ollama 已启动且模型已下载"

    # 第二步：搜索
    print("正在搜索 arXiv...")
    papers_result = search_arxiv(keyword)

    if "未找到" in papers_result:
        return papers_result

    # 第三步：生成总结
    messages_summary = [
        {"role": "system", "content": "你是科研助手，根据论文列表用中文回答用户问题，引用论文标题支持观点。"},
        {"role": "user", "content": f"用户问题：{question}\n\n参考论文：\n{papers_result}\n\n请根据以上论文给出回答。"}
    ]

    print(" 正在生成回答...")
    try:
        response = client.chat.completions.create(
            model=f"ollama:{MODEL_NAME}",
            messages=messages_summary
        )
        answer = response.choices[0].message.content
    except Exception as e:
        return f"生成回答失败：{str(e)}"

    return f"{papers_result}\n\n 总结分析：\n{answer}"


# ============ 运行 ============
if __name__ == "__main__":
    print("=" * 60)
    print("📖 文献检索智能体 (aisuite + Ollama)")
    print("=" * 60)
    question = input("\n请输入你想检索的论文主题：")
    print()
    result = ask_agent(question)
    print("\n" + "=" * 60)
    print(result)
    print("=" * 60)