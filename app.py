import json
import pandas as pd
import plotly.express as px
import streamlit as st
import markdown as md

from src.database import (
    init_db, get_documents, get_document, create_document, update_document,
    delete_document, increment_views, toggle_favorite, get_versions,
    get_apis, create_api, delete_api, get_snippets, create_snippet,
    delete_snippet, search_documents, stats
)
from src.seed import seed_demo
from src.ui import inject_css, badge
from src.utils import slugify, export_json, export_markdown, safe_filename, reading_time, format_date, parse_import_json

st.set_page_config(page_title="Developer Documentation Portal", page_icon="📚", layout="wide")
inject_css()
init_db()
seed_demo()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None

with st.sidebar:
    st.markdown("## 📚 DevDocs Portal")
    st.caption("Documentation workspace")
    nav = st.radio(
        "Navigation",
        ["Dashboard", "Documentation", "API Reference", "Code Snippets", "Analytics", "Import / Export"],
        index=["Dashboard", "Documentation", "API Reference", "Code Snippets", "Analytics", "Import / Export"].index(st.session_state.page)
    )
    st.session_state.page = nav
    st.divider()
    st.markdown("### Quick actions")
    if st.button("＋ New document", use_container_width=True):
        st.session_state.page = "Documentation"
        st.session_state.selected_doc = "new"
        st.rerun()
    if st.button("↻ Refresh data", use_container_width=True):
        st.rerun()
    st.divider()
    st.caption("Local SQLite • No API keys required")

page = st.session_state.page

if page == "Dashboard":
    s = stats()
    st.markdown("""
    <div class="hero">
      <h1>Developer Documentation Portal</h1>
      <p>Build, organize, search, publish, and maintain technical documentation from one workspace.</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    metrics = [
        ("📚", "Documents", s["total"]),
        ("🚀", "Published", s["published"]),
        ("👁️", "Total views", s["views"]),
        ("🔌", "API endpoints", s["apis"]),
    ]
    for c, (icon, label, value) in zip(cols, metrics):
        c.markdown(f'<div class="metric"><div style="font-size:1.5rem">{icon}</div><div class="muted">{label}</div><h2>{value}</h2></div>', unsafe_allow_html=True)

    st.markdown("### Workspace overview")
    left, right = st.columns([1.15, .85])
    docs = get_documents()
    with left:
        if docs:
            df = pd.DataFrame([dict(x) for x in docs])
            counts = df["category"].value_counts().reset_index()
            counts.columns = ["Category", "Documents"]
            fig = px.bar(counts, x="Category", y="Documents", title="Documents by category")
            fig.update_layout(height=330, margin=dict(l=10,r=10,t=55,b=10))
            st.plotly_chart(fig, use_container_width=True)
    with right:
        status_df = pd.DataFrame({
            "Status": ["Published", "Draft", "Archived"],
            "Count": [s["published"], s["drafts"], s["archived"]]
        })
        fig = px.pie(status_df, names="Status", values="Count", hole=.55, title="Publication status")
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recently updated")
    for d in docs[:5]:
        c1, c2, c3 = st.columns([5,2,1])
        with c1:
            st.markdown(f"**{d['title']}**")
            st.caption(d["summary"][:130] if d["summary"] else "No summary")
        with c2:
            badge(d["status"])
            badge(d["difficulty"])
        with c3:
            if st.button("Open", key=f"dash_open_{d['id']}"):
                st.session_state.page = "Documentation"
                st.session_state.selected_doc = d["id"]
                st.rerun()

elif page == "Documentation":
    docs = get_documents()
    if st.session_state.selected_doc is None:
        st.session_state.selected_doc = None

    st.title("📖 Documentation")
    search_col, cat_col, status_col = st.columns([2.2,1,1])
    with search_col:
        q = st.text_input("Search documentation", placeholder="Search title, content, tags, author...")
    with cat_col:
        categories = sorted(set(d["category"] for d in docs)) or ["General"]
        category = st.selectbox("Category", ["All"] + categories)
    with status_col:
        status = st.selectbox("Status", ["All","Published","Draft","Archived"])

    filtered = search_documents(q) if q.strip() else docs
    filtered = [d for d in filtered if (category == "All" or d["category"] == category)
                and (status == "All" or d["status"] == status)]

    if st.session_state.selected_doc == "new":
        selected = None
    elif st.session_state.selected_doc:
        selected = get_document(st.session_state.selected_doc)
    else:
        selected = None

    if selected is None and st.session_state.selected_doc != "new":
        st.markdown(f"**{len(filtered)}** document(s) found")
        for d in filtered:
            with st.container(border=True):
                a,b = st.columns([6,1.2])
                with a:
                    st.markdown(f'<div class="doc-title">{d["title"]}</div>', unsafe_allow_html=True)
                    st.caption(d["summary"] or "No summary")
                    badge(d["category"]); badge(d["status"]); badge(d["difficulty"])
                    if d["tags"]:
                        st.caption("Tags: " + d["tags"])
                with b:
                    if st.button("View", key=f"view_{d['id']}", use_container_width=True):
                        st.session_state.selected_doc = d["id"]
                        increment_views(d["id"])
                        st.rerun()
        if not filtered:
            st.info("No documents match your filters.")
    else:
        if selected is None:
            st.subheader("Create documentation")
            data = {"title":"","slug":"","summary":"","content":"","category":"General","tags":"",
                    "author":"Admin","status":"Draft","difficulty":"Beginner"}
            form_id = "new"
        else:
            st.subheader("Edit documentation")
            data = dict(selected)
            form_id = str(selected["id"])

        with st.form(f"doc_form_{form_id}"):
            title = st.text_input("Title *", data["title"])
            slug = st.text_input("Slug", data["slug"] or slugify(title))
            summary = st.text_area("Short summary", data["summary"], height=80)
            c1,c2,c3 = st.columns(3)
            category = c1.text_input("Category", data["category"])
            author = c2.text_input("Author", data["author"])
            status = c3.selectbox("Status", ["Draft","Published","Archived"],
                                  index=["Draft","Published","Archived"].index(data["status"]))
            c4,c5 = st.columns(2)
            difficulty = c4.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"],
                                      index=["Beginner","Intermediate","Advanced"].index(data["difficulty"]))
            tags = c5.text_input("Tags (comma separated)", data["tags"])
            content = st.text_area("Markdown content", data["content"], height=430,
                                   placeholder="# Your documentation\n\nWrite Markdown here...")
            submitted = st.form_submit_button("Save documentation", type="primary", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Title is required.")
            elif not slugify(slug):
                st.error("Please provide a valid slug.")
            else:
                payload = dict(title=title.strip(), slug=slugify(slug), summary=summary,
                               content=content, category=category or "General", tags=tags,
                               author=author or "Admin", status=status, difficulty=difficulty)
                try:
                    if selected is None:
                        new_id = create_document(payload)
                        st.session_state.selected_doc = new_id
                    else:
                        update_document(selected["id"], payload)
                    st.success("Documentation saved successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save document: {e}")

        if selected:
            preview_tab, history_tab = st.tabs(["Preview", "Version history"])
            with preview_tab:
                st.markdown(f"**{selected['title']}** · {reading_time(selected['content'])} min read")
                st.markdown(selected["content"] or "*No content yet.*")
            with history_tab:
                versions = get_versions(selected["id"])
                if not versions:
                    st.info("No version history yet.")
                for v in versions:
                    with st.expander(f"{format_date(v['created_at'])} — {v['title']}"):
                        st.markdown(v["content"] or "*Empty version*")

            b1,b2,b3 = st.columns(3)
            if b1.button("← Back to list", use_container_width=True):
                st.session_state.selected_doc = None
                st.rerun()
            if b2.button("⭐ Toggle favorite", use_container_width=True):
                toggle_favorite(selected["id"])
                st.rerun()
            if b3.button("🗑️ Delete document", use_container_width=True):
                st.session_state[f"confirm_delete_{selected['id']}"] = True

            if st.session_state.get(f"confirm_delete_{selected['id']}", False):
                st.warning("This permanently deletes the document and its versions.")
                y,n = st.columns(2)
                if y.button("Yes, delete", type="primary"):
                    delete_document(selected["id"])
                    st.session_state.selected_doc = None
                    st.session_state[f"confirm_delete_{selected['id']}"] = False
                    st.rerun()
                if n.button("Cancel"):
                    st.session_state[f"confirm_delete_{selected['id']}"] = False
                    st.rerun()

elif page == "API Reference":
    st.title("🔌 API Reference")
    apis = get_apis()
    left, right = st.columns([1.15,.85])
    with left:
        st.subheader("Endpoint catalog")
        method_filter = st.selectbox("Filter method", ["All","GET","POST","PUT","PATCH","DELETE"])
        for api in apis:
            if method_filter != "All" and api["method"] != method_filter:
                continue
            with st.expander(f"{api['method']}  {api['path']} — {api['name']}"):
                st.caption(api["description"])
                st.markdown(f"**Authentication:** {api['auth']}")
                st.markdown("**Parameters**")
                st.code(api["parameters"] or "None")
                st.markdown("**Response**")
                st.code(api["response"] or "No response schema", language="json")
                if st.button("Delete endpoint", key=f"del_api_{api['id']}"):
                    delete_api(api["id"])
                    st.rerun()
    with right:
        st.subheader("Add endpoint")
        with st.form("api_form"):
            name = st.text_input("Endpoint name")
            method = st.selectbox("Method", ["GET","POST","PUT","PATCH","DELETE"])
            path = st.text_input("Path", "/api/v1/")
            category = st.text_input("Category", "General")
            description = st.text_area("Description")
            parameters = st.text_area("Parameters")
            response = st.text_area("Response JSON")
            auth = st.selectbox("Authentication", ["None","Bearer Token","API Key","Basic Auth","OAuth 2.0"])
            if st.form_submit_button("Add endpoint", type="primary"):
                if not name or not path:
                    st.error("Name and path are required.")
                else:
                    create_api(dict(name=name,method=method,path=path,category=category,
                                     description=description,parameters=parameters,response=response,auth=auth))
                    st.success("Endpoint added.")
                    st.rerun()

elif page == "Code Snippets":
    st.title("💻 Code Snippets")
    snippets = get_snippets()
    search = st.text_input("Search snippets", placeholder="Title, language, tags...")
    if search:
        snippets = [s for s in snippets if search.lower() in " ".join(
            [s["title"],s["language"],s["tags"],s["description"]]).lower()]
    for s in snippets:
        with st.expander(f"{s['title']} · {s['language']}"):
            st.caption(s["description"])
            st.code(s["code"], language=s["language"])
            if s["tags"]:
                st.caption("Tags: " + s["tags"])
            if st.button("Delete snippet", key=f"del_snip_{s['id']}"):
                delete_snippet(s["id"])
                st.rerun()

    st.divider()
    st.subheader("Add code snippet")
    with st.form("snippet_form"):
        c1,c2 = st.columns(2)
        title = c1.text_input("Title")
        language = c2.selectbox("Language", ["python","javascript","typescript","java","kotlin","sql","html","css","bash","json","yaml","csharp","cpp","go","php","text"])
        description = st.text_input("Description")
        tags = st.text_input("Tags")
        code = st.text_area("Code", height=220)
        if st.form_submit_button("Save snippet", type="primary"):
            if not title or not code:
                st.error("Title and code are required.")
            else:
                create_snippet(dict(title=title,language=language,code=code,description=description,tags=tags))
                st.success("Snippet saved.")
                st.rerun()

elif page == "Analytics":
    st.title("📊 Documentation Analytics")
    docs = get_documents()
    s = stats()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Documents", s["total"])
    c2.metric("Views", s["views"])
    c3.metric("Favorites", s["favorites"])
    c4.metric("Snippets", s["snippets"])

    if docs:
        df = pd.DataFrame([dict(d) for d in docs])
        left,right = st.columns(2)
        with left:
            fig = px.bar(df.sort_values("views", ascending=False).head(10), x="title", y="views", title="Top viewed documents")
            fig.update_layout(xaxis_tickangle=-35, height=390)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            diff = df["difficulty"].value_counts().reset_index()
            diff.columns = ["Difficulty","Documents"]
            fig = px.pie(diff, names="Difficulty", values="Documents", title="Difficulty distribution")
            fig.update_layout(height=390)
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Document inventory")
        view = df[["title","category","status","difficulty","views","favorite","author","updated_at"]].copy()
        view.columns = ["Title","Category","Status","Difficulty","Views","Favorite","Author","Updated"]
        st.dataframe(view, use_container_width=True, hide_index=True)

elif page == "Import / Export":
    st.title("📦 Import / Export")
    docs = get_documents()
    st.subheader("Export")
    st.write("Download your documentation collection as JSON, or export an individual document as Markdown.")
    st.download_button("Download all documents (JSON)", export_json(docs),
                       file_name="documentation_export.json", mime="application/json")
    if docs:
        chosen = st.selectbox("Document to export", [d["title"] for d in docs])
        selected = next(d for d in docs if d["title"] == chosen)
        st.download_button("Download selected Markdown", export_markdown(selected),
                           file_name=safe_filename(selected["slug"]) + ".md", mime="text/markdown")

    st.divider()
    st.subheader("Import JSON")
    st.caption("Import a JSON array containing title, slug, summary, content, category, tags, author, status, and difficulty.")
    uploaded = st.file_uploader("Choose JSON file", type=["json"])
    if uploaded:
        raw = uploaded.read().decode("utf-8")
        try:
            records = parse_import_json(raw)
            st.success(f"Loaded {len(records)} document(s).")
            st.json(records[:2])
            if st.button("Import documents", type="primary"):
                imported = 0
                for item in records:
                    if not item.get("title") or not item.get("content"):
                        continue
                    payload = {
                        "title": item["title"],
                        "slug": slugify(item.get("slug") or item["title"]),
                        "summary": item.get("summary",""),
                        "content": item.get("content",""),
                        "category": item.get("category","General"),
                        "tags": item.get("tags",""),
                        "author": item.get("author","Imported"),
                        "status": item.get("status","Draft"),
                        "difficulty": item.get("difficulty","Beginner")
                    }
                    try:
                        create_document(payload)
                        imported += 1
                    except Exception:
                        pass
                st.success(f"Imported {imported} document(s).")
                st.rerun()
        except Exception as e:
            st.error(f"Invalid JSON: {e}")
