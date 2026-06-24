from sklearn.feature_extraction.text import TfidfVectorizer
import yake

def extract_keywords_tfidf(clauses, top_n=5):
    """
    Takes a list of clauses (strings) and finds the top important words
    PER clause, using TF-IDF across the whole set of clauses as context.
    """
    if len(clauses) < 2:
        return [[] for _ in clauses]  # not enough data for TF-IDF comparison

    vectorizer = TfidfVectorizer(stop_words="english", max_features=200)
    tfidf_matrix = vectorizer.fit_transform(clauses)
    feature_names = vectorizer.get_feature_names_out()

    results = []
    for row in tfidf_matrix:
        row_data = row.toarray()[0]
        # Get indices of top N highest TF-IDF scores
        top_indices = row_data.argsort()[-top_n:][::-1]
        top_words = [feature_names[i] for i in top_indices if row_data[i] > 0]
        results.append(top_words)

    return results


def extract_keywords_yake(text, top_n=5):
    """
    YAKE looks WITHIN a single piece of text and finds important
    phrases based on position, frequency, and word relationships.
    Works well even on a single clause (unlike TF-IDF which needs many documents).
    """
    kw_extractor = yake.KeywordExtractor(top=top_n, n=2)  # n=2 means up to 2-word phrases
    keywords = kw_extractor.extract_keywords(text)
    # yake returns (keyword, score) tuples — lower score = more important
    return [kw for kw, score in keywords]