from collections.abc import Iterable

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span, Token

from argus.analysis.lexicons import (
    CERTAINTY_MARKERS,
    FEAR_MARKERS,
    THREAT_MARKERS,
    UNCERTAINTY_MARKERS,
)
from argus.analysis.schemas import DiscourseMetrics, EvidenceSpan


class DiscourseAnalyzer:
    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self.nlp: Language = spacy.load(model_name)

    def analyze(self, text: str) -> DiscourseMetrics:
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")

        doc = self.nlp(text)

        sentences = list(doc.sents)
        word_tokens = [
            token
            for token in doc
            if not token.is_space and not token.is_punct
        ]

        evidence: list[EvidenceSpan] = []

        certainty_count = self._collect_lexicon_matches(
            sentences=sentences,
            lexicon=CERTAINTY_MARKERS,
            category="certainty",
            evidence=evidence,
        )
        uncertainty_count = self._collect_lexicon_matches(
            sentences=sentences,
            lexicon=UNCERTAINTY_MARKERS,
            category="uncertainty",
            evidence=evidence,
        )
        fear_count = self._collect_lexicon_matches(
            sentences=sentences,
            lexicon=FEAR_MARKERS,
            category="fear",
            evidence=evidence,
        )
        threat_count = self._collect_lexicon_matches(
            sentences=sentences,
            lexicon=THREAT_MARKERS,
            category="threat",
            evidence=evidence,
        )

        first_person_plural_count = self._count_lemmas(
            word_tokens,
            {"we", "our", "ours", "us"},
        )
        third_person_plural_count = self._count_lemmas(
            word_tokens,
            {"they", "their", "theirs", "them"},
        )

        sentence_count = len(sentences)
        word_count = len(word_tokens)

        average_sentence_length = (
            word_count / sentence_count
            if sentence_count > 0
            else 0.0
        )

        return DiscourseMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            average_sentence_length=round(
                average_sentence_length,
                2,
            ),
            question_count=text.count("?"),
            exclamation_count=text.count("!"),
            first_person_plural_count=first_person_plural_count,
            third_person_plural_count=third_person_plural_count,
            certainty_marker_count=certainty_count,
            uncertainty_marker_count=uncertainty_count,
            fear_marker_count=fear_count,
            threat_marker_count=threat_count,
            evidence=evidence,
        )

    @staticmethod
    def _count_lemmas(
            tokens: Iterable[Token],
            lemmas: set[str],
    ) -> int:
        return sum(
            1
            for token in tokens
            if token.lemma_.lower() in lemmas
        )

    @staticmethod
    def _collect_lexicon_matches(
            sentences: list[Span],
            lexicon: set[str],
            category: str,
            evidence: list[EvidenceSpan],
    ) -> int:
        total = 0

        for sentence in sentences:
            matched_terms = [
                token.lemma_.lower()
                for token in sentence
                if token.lemma_.lower() in lexicon
            ]

            if not matched_terms:
                continue

            total += len(matched_terms)

            evidence.append(
                EvidenceSpan(
                    category=category,
                    sentence=sentence.text.strip(),
                    matched_terms=sorted(set(matched_terms)),
                )
            )

        return total