import re
import math
from typing import List, Dict, Tuple, Optional
from app.models import GuidelineChunk, ApprovedFact

class GuidelineRetriever:
    """Context-aware retriever for brand guidelines and approved facts.
    Uses token-overlap and term frequency retrieval with pgvector upgrade path.
    """

    @staticmethod
    def _tokenize(text: str) -> set:
        if not text:
            return set()
        words = re.findall(r'\b[a-zA-Z0-9_\-]{3,}\b', text.lower())
        # Filter common stop words
        stopwords = {
            "the", "and", "for", "with", "that", "this", "from", "are", "have", "has",
            "our", "your", "will", "all", "any", "can", "should", "their", "about"
        }
        return {w for w in words if w not in stopwords}

    @classmethod
    def retrieve_relevant_chunks(
        cls,
        text: str,
        chunks: List[GuidelineChunk],
        top_k: int = 6
    ) -> List[GuidelineChunk]:
        if not text or not chunks:
            return []

        text_tokens = cls._tokenize(text)
        if not text_tokens:
            return chunks[:top_k]

        scored_chunks: List[Tuple[float, GuidelineChunk]] = []
        for chunk in chunks:
            chunk_tokens = cls._tokenize(chunk.content + " " + (chunk.section_name or ""))
            if not chunk_tokens:
                continue

            intersection = text_tokens.intersection(chunk_tokens)
            if not intersection:
                score = 0.0
            else:
                # Jaccard / token overlap score boosted by intersection count
                overlap = len(intersection)
                score = overlap / (math.sqrt(len(text_tokens)) * math.sqrt(len(chunk_tokens)) + 1e-5)
            
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        # Return top_k with positive scores or default fallback chunks
        results = [c for score, c in scored_chunks if score > 0][:top_k]
        if not results:
            results = chunks[:top_k]
        return results

    @classmethod
    def retrieve_relevant_facts(
        cls,
        text: str,
        facts: List[ApprovedFact],
        top_k: int = 8
    ) -> List[ApprovedFact]:
        if not text or not facts:
            return []

        text_tokens = cls._tokenize(text)
        if not text_tokens:
            return facts[:top_k]

        scored_facts: List[Tuple[float, ApprovedFact]] = []
        for fact in facts:
            if not fact.is_active:
                continue
            fact_tokens = cls._tokenize(fact.statement + " " + fact.category)
            intersection = text_tokens.intersection(fact_tokens)
            if not intersection:
                score = 0.0
            else:
                score = len(intersection) / (math.sqrt(len(text_tokens)) * math.sqrt(len(fact_tokens)) + 1e-5)
            scored_facts.append((score, fact))

        scored_facts.sort(key=lambda x: x[0], reverse=True)
        results = [f for score, f in scored_facts if score > 0][:top_k]
        if not results:
            results = [f for f in facts if f.is_active][:top_k]
        return results
