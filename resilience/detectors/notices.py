"""Notice generation from detection results.

Transforms triggered detections into formal legal notices following
the templates established in the project's legal strategy documents:
- Notice of Clouded Title
- Fiduciary Liability Notice
- Shareholder Disclosure Letter
- Press Release
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from resilience.detectors.templates import DetectionResult, ThreatType


class NoticeType(Enum):
    """Types of formal notices that can be generated."""

    CLOUDED_TITLE = "clouded_title"
    FIDUCIARY_LIABILITY = "fiduciary_liability"
    SHAREHOLDER_LETTER = "shareholder_letter"
    PRESS_RELEASE = "press_release"


# Mapping from threat types to the most appropriate notice type
_THREAT_TO_NOTICE = {
    ThreatType.CONFLICT_OF_INTEREST: NoticeType.SHAREHOLDER_LETTER,
    ThreatType.CORPORATE_LEVERAGE: NoticeType.CLOUDED_TITLE,
    ThreatType.FPIC_VIOLATION: NoticeType.CLOUDED_TITLE,
    ThreatType.DISCLOSURE_GAP: NoticeType.SHAREHOLDER_LETTER,
    ThreatType.SOVEREIGNTY_THREAT: NoticeType.PRESS_RELEASE,
    ThreatType.FIDUCIARY_BREACH: NoticeType.FIDUCIARY_LIABILITY,
}


@dataclass
class Notice:
    """A generated legal notice ready for distribution."""

    notice_type: NoticeType
    title: str
    body: str
    legal_basis: List[str]
    target_entities: List[str]

    def full_text(self) -> str:
        """Render the complete notice text."""
        lines = [self.title, "=" * len(self.title), ""]
        lines.append(self.body)
        lines.append("")
        if self.legal_basis:
            lines.append("LEGAL BASIS:")
            for basis in self.legal_basis:
                lines.append(f"  - {basis}")
        if self.target_entities:
            lines.append("")
            lines.append("ADDRESSED TO:")
            for entity in self.target_entities:
                lines.append(f"  - {entity}")
        return "\n".join(lines)


class NoticeGenerator:
    """Generates formal notices from detection results."""

    def suggest_notice_type(self, result: DetectionResult) -> NoticeType:
        """Determine the appropriate notice type for a detection result."""
        return _THREAT_TO_NOTICE.get(
            result.threat_type, NoticeType.SHAREHOLDER_LETTER
        )

    def generate(
        self,
        result: DetectionResult,
        target_entities: List[str] | None = None,
        notice_type: NoticeType | None = None,
    ) -> Notice:
        """Generate a notice from a triggered detection result.

        Args:
            result: A detection result (should be triggered).
            target_entities: Who to address the notice to.
            notice_type: Override the auto-suggested notice type.
        """
        ntype = notice_type or self.suggest_notice_type(result)
        targets = target_entities or []
        legal_basis = [
            f"{hook.statute} - {hook.description}"
            for hook in result.applicable_hooks
        ]

        generator = {
            NoticeType.CLOUDED_TITLE: self._clouded_title,
            NoticeType.FIDUCIARY_LIABILITY: self._fiduciary_liability,
            NoticeType.SHAREHOLDER_LETTER: self._shareholder_letter,
            NoticeType.PRESS_RELEASE: self._press_release,
        }[ntype]

        title, body = generator(result)
        return Notice(
            notice_type=ntype,
            title=title,
            body=body,
            legal_basis=legal_basis,
            target_entities=targets,
        )

    def generate_batch(
        self, results: List[DetectionResult], target_entities: List[str] | None = None
    ) -> List[Notice]:
        """Generate notices for all triggered results."""
        return [
            self.generate(r, target_entities=target_entities)
            for r in results
            if r.triggered
        ]

    @staticmethod
    def _clouded_title(result: DetectionResult) -> tuple[str, str]:
        signals = ", ".join(result.signal_scores.keys()) or "undisclosed risks"
        title = "NOTICE OF CLOUDED TITLE AND ADVERSE CLAIM"
        body = (
            f"This notice is filed pursuant to applicable adverse claim doctrine.\n\n"
            f"DETECTION: {result.template_name}\n"
            f"Severity: {result.severity.value.upper()}\n"
            f"Confidence: {result.score:.0%}\n\n"
            f"DEFECT IN TITLE:\n"
            f"The following indicators of compromised title have been identified: "
            f"{signals}.\n\n"
            f"MATERIAL RISK:\n"
            f"Any investment or extraction activity proceeding under the above "
            f"conditions carries material legal risk that must be disclosed to "
            f"investors, partners, and regulatory bodies under SEC Regulation S-K "
            f"Item 103 (Legal Proceedings) and Item 105 (Risk Factors).\n\n"
            f"CAUTIONARY NOTICE:\n"
            f"Failure to disclose the above risks may constitute a violation of "
            f"Rule 10b-5 (Securities Fraud) and trigger liability under the EU "
            f"Corporate Sustainability Due Diligence Directive (CSDDD)."
        )
        return title, body

    @staticmethod
    def _fiduciary_liability(result: DetectionResult) -> tuple[str, str]:
        signals = ", ".join(result.signal_scores.keys()) or "undisclosed risks"
        title = "FIDUCIARY LIABILITY NOTICE"
        body = (
            f"RE: Potential Breach of Fiduciary Duty - ERISA Section 404(a)(1)(B)\n\n"
            f"DETECTION: {result.template_name}\n"
            f"Severity: {result.severity.value.upper()}\n"
            f"Confidence: {result.score:.0%}\n\n"
            f"UNDISCLOSED RISKS:\n"
            f"The following material risks have been identified in portfolio "
            f"holdings: {signals}.\n\n"
            f"FIDUCIARY OBLIGATION:\n"
            f"Under ERISA Section 404(a)(1)(B), fiduciaries must act with the "
            f"care, skill, prudence, and diligence that a prudent person would "
            f"exercise. Continued investment in entities with the above risk "
            f"profile without disclosure may constitute a breach of this duty.\n\n"
            f"ESG COMPLIANCE:\n"
            f"The identified risks implicate environmental, social, and governance "
            f"mandates applicable to institutional investors. Immediate review of "
            f"affected holdings is recommended."
        )
        return title, body

    @staticmethod
    def _shareholder_letter(result: DetectionResult) -> tuple[str, str]:
        signals = ", ".join(result.signal_scores.keys()) or "undisclosed risks"
        title = "SHAREHOLDER DISCLOSURE LETTER"
        body = (
            f"RE: Material Risk Disclosure - SEC Regulation S-K\n\n"
            f"DETECTION: {result.template_name}\n"
            f"Severity: {result.severity.value.upper()}\n"
            f"Confidence: {result.score:.0%}\n\n"
            f"DISCLOSURE REQUIREMENT:\n"
            f"The following material risks require disclosure under SEC Item 103 "
            f"(Legal Proceedings) and Item 105 (Risk Factors): {signals}.\n\n"
            f"This letter serves as formal notice that the undersigned has "
            f"identified indicators of undisclosed material risk in the entity's "
            f"operations. Failure to address these disclosures may expose the "
            f"entity and its officers to liability under Rule 10b-5."
        )
        return title, body

    @staticmethod
    def _press_release(result: DetectionResult) -> tuple[str, str]:
        signals = ", ".join(result.signal_scores.keys()) or "emerging concerns"
        title = "FOR IMMEDIATE RELEASE"
        body = (
            f"SUBJECT: {result.template_name}\n\n"
            f"An analysis of publicly available information has identified "
            f"indicators of {result.threat_type.value.replace('_', ' ')} "
            f"affecting indigenous communities.\n\n"
            f"KEY FINDINGS:\n"
            f"Detection confidence: {result.score:.0%} "
            f"(severity: {result.severity.value})\n"
            f"Indicators identified: {signals}\n\n"
            f"BACKGROUND:\n"
            f"International legal frameworks including the UN Declaration on the "
            f"Rights of Indigenous Peoples (UNDRIP) and the principle of Free, "
            f"Prior and Informed Consent (FPIC) establish clear obligations "
            f"regarding indigenous territorial rights. The identified indicators "
            f"suggest these obligations may not be met.\n\n"
            f"Contact information and supporting documentation available on request."
        )
        return title, body
