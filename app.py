import streamlit as st
import os
import subprocess
import json
import streamlit.components.v1 as components
from pathlib import Path

st.title("📚 Citation Reference Processor")

st.header("Select or Upload Article")

articles_dir = "articles"
os.makedirs(articles_dir, exist_ok=True)

# List existing article files
existing_files = [f for f in os.listdir(articles_dir) if f.endswith(".txt")]

# Dropdown to select existing file
selected_file = st.selectbox("Select existing article file:", ["-- Choose an article --"] + existing_files)

# File uploader for new file
uploaded_file = st.file_uploader("Or upload a new article text file", type=["txt"])

article_path = None
article_base = None

if uploaded_file is not None:
    # Use uploaded file and save it
    filename = uploaded_file.name
    article_base = filename.replace(".txt", "")
    article_path = os.path.join(articles_dir, filename)
    with open(article_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success(f"Uploaded and saved {filename}")

elif selected_file and selected_file != "-- Choose an article --":
    # Use selected existing file
    article_path = os.path.join(articles_dir, selected_file)
    article_base = selected_file.replace(".txt", "")
    st.info(f"Using existing article: {selected_file}")

else:
    st.warning("Please upload a new article or select an existing one.")

# Only proceed if we have an article_path (either uploaded or selected)
if article_path is not None:

    # Initialize session state flags if not present
    if "keywords_extracted" not in st.session_state:
        st.session_state.keywords_extracted = False
    if "references_fetched" not in st.session_state:
        st.session_state.references_fetched = False
    if "citations_formatted" not in st.session_state:
        st.session_state.citations_formatted = False


    # Extract Keywords button callback
    def extract_keywords():
        output_path = f"keywords/{article_base}_keywords.json"
        os.makedirs("keywords", exist_ok=True)
        subprocess.run([
            "python", "scripts/extract_keywords.py",
            article_path, output_path
        ])
        st.session_state.keywords_extracted = True

    if st.button("Extract Keywords", on_click=extract_keywords):
        st.success("✅ Keywords extracted.")

    # Show keywords if extracted
    if st.session_state.keywords_extracted:
        output_path = f"keywords/{article_base}_keywords.json"
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                keywords = json.load(f)
            st.markdown("**📌 Extracted Keywords:**")
            st.write(keywords)
        else:
            st.warning("Keyword file not found.")

    # --- Select keyword extraction method ---
    keyword_options = ["rake", "yake", "bert_score"]
    selected_keyword_group = st.selectbox("Select keyword group for reference search:", keyword_options)

    # Fetch References button callback
    def fetch_references():
        os.makedirs("references_raw", exist_ok=True)
        sources = ["openalex", "semanticscholar", "crossref"]

        for source in sources:
            ref_path = f"references_raw/{article_base}_references_{source}_{selected_keyword_group}.json"
            subprocess.run([
                "python", "scripts/fetch_references.py",
                f"keywords/{article_base}_keywords.json",
                ref_path,
                source,
                selected_keyword_group
            ])
        
        st.session_state.references_fetched = True
        st.session_state.diagram_rendered = True


    if st.button("Fetch References", on_click=fetch_references):
        st.success("✅ References fetched.")

        # Generate and display diagrams immediately after fetching
        for source in ["openalex", "semanticscholar", "crossref"]:
            ref_path = f"references_raw/{article_base}_references_{source}_{selected_keyword_group}.json"
            diagram_path = f"diagrams/{article_base}_{source}_{selected_keyword_group}_plotly.html"
            os.makedirs("diagrams", exist_ok=True)

            if os.path.exists(ref_path):
                subprocess.run([
                    "python", "scripts/generate_diagram.py",
                    ref_path,
                    diagram_path
                ])
            else:
                st.warning(f"References for {source.title()} not found, cannot generate diagram.")
    
        # Persist and show diagrams if already rendered
    if st.session_state.get("diagram_rendered", False):
        st.markdown("## 📊 Citation Diagrams")
        for source in ["openalex", "semanticscholar", "crossref"]:
            diagram_path = f"diagrams/{article_base}_{source}_{selected_keyword_group}_plotly.html"
            if os.path.exists(diagram_path):
                st.markdown(f"### {source.title()} Citation Diagram")
                with open(diagram_path, "r", encoding="utf-8") as f:
                    html_data = f.read()
                components.html(html_data, height=600, scrolling=True)
            else:
                st.warning(f"Diagram for {source.title()} not found.")

    # Format Citations button callback
    def format_citations():
        os.makedirs("citations_formatted", exist_ok=True)
        engines = ["openalex", "semanticscholar", "crossref"]
        for engine in engines:
            subprocess.run([
                "python", "scripts/format_citations.py",
                f"references_raw/{article_base}_references_{engine}_{selected_keyword_group}.json",
                f"citations_formatted/{article_base}_{engine}_{selected_keyword_group}"
            ])
        st.session_state.citations_formatted = True

        # Save formatted file paths in session_state for later use
        st.session_state["formatted_files"] = {
            engine: {
                "apa": f"citations_formatted/{article_base}_{engine}_{selected_keyword_group}_apa.txt",
                "mla": f"citations_formatted/{article_base}_{engine}_{selected_keyword_group}_mla.txt",
                "chicago": f"citations_formatted/{article_base}_{engine}_{selected_keyword_group}_chicago.txt",
            } for engine in engines
        }

    if st.button("Format Citations", on_click=format_citations):
        st.success("✅ Citations formatted.")

    # View formatted citations if available
    if "formatted_files" in st.session_state and st.session_state.citations_formatted:
        st.markdown("### 📖 View Formatted Citations")
        engine = st.selectbox("Select Engine", ["openalex", "semanticscholar", "crossref"])
        format_type = st.selectbox("Select Format", ["apa", "mla", "chicago"])
        selected_file = st.session_state["formatted_files"][engine][format_type]
        if os.path.exists(selected_file):
            with open(selected_file, "r", encoding="utf-8") as f:
                st.text_area(f"{engine.title()} - {format_type.upper()} Citation", f.read(), height=300)
        else:
            st.warning("Citation file not found. Did you run formatting first?")

    # Export BibTeX button callback
    def export_bibtex():
        for engine in ["openalex", "semanticscholar", "crossref"]:
            subprocess.run([
                "python", "scripts/json_to_bibtex.py",
                f"references_raw/{article_base}_references_{engine}_{selected_keyword_group}.json",
                f"citations_formatted/{article_base}_{engine}_{selected_keyword_group}.bib"
            ])

    if st.button("Export BibTeX", on_click=export_bibtex):
        st.success("✅ BibTeX files generated.")

    if article_path and article_base:
        st.header("📌 Keyword Extraction and Reference Matching Diagram")

        if st.button("🧩 Generate Full Diagram"):
            output_path = f"diagrams/{article_base}_pipeline.html"

            try:
                result = subprocess.run(
                    ["python", "scripts/generate_pipeline_graph.py", article_path, output_path, selected_keyword_group],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                st.success("Diagram successfully generated.")
                st.code(result.stdout)

                with open(output_path, "r", encoding="utf-8") as f:
                    st.components.v1.html(f.read(), height=800, scrolling=True)

            except subprocess.CalledProcessError as e:
                st.error("An error occurred while generating the diagram.")
                st.code(e.stderr)
