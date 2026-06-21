import streamlit as st
import arxiv
from openai import OpenAI

# ============ 配置 DeepSeek ============
client = OpenAI(
    api_key="sk-38b12613fcaf4638858acc590dcd5986",  # 去 platform.deepseek.com 注册获取
    base_url="https://api.deepseek.com/v1"
)

st.set_page_config(page_title="文献查询智能体", layout="centered")
st.title("文献查询智能体")
st.markdown("输入研究主题，AI 自动搜索 arXiv 并总结分析")


def search_arxiv(topic, max_results=5):
    try:
        search = arxiv.Search(query=topic, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        results = []
        for paper in list(search.results()):
            results.append({
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "summary": paper.summary[:400] + "..." if len(paper.summary) > 400 else paper.summary,
                "pdf_url": paper.pdf_url,
                "published": paper.published.strftime("%Y-%m-%d")
            })
        return results
    except Exception as e:
        return {"error": str(e)}


def ask_deepseek(prompt):
    """调用 DeepSeek API"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 调用失败：{str(e)}"


topic = st.text_input("输入研究主题", placeholder="例如：machine learning, transformer")

if topic:
    with st.spinner("🔍 AI 正在生成搜索关键词..."):
        keyword = ask_deepseek(f"根据用户问题生成 arXiv 搜索关键词，只输出英文关键词。用户问题：{topic}")
        if keyword.startswith("AI 调用失败"):
            st.error(keyword)
            st.stop()
        st.info(f"生成的关键词：{keyword}")

    with st.spinner("📚 正在搜索 arXiv..."):
        papers = search_arxiv(keyword)

    if isinstance(papers, dict) and "error" in papers:
        st.error(f"❌ {papers['error']}")
    elif not papers:
        st.info("未找到相关论文")
    else:
        st.success(f"✅ 找到 {len(papers)} 篇论文")
        for p in papers:
            with st.expander(f"📄 {p['title']}"):
                st.write(f"**作者：** {', '.join(p['authors'][:3])}")
                st.write(f"**发布时间：** {p['published']}")
                st.write(f"**摘要：** {p['summary']}")
                st.markdown(f"📎 [PDF链接]({p['pdf_url']})")

        st.divider()
        with st.spinner("✍️ AI 正在生成总结..."):
            summary = ask_deepseek(f"用户问题：{topic}\n\n参考论文摘要：\n" + "\n".join(
                [p["summary"] for p in papers]) + "\n\n请根据以上论文用中文回答用户问题。")
        st.subheader("📝 AI 总结")
        st.write(summary)