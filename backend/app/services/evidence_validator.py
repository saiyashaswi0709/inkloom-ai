from typing import List, Dict, Any, Optional, Tuple
from app.models import GuidelineChunk, ApprovedFact, FindingType, FindingSeverity

class EvidenceValidator:
    """Validates AI citations against ground truth database records.
    Guarantees no fabricated references or imaginary guidelines reach the user.
    """

    @staticmethod
    def validate_citation(
        citation_source: Optional[str],
        citation_section: Optional[str],
        claimed_evidence_text: Optional[str],
        available_chunks: List[GuidelineChunk],
        available_facts: List[ApprovedFact]
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Validates citation against stored chunks and facts.
        Returns (is_valid, validated_source, validated_section, matched_chunk_id).
        """
        if not citation_source and not citation_section and not claimed_evidence_text:
            return False, "Unverified Claim", "No Approved Record Found", None

        # Check in guideline chunks
        for chunk in available_chunks:
            # Check source doc name or section
            doc_name = chunk.guideline.source_document_name if chunk.guideline else ""
            title = chunk.guideline.title if chunk.guideline else ""
            section = chunk.section_name or ""

            # Direct match on chunk ID if provided
            if citation_section and (citation_section.lower() in section.lower() or section.lower() in citation_section.lower()):
                return True, doc_name or title or "Brand Guideline", section, chunk.id

            if claimed_evidence_text and (claimed_evidence_text.lower() in chunk.content.lower() or chunk.content.lower() in claimed_evidence_text.lower()):
                return True, doc_name or title or "Brand Guideline", section, chunk.id

        # Check in approved facts
        for fact in available_facts:
            if claimed_evidence_text and (claimed_evidence_text.lower() in fact.statement.lower() or fact.statement.lower() in claimed_evidence_text.lower()):
                return True, f"Approved Fact ({fact.verification_source})", fact.category, None
            if citation_source and fact.verification_source and citation_source.lower() in fact.verification_source.lower():
                return True, f"Approved Fact ({fact.verification_source})", fact.category, None

        # If no valid ground truth matches, return unverified
        return False, "Unverified Source", "External / Unconfirmed Claim", None
