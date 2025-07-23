import requests
import json
import nltk
import re
import string
from nltk.corpus import stopwords
from typing import List, Dict

nltk.download('stopwords')

# --- Utility ---
def clean_and_filter_keywords(keywords):
    stop_words = set(stopwords.words("english"))
    cleaned_keywords = []

    for kw in keywords:
        kw = re.sub(f"[{re.escape(string.punctuation)}]", "", kw)
        words = [w for w in kw.lower().split() if w not in stop_words and len(w) > 2]
        if 1 < len(words) <= 4:
            cleaned_keywords.append(" ".join(words))

    seen = set()
    unique_keywords = []
    for kw in cleaned_keywords:
        if kw not in seen:
            unique_keywords.append(kw)
            seen.add(kw)

    return unique_keywords[:5]


# --- OpenAlex ---
def query_openalex(keywords, max_results=2):
    base_url = "https://api.openalex.org/works"
    keyword_to_refs = {}

    print(f"Querying OpenAlex with up to {max_results} results per keyword...")
    for kw in keywords:
        params = {"search": kw, "per_page": max_results}
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"OpenAlex query failed for '{kw}' with status {response.status_code}")
            continue

        data = response.json()
        refs = []
        for item in data.get('results', []):
            refs.append({
                "title": item.get("title"),
                "author": ", ".join([auth.get("author", {}).get("display_name", "") for auth in item.get("authorships", [])]),
                "year": item.get("publication_year"),
                "journal": item.get("host_venue", {}).get("display_name"),
                "doi": item.get("doi"),
                "url": item.get("id")
            })
        keyword_to_refs[kw] = refs[:max_results]

    return keyword_to_refs


# --- Crossref ---
def query_crossref(keywords, max_results=2):
    base_url = "https://api.crossref.org/works"
    keyword_to_refs = {}

    print(f"Querying Crossref with up to {max_results} results per keyword...")
    for kw in keywords:
        params = {"query": kw, "rows": max_results}
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Crossref query failed for '{kw}' with status {response.status_code}")
            continue

        data = response.json()
        refs = []
        for item in data.get('message', {}).get('items', []):
            refs.append({
                "title": item.get("title", [""])[0] if item.get("title") else "",
                "author": ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author", [])]) if item.get("author") else "",
                "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                "journal": item.get("container-title", [""])[0] if item.get("container-title") else "",
                "doi": item.get("DOI"),
                "url": item.get("URL")
            })
        keyword_to_refs[kw] = refs[:max_results]

    return keyword_to_refs


# --- Semantic Scholar ---
def query_semanticscholar(keywords: List[str], max_results: int = 2) -> Dict[str, List[Dict]]:
    keyword_to_refs = {}
    print(f"Querying Semantic Scholar with up to {max_results} results per keyword...")

    for kw in keywords:
        print(f"\n🔍 Querying: '{kw}'")
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={kw}&limit={max_results}&fields=title,authors,year,abstract,url"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ Semantic Scholar query failed for '{kw}' with status {response.status_code}")
                print("Response content:", response.text)
                continue

            data = response.json()
            papers = data.get("data", [])
            print(f"✅ Found {len(papers)} papers for keyword '{kw}'")

            refs = []
            for item in papers:
                refs.append({
                    "title": item.get("title"),
                    "authors": [a.get("name") for a in item.get("authors", [])],
                    "year": item.get("year"),
                    "abstract": item.get("abstract"),
                    "url": item.get("url"),
                    "source": "semanticscholar",
                })
            keyword_to_refs[kw] = refs

        except Exception as e:
            print(f"⚠️ Exception for keyword '{kw}':", e)

    print("\n📦 Final grouped references:")
    print(json.dumps(keyword_to_refs, indent=2, ensure_ascii=False))

    return keyword_to_refs


# --- Entry Point ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Usage: python fetch_references.py <keyword_json_file> <output_json_file> <source> <keyword_group>")
        print("Example: python fetch_references.py keywords/article_1_keywords.json references/article_1_refs.json openalex rake")
        sys.exit(1)

    keywords_file = sys.argv[1]
    output_file = sys.argv[2]
    source = sys.argv[3].lower()
    keyword_group = sys.argv[4]  # e.g. "rake", "yake", "bert_score"

    with open(keywords_file, "r", encoding="utf-8") as f:
        keyword_data = json.load(f)

    keywords = keyword_data.get(keyword_group, [])
    if not keywords:
        print(f"No keywords found under '{keyword_group}' key in JSON.")
        sys.exit(1)

    max_results = 2

    if source == "openalex":
        refs = query_openalex(keywords, max_results)
    elif source == "crossref":
        refs = query_crossref(keywords, max_results)
    elif source == "semanticscholar":
        refs = query_semanticscholar(keywords, max_results)
    else:
        print(f"Unknown source: {source}")
        sys.exit(1)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(refs, f, indent=2, ensure_ascii=False)

    print(f"References saved to {output_file}")


# python scripts/fetch_references.py keywords/article_1_keywords.json references_raw/article_1_references_openalex.json openalex yake
