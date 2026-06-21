import streamlit as st
import arxiv

st.set_page_config(page_title="文献查询智能体", layout="centered")

st.title("文献查询智能体")
st.markdown("输入关键词，搜索 arXiv 上的相关论文")


def search_papers(topic, max_results=5):
    try:
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
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


topic = st.text_input("输入关键词", placeholder="例如：machine learning")

if topic:
    with st.spinner("正在搜索..."):
        papers = search_papers(topic)

    if isinstance(papers, dict) and "error" in papers:
        st.error(f"❌ {papers['error']}")
    elif not papers:
        st.info("未找到相关论文")
    else:
        st.success(f"找到 {len(papers)} 篇论文")
        for p in papers:
            st.subheader(p["title"])
            st.write(f"**作者：** {', '.join(p['authors'][:3])}")
            st.write(f"**摘要：** {p['summary']}")
            st.markdown(f"📎 [PDF链接]({p['pdf_url']})")
            st.divider()