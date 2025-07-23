import json

def extract_authors(ref):
    if "author" in ref and isinstance(ref["author"], str):
        return ref["author"]
    elif "authors" in ref:
        if isinstance(ref["authors"], list):
            # Case 1: List of dicts (e.g. {"name": "John Doe"})
            if all(isinstance(a, dict) and "name" in a for a in ref["authors"]):
                return ", ".join(a.get("name", "") for a in ref["authors"])
            # Case 2: List of strings
            elif all(isinstance(a, str) for a in ref["authors"]):
                return ", ".join(ref["authors"])
    return "Bilinmeyen Yazar"


def extract_doi(ref):
    if "doi" in ref:
        return ref["doi"]
    elif "externalIds" in ref and "DOI" in ref["externalIds"]:
        return ref["externalIds"]["DOI"]
    return ""

def extract_journal(ref):
    if "journal" in ref:
        return ref["journal"]
    elif "venue" in ref:
        return ref["venue"]
    return ""

def extract_year(ref):
    return ref.get("year", "n.d.")

def extract_title(ref):
    return ref.get("title", "Başlıksız")

def format_apa(ref):
    authors = extract_authors(ref)
    year = extract_year(ref)
    title = extract_title(ref)
    journal = extract_journal(ref)
    doi = extract_doi(ref)
    
    citation = f"{authors} ({year}). {title}."
    if journal:
        citation += f" {journal}."
    if doi:
        citation += f" doi:{doi}"
    return citation

def format_mla(ref):
    authors = extract_authors(ref)
    title = extract_title(ref)
    journal = extract_journal(ref)
    year = extract_year(ref)
    citation = f"{authors}. \"{title}.\" {journal}, {year}."
    return citation

def format_chicago(ref):
    authors = extract_authors(ref)
    title = extract_title(ref)
    journal = extract_journal(ref)
    year = extract_year(ref)
    citation = f"{authors}. \"{title}.\" {journal} ({year})."
    return citation

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python format_citations.py <references_json_file> <output_prefix>")
        sys.exit(1)
    
    ref_file = sys.argv[1]
    output_prefix = sys.argv[2]

    with open(ref_file, "r", encoding="utf-8") as f:
        references_raw = json.load(f)

    # Flatten if the JSON is grouped by keywords (dict of lists)
    if isinstance(references_raw, dict):
        references = []
        for refs_list in references_raw.values():
            references.extend(refs_list)
    else:
        references = references_raw

    apa_citations = [format_apa(r) for r in references]
    mla_citations = [format_mla(r) for r in references]
    chicago_citations = [format_chicago(r) for r in references]

    with open(f"{output_prefix}_apa.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(apa_citations))

    with open(f"{output_prefix}_mla.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(mla_citations))

    with open(f"{output_prefix}_chicago.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(chicago_citations))

    print(f"Citations formatted and saved as {output_prefix}_{{apa,mla,chicago}}.txt")


# python scripts/format_citations.py references_raw/article_1_references_openalex.json citations_formatted/article_1_openalex