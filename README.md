# Developer Documentation Portal

A strong, portfolio-ready documentation management portal built with **Python, Streamlit, SQLite, Markdown, Pandas, Plotly, and Pygments**.

## Features

- Dashboard with documentation KPIs
- Create, edit, delete, and duplicate documents
- Markdown editor with live preview
- Full-text search across title, summary, content, tags, and author
- Category and tag filtering
- API reference management
- Code snippet library with syntax highlighting
- Favorites/bookmarks
- Recently updated documents
- Version history for documents
- Document status: Draft / Published / Archived
- Difficulty levels: Beginner / Intermediate / Advanced
- Export selected documents as Markdown or JSON
- Import JSON documentation collections
- SQLite persistence
- Seed demo documentation
- Responsive sidebar navigation
- Charts and analytics
- No external API keys required

## Run

### Windows

```bash
cd "Developer Documentation Portal"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS/Linux

```bash
cd "Developer Documentation Portal"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit, normally:

`http://localhost:8501`

## Project Structure

```text
Developer Documentation Portal/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── database.py
│   ├── seed.py
│   ├── ui.py
│   └── utils.py
├── data/
│   └── docs.db
└── docs/
```

## Default behavior

The database is created automatically on first launch. Demo content is seeded automatically when the database is empty.

No login or external services are required.
