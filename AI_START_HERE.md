# PLDA — AI START HERE

## Purpose

PLDA is a multi-agent legal research AI system.

The repository is the primary handover point for continuing development
with another AI or on another device.

## FIRST STEPS FOR ANY AI

Before changing code:

1. Read `AGENTS.md`.
2. Read `AI_CONTEXT.md`.
3. Read `PROJECT_STATUS.md`.
4. Read `CONTRIBUTING.md`.
5. Read relevant files in `docs/`.
6. Inspect the current Git status and recent commits.
7. Inspect the actual implementation before making assumptions.

## IMPORTANT RULE

Do not assume that a file existing means that its functionality is complete.

Verify:
- implementation;
- callers;
- dependencies;
- database usage;
- tests;
- actual runtime behavior.

## LEGAL RESEARCH PRINCIPLES

PLDA must:

- identify jurisdiction;
- identify the relevant date;
- prefer primary official legal sources;
- distinguish binding law from soft law;
- verify legal sources;
- track source versions and effective dates;
- cite important conclusions;
- distinguish facts from assumptions;
- preserve uncertainty;
- preserve counterarguments;
- never invent legal authority.

## MVP

Initial target:

- 1–2 jurisdictions;
- 5–7 specialized agents;
- CONSULTATION mode;
- CASE mode;
- primary official sources;
- Source Verification;
- Law Timeline.

Additional functionality must be added incrementally.

## CURRENT IMPLEMENTATION

The project already contains a Python core and SQLite database.

Core modules include functionality for:

- case analysis;
- research planning;
- intent analysis;
- jurisdiction;
- legal repository;
- sources;
- source verification;
- evidence;
- legal conflicts;
- law timeline;
- international rights;
- constitutional limits;
- research modes;
- research storage;
- document ingestion;
- police law;
- tax law;
- opportunity analysis.

Database:

`database/plda.db`

Do not replace the database or core architecture without first inspecting
the existing implementation.

## SOURCE VERIFICATION

An unverified document must not be treated as a confirmed legal norm.

Where available, record:

- source identity;
- issuing institution;
- jurisdiction;
- date;
- effective status;
- version;
- official URL;
- SHA-256 hash;
- article/paragraph/section.

## DEVELOPMENT RULES

Make small, reversible changes.

Before modifying a subsystem:

1. inspect the existing code;
2. identify its callers;
3. inspect database dependencies;
4. inspect tests;
5. determine actual behavior;
6. make the smallest useful change;
7. run available checks;
8. update documentation;
9. commit the change.

Never delete or replace working code merely to create a cleaner architecture.

## SECURITY

Never commit:

- API keys;
- passwords;
- access tokens;
- private credentials;
- private case data.

Use environment variables and configuration templates.

## PORTABILITY

The project must remain recoverable from GitHub.

Another AI should be able to reconstruct the project by reading:

- `AI_START_HERE.md`
- `AGENTS.md`
- `AI_CONTEXT.md`
- `PROJECT_STATUS.md`
- `CONTRIBUTING.md`
- `README.md`
- `docs/`

## HANDOVER

When ending a development session:

1. update `PROJECT_STATUS.md` if necessary;
2. document incomplete work;
3. run tests/checks;
4. check `git status`;
5. commit important changes;
6. push to GitHub when appropriate.

## DO NOT GUESS

If information is missing, inspect the repository first.

If functionality is not verified, describe it as unverified.

If a legal source cannot be confirmed, do not present it as established law.

