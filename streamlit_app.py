import streamlit as st
from groq import Groq
import json
import re

# 1. Page Configuration
st.set_page_config(page_title="AI Content Brief Generator", layout="centered")
st.title("📝 AI Content Brief & SEO Assistant")
st.markdown("Generate a complete content brief for any topic using Llama 3 on Groq.")

# 2. Get API key from Streamlit Secrets
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_API_KEY = st.sidebar.text_input("Enter your Groq API Key:", type="password")

# Initialize client only if we have a key
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    st.warning("⚠️ Please configure your GROQ_API_KEY in the app's Secrets settings, or enter it in the sidebar to begin.")
    st.stop()

# Helper function to parse JSON response safely
def extract_json(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
    return text

topic = st.text_input("Enter your topic:", placeholder="e.g., sustainable gardening, remote work tools")

if st.button("Generate Content Brief"):
    if topic:
        with st.spinner("AI is working..."):
            prompt = f"""For topic: "{topic}"
Return ONLY valid JSON. No explanations. No markdown. Use this exact structure:
{{
    "target_audience": ["persona1", "persona2", "persona3"],
    "seo_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
    "blog_outline": {{
        "h1_title": "Main title",
        "sections": ["Section1", "Section2", "Section3"]
    }},
    "tone_of_voice": "professional"
}}"""
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                raw = response.choices[0].message.content
                cleaned = extract_json(raw)
                data = json.loads(cleaned)

                st.subheader("🎯 Target Audience")
                for p in data["target_audience"]:
                    st.write(f"- {p}")
                
                st.subheader("🔑 SEO Keywords")
                st.write(", ".join(data["seo_keywords"]))
                
                st.subheader("📚 Blog Outline")
                st.write(f"**H1:** {data['blog_outline']['h1_title']}")
                for i, sec in enumerate(data['blog_outline']['sections'], 1):
                    st.write(f"{i}. {sec}")
                
                st.subheader("🎭 Tone of Voice")
                st.write(data["tone_of_voice"])
            except Exception as e:
                st.error(f"Error: {e}")
                st.code(raw if 'raw' in locals() else "No response")
    else:
        st.warning("AI_Brief_content_generator.")