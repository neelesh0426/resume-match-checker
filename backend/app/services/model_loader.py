import logging
import threading
from typing import Optional
import spacy
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

_spacy_nlp: Optional[spacy.language.Language] = None
_embedding_model: Optional[SentenceTransformer] = None
_model_lock = threading.Lock()


def get_spacy_nlp() -> spacy.language.Language:
    """Returns cached spaCy Language model singleton.
    Lazy loaded on first request for fast server startup.
    """
    global _spacy_nlp
    if _spacy_nlp is None:
        with _model_lock:
            if _spacy_nlp is None:
                model_name = settings.spacy_model_name
                try:
                    logger.info(f"Loading spaCy model: {model_name}...")
                    _spacy_nlp = spacy.load(model_name)
                    logger.info("spaCy model loaded successfully.")
                except Exception as e:
                    logger.warning(f"Could not load spaCy model '{model_name}': {e}. Falling back to blank 'en' model.")
                    _spacy_nlp = spacy.blank("en")
    return _spacy_nlp


def get_embedding_model() -> SentenceTransformer:
    """Returns cached SentenceTransformer model singleton ('all-MiniLM-L6-v2').
    Downloads once to local HuggingFace cache on first use, then runs locally.
    """
    global _embedding_model
    if _embedding_model is None:
        with _model_lock:
            if _embedding_model is None:
                model_name = settings.embedding_model_name
                logger.info(f"Loading SentenceTransformer: {model_name} (runs locally)...")
                _embedding_model = SentenceTransformer(model_name)
                logger.info("SentenceTransformer model loaded successfully.")
    return _embedding_model
