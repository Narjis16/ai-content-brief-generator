import json
import re

import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(page_title="AI Content Brief Generator", layout="centered")
st.title("📝 AI Content Brief & SEO Assistant")
st.markdown("Generate complete content briefs and SEO outlines for any topic using Groq.")

# Sidebar configuration
st.sidebar.header("Configuration")
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Groq API Key", type="password")

model = st.sidebar.selectbox("Model", ["llama-3.3-70b-versatile"], index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
keyword_count = st.sidebar.slider("SEO keyword count", 3, 10, 5)
tone_of_voice = st.sidebar.selectbox(
    "Tone of voice",
    ["professional", "friendly", "conversational", "authoritative", "creative"],
    index=0,
)

st.sidebar.markdown("Use the sidebar to configure model settings and prompt behavior.")

if not api_key:
    st.warning("⚠️ Please configure your GROQ_API_KEY in Streamlit Secrets, or enter it in the sidebar to begin.")
    st.stop()

client = Groq(api_key=api_key)

# Helper functions

def extract_json(text: str) -> str:
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json_match.group(0)

    raise ValueError("Unable to extract JSON from the model response.")


def validate_content_brief(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Response JSON must be an object.")

    required_fields = ["target_audience", "seo_keywords", "blog_outline", "tone_of_voice"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data["target_audience"], list) or not all(isinstance(item, str) for item in data["target_audience"]):
        raise ValueError("target_audience must be a list of strings.")

    if not isinstance(data["seo_keywords"], list) or not all(isinstance(item, str) for item in data["seo_keywords"]):
        raise ValueError("seo_keywords must be a list of strings.")

    blog_outline = data["blog_outline"]
    if not isinstance(blog_outline, dict):
        raise ValueError("blog_outline must be an object.")
    if "h1_title" not in blog_outline or "sections" not in blog_outline:
        raise ValueError("blog_outline must contain h1_title and sections.")
    if not isinstance(blog_outline["h1_title"], str):
        raise ValueError("blog_outline.h1_title must be a string.")
    if not isinstance(blog_outline["sections"], list) or not all(isinstance(item, str) for item in blog_outline["sections"]):
        raise ValueError("blog_outline.sections must be a list of strings.")

    if not isinstance(data["tone_of_voice"], str):
        raise ValueError("tone_of_voice must be a string.")

    return data


def format_list(items: list[str]) -> str:
    return ", ".join(items) if items else "—"

# App inputs
topic = st.text_input("Topic", placeholder="e.g., sustainable gardening, remote work tools")

if st.button("Generate Content Brief"):
    if not topic.strip():
        st.warning("Please enter a valid topic.")
    else:
        with st.spinner("AI is generating your content brief..."):
            prompt = f"""Create a content brief for the topic: \"{topic}\".
Return ONLY valid JSON with the exact structure below and no surrounding markdown or explanation:
{{
  "target_audience": ["persona1", "persona2", "persona3"],
  "seo_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
  "blog_outline": {{
    "h1_title": "Main title",
    "sections": ["Section1", "Section2", "Section3"]
  }},
  "tone_of_voice": "professional"
}}
Produce {keyword_count} SEO keywords and use a {tone_of_voice} voice.
"""

            raw_response = ""
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                )
                raw_response = response.choices[0].message.content
                cleaned = extract_json(raw_response)
                data = json.loads(cleaned)
                validated = validate_content_brief(data)

                st.success("✅ Content brief generated successfully")

                st.subheader("🎯 Target Audience")
                for persona in validated["target_audience"]:
                    st.write(f"- {persona}")

                st.subheader("🔑 SEO Keywords")
                st.write(format_list(validated["seo_keywords"]))

                st.subheader("📚 Blog Outline")
                st.write(f"**H1:** {validated['blog_outline']['h1_title']}")
                for index, section in enumerate(validated["blog_outline"]["sections"], start=1):
                    st.write(f"{index}. {section}")

                st.subheader("🎭 Tone of Voice")
                st.write(validated["tone_of_voice"])

                with st.expander("View raw AI response"):
                    st.code(raw_response)
            except json.JSONDecodeError:
                st.error("Unable to parse the AI response as JSON.")
                if raw_response:
                    with st.expander("Raw AI response"):
                        st.code(raw_response)
            except Exception as error:
                st.error(f"Error: {error}")
                if raw_response:
                    with st.expander("Raw AI response"):
                        st.code(raw_response)
