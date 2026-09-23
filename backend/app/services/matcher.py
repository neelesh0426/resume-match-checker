import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.model_loader import get_embedding_model

logger = logging.getLogger(__name__)


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """Calculate baseline TF-IDF cosine similarity between two texts."""
    if not text1.strip() or not text2.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=2000
        )
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(np.clip(sim, 0.0, 1.0))
    except Exception as e:
        logger.warning(f"TF-IDF similarity calculation error: {e}")
        return 0.0


def compute_dense_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Calculate dense semantic similarity using all-MiniLM-L6-v2 sentence embeddings.
    Embeds resume and JD, computing cosine similarity between document vectors.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    try:
        model = get_embedding_model()

        # To capture fine-grained relevance, we also chunk long documents
        # into paragraphs / segments of ~256-512 tokens
        resume_trimmed = resume_text[:4000]
        jd_trimmed = jd_text[:4000]

        embeddings = model.encode(
            [resume_trimmed, jd_trimmed],
            normalize_embeddings=True,
            show_progress_bar=False
        )

        # Dot product of normalized vectors equals cosine similarity
        sim = float(np.dot(embeddings[0], embeddings[1]))
        return float(np.clip(sim, 0.0, 1.0))
    except Exception as e:
        logger.error(f"Semantic similarity computation error: {e}")
        return 0.0


def compute_overall_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Combines dense semantic embedding similarity (80%) and TF-IDF lexical similarity (20%).
    Returns a unified semantic relevance score in [0.0, 1.0].
    """
    dense_sim = compute_dense_semantic_similarity(resume_text, jd_text)
    tfidf_sim = compute_tfidf_similarity(resume_text, jd_text)

    # Blend: Sentence embeddings capture conceptual meaning, TF-IDF reinforces exact terminology match
    combined = (0.80 * dense_sim) + (0.20 * tfidf_sim)
    return float(np.clip(round(combined, 4), 0.0, 1.0))
