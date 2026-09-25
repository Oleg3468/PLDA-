# PLDA Project Status

This document describes the current implementation state.
File existence does not prove complete functionality.

## IMPLEMENTED / PRESENT IN CODE

### Core legal research
- case analysis
- intent analysis
- research planning
- jurisdiction handling
- legal repository
- source handling
- source verification
- evidence registry
- legal conflict handling
- law timeline
- international rights
- constitutional limits
- research modes
- research storage
- document ingestion

### Domain modules
- police-law engine
- tax engine
- opportunity analysis

### Database
SQLite database:
`database/plda.db`

Known legal structures include:
- legal_sources
- arguments
- research_history

## PARTIAL / REQUIRES VERIFICATION

The existence of a module does not establish that it is
production-ready or covers all jurisdictions.

These areas require functional verification:
- multi-agent orchestration
- source acquisition from live official databases
- national jurisdiction coverage
- international organization source coverage
- UN document retrieval
- court database retrieval
- document download policies
- consultation mode
- case mode
- complete citation generation
- source verification completeness
- legal version tracking completeness
- cross-agent disagreement handling
- automated testing
- external API integrations

## PLANNED

Potential future development:
- expanded jurisdiction packs
- specialized source agents
- UN-focused research agent
- court-law research agents
- stronger primary-source connectors
- machine-learning components
- broader automated testing
- production deployment
- multi-device setup automation

## IMPORTANT AI RULE

Do not claim that a feature is implemented merely because
a file or class with a related name exists.

Before modifying a subsystem:
1. Read the relevant source code.
2. Inspect its callers.
3. Inspect its database dependencies.
4. Check available tests.
5. Determine actual behavior.
6. Distinguish implemented behavior from planned behavior.

## LEGAL SAFETY

PLDA is a legal research system.

It must:
- identify jurisdiction;
- identify relevant date;
- prefer primary official sources;
- distinguish binding law from non-binding material;
- trace important conclusions to sources;
- distinguish facts from assumptions;
- preserve uncertainty;
- never invent legal authority;
- preserve relevant counterarguments and disagreements.

## PORTABILITY

The repository must eventually contain enough documentation
and configuration templates for another developer or AI system
to reconstruct the development environment.

Secrets must never be committed.
Private case data must not be committed unless explicitly intended.
