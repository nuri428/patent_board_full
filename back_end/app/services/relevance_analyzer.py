import logging
import math
import re
from collections import Counter


logger = logging.getLogger(__name__)


class RelevanceAnalyzer:
    """Analyze chatbot answer relevance for a query-response pair."""

    _TOKEN_PATTERN: re.Pattern[str] = re.compile(r"\b\w+\b", flags=re.UNICODE)
    _STOPWORDS: set[str] = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }

    def analyze_relevance(self, query: str, response: str) -> dict[str, object]:
        """Calculate relevance score and metadata for a query-response pair."""
        logger.info(
            "Starting relevance analysis: query_len=%s response_len=%s",
            len(query or ""),
            len(response or ""),
        )

        if not query or not response:
            logger.warning("Relevance analysis received empty query or response")
            return {
                "relevance_score": 0.0,
                "analysis_metadata": {
                    "matched_keywords": [],
                    "keyword_match_count": 0,
                    "query_keyword_count": 0,
                    "response_length": len(response or ""),
                    "semantic_score": 0.0,
                    "context_score": 0.0,
                    "factors": {
                        "keyword_weight": 0.5,
                        "semantic_weight": 0.3,
                        "context_weight": 0.2,
                    },
                },
            }

        query_tokens = self._extract_keywords(query)
        response_tokens = self._extract_keywords(response)
        query_counter = Counter(query_tokens)
        response_counter = Counter(response_tokens)

        keyword_score, matched_keywords, keyword_match_count = self._keyword_match_score(
            query_counter, response_counter
        )
        semantic_score = self._semantic_similarity_score(query_tokens, response_tokens)
        context_score = self._context_alignment_score(
            query_tokens=query_tokens,
            response_tokens=response_tokens,
            response=response,
        )

        relevance_score = self._normalize_score(
            (keyword_score * 0.5) + (semantic_score * 0.3) + (context_score * 0.2)
        )

        metadata = {
            "matched_keywords": matched_keywords,
            "keyword_match_count": keyword_match_count,
            "query_keyword_count": len(query_tokens),
            "response_length": len(response),
            "semantic_score": semantic_score,
            "context_score": context_score,
            "factors": {
                "keyword_weight": 0.5,
                "semantic_weight": 0.3,
                "context_weight": 0.2,
            },
        }

        logger.info(
            "Completed relevance analysis: relevance_score=%.4f keyword_matches=%s semantic_score=%.4f context_score=%.4f",
            relevance_score,
            keyword_match_count,
            semantic_score,
            context_score,
        )
        logger.debug("Relevance analysis metadata: %s", metadata)

        return {
            "relevance_score": relevance_score,
            "analysis_metadata": metadata,
        }

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract normalized keywords from text."""
        tokens = [token.lower() for token in self._TOKEN_PATTERN.findall(text)]
        return [token for token in tokens if len(token) > 1 and token not in self._STOPWORDS]

    def _keyword_match_score(
        self, query_counter: Counter[str], response_counter: Counter[str]
    ) -> tuple[float, list[str], int]:
        """Compute weighted keyword matching score using term frequency overlap."""
        if not query_counter:
            return 0.0, [], 0

        matched: list[str] = []
        matched_count = 0
        for term, query_count in query_counter.items():
            if term in response_counter:
                match_count = min(query_count, response_counter[term])
                matched.extend([term] * match_count)
                matched_count += match_count

        total_query_terms = sum(query_counter.values())
        score = matched_count / total_query_terms if total_query_terms else 0.0
        return self._normalize_score(score), sorted(set(matched)), matched_count

    def _semantic_similarity_score(
        self, query_tokens: list[str], response_tokens: list[str]
    ) -> float:
        """Approximate semantic similarity with cosine similarity on token frequency vectors."""
        if not query_tokens or not response_tokens:
            return 0.0

        query_counter = Counter(query_tokens)
        response_counter = Counter(response_tokens)
        shared_terms = set(query_counter) | set(response_counter)

        dot_product = sum(query_counter[term] * response_counter[term] for term in shared_terms)
        query_norm = math.sqrt(sum(value * value for value in query_counter.values()))
        response_norm = math.sqrt(sum(value * value for value in response_counter.values()))

        if query_norm == 0.0 or response_norm == 0.0:
            return 0.0

        return self._normalize_score(dot_product / (query_norm * response_norm))

    def _context_alignment_score(
        self,
        query_tokens: list[str],
        response_tokens: list[str],
        response: str,
    ) -> float:
        """Estimate context alignment from topical overlap and response adequacy."""
        if not query_tokens or not response_tokens:
            return 0.0

        query_terms = set(query_tokens)
        response_terms = set(response_tokens)
        overlap_ratio = len(query_terms & response_terms) / len(query_terms)

        response_word_count = len(self._TOKEN_PATTERN.findall(response))
        if response_word_count < 8:
            length_factor = 0.4
        elif response_word_count > 450:
            length_factor = 0.8
        else:
            length_factor = 1.0

        return self._normalize_score((overlap_ratio * 0.7) + (length_factor * 0.3))

    def _normalize_score(self, score: float) -> float:
        """Clamp score into a 0.0-1.0 range with fixed precision."""
        return round(max(0.0, min(1.0, score)), 4)
