from dataclasses import dataclass, field
from typing import List, Optional


EVENT_TYPES = {
    "adopted",
    "amended",
    "entered_into_force",
    "suspended",
    "restored",
    "repealed",
    "expired",
    "court_review",
}


@dataclass
class LawEvent:
    event_id: str
    law_id: str
    event_type: str
    event_date: str
    effective_date: Optional[str] = None
    title: str = ""
    description: str = ""
    source_url: Optional[str] = None
    source_reference: Optional[str] = None


@dataclass
class LawTimeline:
    law_id: str
    title: str
    jurisdiction: str
    original_date: Optional[str] = None
    events: List[LawEvent] = field(default_factory=list)


def validate_event(event: LawEvent) -> None:
    if event.event_type not in EVENT_TYPES:
        raise ValueError(
            f"Unknown event type: {event.event_type}"
        )


def add_event(
    timeline: LawTimeline,
    event: LawEvent,
) -> LawTimeline:

    validate_event(event)

    if event.law_id != timeline.law_id:
        raise ValueError(
            "Event law_id does not match timeline."
        )

    timeline.events.append(event)

    timeline.events.sort(
        key=lambda item: (
            item.event_date,
            item.effective_date or "",
        )
    )

    return timeline


def count_amendments(
    timeline: LawTimeline,
) -> int:

    return sum(
        event.event_type == "amended"
        for event in timeline.events
    )


def events_during_period(
    timeline: LawTimeline,
    start_date: str,
    end_date: str,
) -> List[LawEvent]:

    return [
        event
        for event in timeline.events
        if start_date <= event.event_date <= end_date
    ]


def amendments_during_period(
    timeline: LawTimeline,
    start_date: str,
    end_date: str,
) -> List[LawEvent]:

    return [
        event
        for event in events_during_period(
            timeline,
            start_date,
            end_date,
        )
        if event.event_type == "amended"
    ]


def timeline_summary(
    timeline: LawTimeline,
) -> dict:

    return {
        "law_id": timeline.law_id,
        "title": timeline.title,
        "jurisdiction": timeline.jurisdiction,
        "original_date": timeline.original_date,
        "total_events": len(timeline.events),
        "total_amendments": count_amendments(timeline),
        "events": [
            {
                "event_id": event.event_id,
                "type": event.event_type,
                "event_date": event.event_date,
                "effective_date":
                    event.effective_date,
                "title": event.title,
                "source_reference":
                    event.source_reference,
            }
            for event in timeline.events
        ],
    }


def compare_periods(
    timeline: LawTimeline,
    before_start: str,
    before_end: str,
    after_start: str,
    after_end: str,
) -> dict:

    before = amendments_during_period(
        timeline,
        before_start,
        before_end,
    )

    after = amendments_during_period(
        timeline,
        after_start,
        after_end,
    )

    return {
        "before_period": {
            "start": before_start,
            "end": before_end,
            "amendments": len(before),
        },
        "after_period": {
            "start": after_start,
            "end": after_end,
            "amendments": len(after),
        },
        "difference": len(after) - len(before),
    }


def build_ukraine_martial_law_period() -> dict:
    return {
        "jurisdiction": "Ukraine",
        "start": "2022-02-24",
        "label": "Martial law period",
        "important_rule":
            "Do not treat martial law as an amendment "
            "to the Constitution.",
        "research_required": [
            "constitution",
            "martial_law_decrees",
            "statutes",
            "amendments",
            "court_decisions",
            "international_law",
        ],
    }
