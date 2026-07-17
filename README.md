# 📝 AI Content Brief Generator

Generate content briefs, target audience personas, SEO keyword lists, and blog outlines using Groq's Llama models.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

## Setup

1. Install `uv` if you don't already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Sync the dependencies:

```bash
uv sync
```

3. Run the app:

```bash
uv run streamlit run streamlit_app.py
```

## Configuration

- Add your `GROQ_API_KEY` to Streamlit Secrets, or enter it in the sidebar when running the app.
- The app uses `llama-3.3-70b-versatile` by default to generate JSON content briefs.
