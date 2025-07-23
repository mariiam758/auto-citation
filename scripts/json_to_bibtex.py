import json

def json_to_bibtex_entry(ref, index):
    # Handle author list
    authors_list = []
    if isinstance(ref.get("author"), list):
        for author in ref["author"]:
            name = author.get("name") or f"{author.get('given', '')} {author.get('family', '')}".strip()
            if name:
                authors_list.append(name)
    elif isinstance(ref.get("author"), str):
        authors_list = [a.strip() for a in ref["author"].split(",")]

    authors = " and ".join(authors_list)

    title = ref.get("title", "")
    journal = ref.get("venue") or ref.get("journal", "")
    year = ref.get("year") or ref.get("publicationYear", "")
    doi = ref.get("doi", "") or ref.get("externalIds", {}).get("DOI", "")
    
    bibtex = f"@article{{ref{index},\n"
    if authors:
        bibtex += f"  author = {{{authors}}},\n"
    if title:
        bibtex += f"  title = {{{title}}},\n"
    if journal:
        bibtex += f"  journal = {{{journal}}},\n"
    if year:
        bibtex += f"  year = {{{year}}},\n"
    if doi:
        bibtex += f"  doi = {{{doi}}},\n"
    bibtex += "}\n"

    return bibtex

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python json_to_bibtex.py <references_json_file> <output_bib_file>")
        sys.exit(1)
    
    ref_file = sys.argv[1]
    bib_file = sys.argv[2]

    with open(ref_file, "r", encoding="utf-8") as f:
        references_raw = json.load(f)

    # Flatten dict of lists to a single list
    if isinstance(references_raw, dict):
        references = []
        for refs_list in references_raw.values():
            references.extend(refs_list)
    else:
        references = references_raw

    with open(bib_file, "w", encoding="utf-8") as f:
        for i, ref in enumerate(references):
            entry = json_to_bibtex_entry(ref, i + 1)
            f.write(entry + "\n")

    print(f"BibTeX entries saved to {bib_file}")

