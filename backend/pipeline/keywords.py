from sklearn.feature_extraction.text import TfidfVectorizer
import yake
from typing import List

def extract_keywords_tfidf(clauses: List[str], top_n: int = 5) -> List[List[str]]:
    """
    Finds top important words per clause using TF-IDF across the contract clauses.
    """
    if len(clauses) < 2:
        return [[] for _ in clauses]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=200)
    tfidf_matrix = vectorizer.fit_transform(clauses)
    feature_names = vectorizer.get_feature_names_out()

    results = []
    for row in tfidf_matrix:
        row_data = row.toarray()[0]
        top_indices = row_data.argsort()[-top_n:][::-1]
        top_words = [feature_names[i] for i in top_indices if row_data[i] > 0]
        results.append(top_words)

    return results


def extract_keywords_yake(text: str, top_n: int = 5) -> List[str]:
    """
    YAKE keyword and keyphrase extraction within a single piece of text.
    """
    kw_extractor = yake.KeywordExtractor(top=top_n, n=2)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]
