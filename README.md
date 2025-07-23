# 🧠 Auto Citation Pipeline

This project is a multi-step citation generation pipeline that takes an article, extracts keywords, fetches relevant academic references, formats them into APA style, and generates a `.bib` file — all through a user-friendly Streamlit interface.


## 🚀 How to Run

### 1. Install requirements

```bash
pip install -r requirements.txt
```

### 2. Add article
Put your .txt file in the articles/ folder. For example:

```bash

articles/article_1.txt
```

### 3. Launch the Streamlit app
```bash

streamlit run app.py
```

### 4. Use the Interface

Select an article from the dropdown.

Click buttons in order:

1. Extract Keywords

2. Fetch References (choose keyword group : rake, yake, ..)

3. Format Citations

4. Export BibTeX

5. Generate full diagram


