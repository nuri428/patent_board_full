import logging
import re
from collections.abc import Iterable
from typing import TypedDict, cast


logger = logging.getLogger(__name__)


class ConfidenceDetails(TypedDict):
    confidence_value: float
    confidence_level: str
    source_factors: object


class ConfidenceCalculator:
    """Calculate confidence scores for chatbot responses."""

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
    _SOURCE_WEIGHTS: dict[str, float] = {
        "KIPRIS": 1.0,
        "KIPO": 0.95,
        "USPTO": 0.9,
        "EPO": 0.85,
        "WIPO": 0.82,
        "JPO": 0.8,
        "CNIPA": 0.78,
        "PCT": 0.8,
        "OTHER": 0.6,
    }
    _FACTOR_WEIGHTS: dict[str, float] = {
        "source_reliability": 0.35,
        "response_completeness": 0.3,
        "context_alignment": 0.25,
        "length_quality": 0.1,
    }

    def calculate_confidence(
        self, response: str, query: str, sources_used: list[object] | None = None
    ) -> float:
        """Return a normalized confidence score in range 0.0-1.0."""
        details = self.calculate_confidence_details(
            response=response,
            query=query,
            sources_used=sources_used,
        )
        return cast(float, details["confidence_value"])

    def calculate_confidence_details(
        self, response: str, query: str, sources_used: list[object] | None = None
    ) -> ConfidenceDetails:
        """Return confidence value, level, and source factors for persistence."""
        logger.info(
            "Starting confidence calculation: query_len=%s response_len=%s sources=%s",
            len(query or ""),
            len(response or ""),
            len(sources_used or []),
        )

        if not response or not query:
            logger.warning("Confidence calculation received empty query or response")
            empty_factors = {
                "source_reliability": 0.0,
                "response_completeness": 0.0,
                "context_alignment": 0.0,
                "length_quality": 0.0,
                "weights": self._FACTOR_WEIGHTS,
                "normalized_sources": [],
            }
            return {
                "confidence_value": 0.0,
                "confidence_level": self.get_confidence_level(0.0),
                "source_factors": empty_factors,
            }

        normalized_sources = self._normalize_sources(sources_used or [])
        source_reliability = self._source_reliability_score(normalized_sources)
        response_completeness = self._response_completeness_score(query, response)
        context_alignment = self._context_alignment_score(query, response)
        length_quality = self._length_quality_score(response)

        weighted_score = (
            (source_reliability * self._FACTOR_WEIGHTS["source_reliability"])
            + (response_completeness * self._FACTOR_WEIGHTS["response_completeness"])
            + (context_alignment * self._FACTOR_WEIGHTS["context_alignment"])
            + (length_quality * self._FACTOR_WEIGHTS["length_quality"])
        )
        confidence_value = self._normalize_score(weighted_score)
        confidence_level = self.get_confidence_level(confidence_value)

        factors = {
            "source_reliability": source_reliability,
            "response_completeness": response_completeness,
            "context_alignment": context_alignment,
            "length_quality": length_quality,
            "weights": self._FACTOR_WEIGHTS,
            "normalized_sources": normalized_sources,
        }

        logger.info(
            "Completed confidence calculation: score=%.4f level=%s source=%.4f completeness=%.4f context=%.4f quality=%.4f",
            confidence_value,
            confidence_level,
            source_reliability,
            response_completeness,
            context_alignment,
            length_quality,
        )
        logger.debug("Confidence factors: %s", factors)

        return {
            "confidence_value": confidence_value,
            "confidence_level": confidence_level,
            "source_factors": factors,
        }

    def get_confidence_level(self, score: float) -> str:
        """Map numeric confidence score to a confidence level label."""
        if score < 0.5:
            return "low"
        if score < 0.7:
            return "medium"
        if score < 0.9:
            return "high"
        return "very_high"

    def _normalize_sources(self, sources_used: Iterable[object]) -> list[str]:
        """Normalize mixed source payloads into uppercase source labels."""
        normalized: list[str] = []
        for source in sources_used:
            if isinstance(source, str):
                value = source.strip().upper()
            elif isinstance(source, dict):
                raw = (
                    source.get("source")
                    or source.get("name")
                    or source.get("database")
                    or source.get("provider")
                    or "OTHER"
                )
                value = str(raw).strip().upper()
            else:
                value = str(source).strip().upper()

            normalized.append(value or "OTHER")
        return normalized

    def _source_reliability_score(self, sources: list[str]) -> float:
        """Score source reliability using patent-source-specific weights."""
        if not sources:
            return 0.4

        source_scores = [self._SOURCE_WEIGHTS.get(source, self._SOURCE_WEIGHTS["OTHER"]) for source in sources]
        reliability = sum(source_scores) / len(source_scores)
        return self._normalize_score(reliability)

    def _response_completeness_score(self, query: str, response: str) -> float:
        """Estimate completeness by checking coverage of query clauses and keywords."""
        query_parts = [part.strip() for part in re.split(r"\?|,|\band\b|\bor\b", query, flags=re.IGNORECASE) if part.strip()]
        response_text = response.lower()

        if not query_parts:
            return 0.0

        covered_parts = 0
        for part in query_parts:
            keywords = self._extract_keywords(part)
            if not keywords:
                continue
            matched = sum(1 for keyword in keywords if keyword in response_text)
            if matched / len(keywords) >= 0.6:
                covered_parts += 1

        part_coverage = covered_parts / max(1, len(query_parts))
        keyword_overlap = self._keyword_overlap_score(query, response)
        return self._normalize_score((part_coverage * 0.7) + (keyword_overlap * 0.3))

    def _context_alignment_score(self, query: str, response: str) -> float:
        """Estimate intent alignment from query-response topical overlap."""
        query_keywords = set(self._extract_keywords(query))
        response_keywords = set(self._extract_keywords(response))

        if not query_keywords:
            return 0.0

        overlap_ratio = len(query_keywords & response_keywords) / len(query_keywords)
        intent_bonus = self._intent_bonus(query, response)
        return self._normalize_score((overlap_ratio * 0.8) + (intent_bonus * 0.2))

    def _length_quality_score(self, response: str) -> float:
        """Estimate quality from response length and sentence structure."""
        words = self._TOKEN_PATTERN.findall(response)
        word_count = len(words)
        sentences = [segment.strip() for segment in re.split(r"[.!?]", response) if segment.strip()]

        if word_count < 12:
            length_score = 0.35
        elif word_count < 35:
            length_score = 0.7
        elif word_count <= 420:
            length_score = 1.0
        else:
            length_score = 0.75

        sentence_score = 1.0 if len(sentences) >= 2 else 0.65
        return self._normalize_score((length_score * 0.7) + (sentence_score * 0.3))

    def _keyword_overlap_score(self, query: str, response: str) -> float:
        """Return keyword overlap ratio between query and response."""
        query_keywords = self._extract_keywords(query)
        response_keywords = set(self._extract_keywords(response))
        if not query_keywords:
            return 0.0

        matched = sum(1 for token in query_keywords if token in response_keywords)
        return self._normalize_score(matched / len(query_keywords))

    def _intent_bonus(self, query: str, response: str) -> float:
        """Return intent bonus for answer style matching query intent."""
        query_lower = query.lower()
        response_lower = response.lower()

        if query_lower.startswith("how") and ("step" in response_lower or "first" in response_lower):
            return 1.0
        if query_lower.startswith("why") and (
            "because" in response_lower or "due to" in response_lower
        ):
            return 1.0
        if query_lower.startswith("what"):
            return 0.8
        return 0.6

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract normalized keywords from text for lightweight NLP scoring."""
        tokens = [token.lower() for token in self._TOKEN_PATTERN.findall(text)]
        return [token for token in tokens if len(token) > 1 and token not in self._STOPWORDS]

    def _normalize_score(self, score: float) -> float:
        """Clamp score into a 0.0-1.0 range with fixed precision."""
        return round(max(0.0, min(1.0, score)), 4)
