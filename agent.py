import streamlit as st
import arxiv
import openai


openai.api_key = "sk-c3ba46d6f7564ddbb0f3a70fd8fc14ce"
openai.base_url = "https://api.deepseek.com/v1"

# 搜索论文函数
def search_papers(topic):
    search = arxiv.Search(query=topic, max_results=5)
    results = []
    for paper in search.results():
        results.append({
            "title": paper.title,
            "summary": paper.summary[:300],
            "pdf_url": paper.pdf_url
        })
    return results

# 用 DeepSeek 生成回复（类似 aisuite 的功能）
def ask_deepseek(prompt):
    response = openai.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ========== Streamlit 界面 ==========
st.title("文献查询智能体")
topic = st.text_input("输入研究主题")

if topic:
    with st.spinner("搜索中..."):
        papers = search_papers(topic)
        for p in papers:
            st.subheader(p["title"])
            st.write(p["summary"])
            st.write(f"[PDF链接]({p['pdf_url']})")
            st.divider()