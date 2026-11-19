import re
from typing import Optional

class CorrectionEngine:
    """Intent-preserving Smart Correction Engine.
    Ensures corrections preserve the author's intent while resolving brand violations.
    """

    @staticmethod
    def extract_surrounding_sentence(text: str, start_pos: int, end_pos: int) -> str:
        """Finds sentence boundaries around the violation."""
        if not text:
            return ""
        
        # Look backwards for sentence start (. ! ? or newline or start of text)
        before = text[:start_pos]
        after = text[end_pos:]

        start_match = re.search(r'[.!?\n]\s*([^\.!?\n]*)$', before)
        sentence_start = start_pos - len(start_match.group(1)) if start_match else 0

        # Look forwards for sentence end (. ! ? or newline or end of text)
        end_match = re.search(r'([^\.!?\n]*[.!?\n]?)', after)
        sentence_end = end_pos + len(end_match.group(1)) if end_match else len(text)

        sentence = text[sentence_start:sentence_end].strip()
        return sentence if sentence else text[start_pos:end_pos]

    @staticmethod
    def build_deterministic_correction(
        sentence: str,
        problematic_text: str,
        preferred_term: Optional[str],
        rule_explanation: str
    ) -> str:
        """Substitutes prohibited terms with preferred terms preserving casing and context."""
        if not preferred_term:
            return sentence

        # If sentence contains exact term with casing preserved
        def replace_with_case(match):
            m_text = match.group(0)
            if m_text.isupper():
                return preferred_term.upper()
            elif m_text.istitle():
                return preferred_term.capitalize()
            return preferred_term

        pattern = re.compile(re.escape(problematic_text), re.IGNORECASE)
        corrected = pattern.sub(replace_with_case, sentence)
        return corrected
