import json
from rake_nltk import Rake
import yake
from transformers import AutoTokenizer, AutoModel, AutoModelForTokenClassification
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def extract_rake(text, max_keywords=10):
    r = Rake()
    r.extract_keywords_from_text(text)
    ranked_phrases = r.get_ranked_phrases()[:max_keywords]
    return ranked_phrases

def extract_yake(text, max_keywords=10):
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=max_keywords)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]

# Basic BERTScore-based keyword extraction:
# Here we score candidate keywords by their embedding similarity to the document embedding
def extract_bert_keywords(text, candidate_phrases, max_keywords=10):
    from transformers import AutoTokenizer, AutoModel
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    model = AutoModel.from_pretrained('bert-base-uncased')
    
    def embed_text(texts):
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:,0,:].numpy()
        return embeddings

    doc_embedding = embed_text([text])[0]
    candidates_embeddings = embed_text(candidate_phrases)
    sims = cosine_similarity([doc_embedding], candidates_embeddings)[0]
    
    top_idx = np.argsort(sims)[::-1][:max_keywords]
    top_keywords = [candidate_phrases[i] for i in top_idx]
    return top_keywords

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python extract_keywords.py <input_text_file> <output_json_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("Extracting RAKE keywords...")
    rake_keywords = extract_rake(text)
    print("Extracting YAKE keywords...")
    yake_keywords = extract_yake(text)
    print("Generating candidate phrases for BERTScore...")
    # As a simple candidate phrase set for BERTScore, use rake keywords here
    bert_keywords = extract_bert_keywords(text, rake_keywords)
    
    results = {
        "rake": rake_keywords,
        "yake": yake_keywords,
        "bert_score": bert_keywords
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"Keywords saved to {output_path}")
