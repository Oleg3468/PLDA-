from dataclasses import dataclass, field
from typing import List


CONFLICT_STATUSES = {
    "compatible",
    "potential_conflict",
    "requires_judicial_review",
    "not_applicable",
    "insufficient_evidence",
}


@dataclass
class LegalRule:
    rule_id: str
    title: str
    jurisdiction: str
    source_type: str
    text: str
    mandatory: bool = True


@dataclass
class ConflictFinding:
    national_rule: LegalRule
    international_rules: List[LegalRule] = field(default_factory=list)
    status: str = "insufficient_evidence"
    reasoning: str = ""
    issues_to_verify: List[str] = field(default_factory=list)


def validate_status(status: str) -> None:
    if status not in CONFLICT_STATUSES:
        raise ValueError(
            f"Unknown conflict status: {status}"
        )


def compare_rules(
    national_rule: LegalRule,
    international_rules: List[LegalRule],
    status: str,
    reasoning: str,
    issues_to_verify: List[str] = None,
) -> ConflictFinding:

    validate_status(status)

    return ConflictFinding(
        national_rule=national_rule,
        international_rules=international_rules,
        status=status,
        reasoning=reasoning,
        issues_to_verify=issues_to_verify or [],
    )


def needs_judicial_review(
    finding: ConflictFinding,
) -> bool:

    return finding.status in {
        "potential_conflict",
        "requires_judicial_review",
    }


def requires_more_evidence(
    finding: ConflictFinding,
) -> bool:

    return finding.status == "insufficient_evidence"


def finding_summary(
    finding: ConflictFinding,
) -> dict:

    return {
        "national_rule": {
            "id": finding.national_rule.rule_id,
            "title": finding.national_rule.title,
            "jurisdiction":
                finding.national_rule.jurisdiction,
            "source_type":
                finding.national_rule.source_type,
        },
        "international_rules": [
            {
                "id": rule.rule_id,
                "title": rule.title,
                "jurisdiction": rule.jurisdiction,
                "source_type": rule.source_type,
            }
            for rule in finding.international_rules
        ],
        "status": finding.status,
        "reasoning": finding.reasoning,
        "needs_judicial_review":
            needs_judicial_review(finding),
        "requires_more_evidence":
            requires_more_evidence(finding),
        "issues_to_verify":
            finding.issues_to_verify,
    }
