import streamlit as st
import arxiv
import requests

# ============ 配置 ============
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


# ============ 调用 Ollama ============
def ask_ollama(prompt, system_prompt=None):
    """调用 Ollama API"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "")
        else:
            return f"错误：{response.status_code}"
    except Exception as e:
        return f"Ollama 调用失败：{str(e)}"


# ============ 工具函数：搜索 arXiv ============
def search_arxiv(query: str, max_results: int = 5):
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for paper in search.get_results():  # get_results() 替代 results()
            results.append({
                "title": paper.title,
                "summary": paper.summary[:400],
                "url": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "authors": [a.name for a in paper.authors][:3],
                "published": paper.published.strftime("%Y-%m-%d")
            })
        return results
    except Exception as e:
        return {"error": str(e)}


# ============ 智能体主函数 ============
def ask_agent(question: str):
    # 第一步：生成搜索关键词
    keyword_prompt = f"根据用户问题生成 arXiv 搜索关键词，只输出英文关键词，不要其他内容。\n用户问题：{question}"
    keyword = ask_ollama(keyword_prompt)
    if "错误" in keyword or "失败" in keyword:
        return None, keyword

    # 第二步：搜索
    papers = search_arxiv(keyword)
    if isinstance(papers, dict) and "error" in papers:
        return None, f"搜索出错：{papers['error']}"
    if not papers:
        return None, "未找到相关论文"

    # 第三步：生成总结
    papers_text = ""
    for i, p in enumerate(papers, 1):
        papers_text += f"\n{i}. 标题：{p['title']}\n   作者：{', '.join(p['authors'])}\n   摘要：{p['summary']}...\n"

    summary_prompt = f"""用户问题：{question}

参考论文：
{papers_text}

请根据以上论文用中文回答用户问题，引用论文标题支持你的观点。"""

    answer = ask_ollama(summary_prompt, system_prompt="你是科研助手，帮助用户整理和分析学术论文。")

    return papers, answer


# ============ Streamlit 界面 ============
st.set_page_config(page_title="文献查询智能体", layout="centered")

st.title("文献查询智能体")
st.markdown("输入研究主题，Agent 自动搜索 arXiv 并总结分析")

# 检查 Ollama 是否可用
ollama_ok = True


topic = st.text_input("输入研究主题", placeholder="例如：machine learning, transformer")

if topic and ollama_ok:
    with st.spinner("Agent 正在思考并搜索..."):
        papers, result = ask_agent(topic)

    if papers is None:
        st.error(f"❌ {result}")
    else:
        # 显示结果
        st.success(f"找到 {len(papers)} 篇论文")

        # 显示论文列表
        for p in papers:
            with st.expander(f"{p['title']}"):
                st.write(f"**作者：** {', '.join(p['authors'])}")
                st.write(f"**发布时间：** {p['published']}")
                st.write(f"**摘要：** {p['summary']}...")
                st.markdown(f"📎 [PDF链接]({p['pdf_url']})")

        st.divider()
        st.subheader("Agent 总结分析")
        st.write(result)