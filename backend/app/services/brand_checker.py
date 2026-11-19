import re
from typing import List, Dict, Any, Optional
from app.models import BrandRule, RuleType, FindingSeverity, FindingType

class DeterministicMatch:
    def __init__(
        self,
        rule_id: str,
        problematic_text: str,
        start_pos: int,
        end_pos: int,
        preferred_term: Optional[str],
        explanation: str,
        severity: FindingSeverity,
        rule_type: RuleType
    ):
        self.rule_id = rule_id
        self.problematic_text = problematic_text
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.preferred_term = preferred_term
        self.explanation = explanation
        self.severity = severity
        self.rule_type = rule_type

class BrandChecker:
    """Deterministic Brand Rule Engine.
    Executes fast regex, keyword, and terminology matching against registered rules.
    """

    @staticmethod
    def check_content(text: str, rules: List[BrandRule]) -> List[DeterministicMatch]:
        matches: List[DeterministicMatch] = []
        if not text or not rules:
            return matches

        for rule in rules:
            if not rule.is_active:
                continue

            if rule.rule_type == RuleType.REGEX and rule.pattern:
                try:
                    pattern = re.compile(rule.pattern, re.IGNORECASE)
                    for m in pattern.finditer(text):
                        matches.append(DeterministicMatch(
                            rule_id=rule.id,
                            problematic_text=m.group(0),
                            start_pos=m.start(),
                            end_pos=m.end(),
                            preferred_term=rule.preferred_term,
                            explanation=rule.explanation or f"Matches restricted pattern: {rule.pattern}",
                            severity=rule.severity,
                            rule_type=rule.rule_type
                        ))
                except re.error:
                    continue

            elif rule.prohibited_term:
                term = rule.prohibited_term.strip()
                if not term:
                    continue
                
                # Word boundary matching for clean words, or literal substring for multi-word phrases
                escaped_term = re.escape(term)
                # If term starts and ends with alphanumeric characters, apply word boundaries
                pattern_str = r'\b' + escaped_term + r'\b' if (term[0].isalnum() and term[-1].isalnum()) else escaped_term
                
                try:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    for m in pattern.finditer(text):
                        matches.append(DeterministicMatch(
                            rule_id=rule.id,
                            problematic_text=m.group(0),
                            start_pos=m.start(),
                            end_pos=m.end(),
                            preferred_term=rule.preferred_term,
                            explanation=rule.explanation or f"'{term}' is prohibited. Use '{rule.preferred_term}' instead.",
                            severity=rule.severity,
                            rule_type=rule.rule_type
                        ))
                except re.error:
                    continue

        # Sort matches by position in text
        matches.sort(key=lambda x: x.start_pos)
        return matches
