"""
PulseMetrics-AI: Qualitative RAG (Retrieval-Augmented Generation) Engine
Indexes unstructured customer feedback, churn exit interviews, and executive QBRs.
Retrieves relevant contextual excerpts and citations to explain the 'why' behind the numbers.
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

class QualitativeRAGEngine:
    def __init__(self):
        self.doc_df = pd.read_csv(os.path.join(RAW_DIR, "qualitative_customer_transcripts.csv"))
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.doc_df["notes"].fillna(""))
        
    def search(self, query: str, top_k: int = 4):
        """Retrieves top_k relevant qualitative document excerpts matching the query."""
        q_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(q_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(sim_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = sim_scores[idx]
            if score > 0.05: # Relevance threshold
                row = self.doc_df.iloc[idx]
                results.append({
                    "doc_id": row["doc_id"],
                    "customer_id": row["customer_id"],
                    "doc_type": row["doc_type"],
                    "author": row["author"],
                    "date": row["date"],
                    "notes": row["notes"],
                    "relevance_score": round(float(score), 3)
                })
        return results

if __name__ == "__main__":
    rag = QualitativeRAGEngine()
    hits = rag.search("competitor pricing datadog and api latency")
    print(f"Retrieved {len(hits)} hits:")
    for h in hits:
        print(f"[{h['doc_type']} | Score: {h['relevance_score']}] {h['notes']}")
