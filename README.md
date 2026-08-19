# ABC Prospect

An internal commercial prospecting application built with FastAPI and PostgreSQL.

## Project Overview

ABC Prospect brings company research, qualification and follow-up into one controlled workflow. It helps identify organizations with strong reputations but weak digital presence, while keeping commercial decisions and AI-assisted content under human review.

The project is an internal tool, not a public SaaS product or an automated outreach platform.

## Problem It Solves

Manual prospecting spreads evidence across searches, notes and disconnected contact records. ABC Prospect centralizes this information, makes prioritization explainable and preserves an audit trail for important actions.

## Features

- Authenticated internal access
- Company and contact management
- Search, filtering and duplicate review
- Commercial pipeline and activity history
- Versioned, explainable opportunity scoring
- Google Places integration with explicit human confirmation
- Controlled website assessments
- AI-assisted commercial diagnostics and drafts
- Mandatory human review before approval
- Dashboard and manually triggered CSV export
- Audit records for sensitive workflows

The application does not scrape platforms, send bulk messages, publish generated content or make autonomous commercial decisions.

## Technology Stack

- Python and FastAPI
- PostgreSQL
- SQLAlchemy and Alembic
- pytest
- Docker and Docker Compose
- Jinja2, HTML, CSS and JavaScript
- Google Places API integration
- OpenAI Responses API adapter, disabled by default

## Architecture

ABC Prospect is a modular monolith with separate API, service, repository and persistence responsibilities. Database changes use a linear Alembic migration chain. External providers are behind adapters so tests can use deterministic fakes and integrations can remain disabled by default.

See [ARCHITECTURE.md](ARCHITECTURE.md), [DATA_MODEL.md](DATA_MODEL.md) and [docs/traceability.md](docs/traceability.md).

## Explainable Scoring and AI

Opportunity scores are versioned and retain their components so a reviewer can understand how a result was produced. Scores support prioritization but do not automate commercial decisions.

AI-assisted drafts use minimized business context, structured outputs and immutable history. Contact details, free-form notes and other unnecessary data are excluded from provider context. Generated material must be reviewed, edited and explicitly approved by a person; the system never sends it automatically.

## Security

- Password hashing and authenticated sessions
- Restrictive production configuration
- Defensive HTTP headers and readiness checks
- External integrations disabled unless explicitly configured
- Environment-based secrets outside source control
- Rate and usage controls for AI-assisted operations
- Auditability for exports and generated content
- Non-root production container configuration

See [SECURITY.md](SECURITY.md) and the public policy documents under `docs/`.

## Testing

The test suite covers domain rules, authentication, search, duplicate handling, scoring, pipeline transitions, provider adapters, AI safeguards, reporting and database behavior. PostgreSQL and Alembic integration checks complement unit and functional tests.

```bash
pytest
```

## Current Status

- Core internal workflow and operational software preparation are implemented and validated.
- The commercial-validation protocol and supporting instrumentation are ready.
- A real pilot, user feedback and the final product decision remain pending.
- Production deployment has not been performed.

The repository deliberately avoids presenting a completion percentage as a substitute for these remaining real-world validation steps.

## Key Lessons Learned

- Explainability is essential when software supports prioritization.
- AI-generated content needs minimized context, explicit review and an immutable history.
- External search results should remain provisional until a person confirms them.
- Audit trails matter for exports, merges and commercial-content decisions.
- Operational readiness and real-world product validation are different milestones.

## Documentation

- [Roadmap](ROADMAP.md)
- [Project context](PROJECT_CONTEXT.md)
- [Business rules](docs/business_rules.md)
- [Testing](docs/testing.md)
- [Commercial validation protocol](docs/sprint-15-commercial-validation.md)
