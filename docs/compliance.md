# Compliance Considerations (GGZ / Healthcare Context)

This is a proof-of-concept system using mocked data and no real patient
information. It is **not** compliant or certified for production use in
healthcare — the notes below describe how the architecture anticipates the
relevant frameworks, not a claim that those frameworks are satisfied today.

## Frameworks relevant to this domain

- **AVG (GDPR)**: patient conversations and derived data (transcripts,
  extracted clinical info, summaries) are special-category health data under
  Art. 9 GDPR. Any real deployment needs an explicit legal basis, data
  minimization, and a documented retention policy.
- **NEN 7510 / 7512 / 7513**: the Dutch information security, secure data
  exchange, and logging/accountability standards for healthcare information
  systems. NEN 7510 in particular expects a documented ISMS (risk
  assessment, access control, incident handling) around a system like this
  one — not just secure code.
- **Medisch beroepsgeheim**: professional confidentiality applies to the
  treating clinician, not to the tooling. A system that surfaces AI-generated
  content to a clinician must make clear that the clinician remains
  responsible for what goes in the record — reflected here in
  `quality_check.requires_human_review` (see below).
- **Verwerkersovereenkomst / subverwerkersovereenkomst**: any third-party
  processor in the pipeline (an LLM API, a transcription API, cloud hosting)
  needs a data processing agreement, and its subprocessors need one in turn.
  `src/llm/llm_factory.py` and `src/transcription/openai_whisper.py` currently
  call OpenAI directly with no such agreement in place — fine for a demo with
  synthetic text, not acceptable for real patient data.

## Where the architecture already anticipates this

- **Mandatory human review is structural, not optional.** `QualityControlTask`
  (`src/tasks/quality_control_task.py`) always returns a
  `requires_human_review` flag; nothing in the pipeline marks a report as
  final without it. This is the direct analogue of "verplichte menselijke
  beoordeling" in the job description.
- **Provider abstraction isolates the compliance-sensitive boundary.**
  `BaseLLM` (`src/llm/base.py`) and `TranscriptionService`
  (`src/transcription/base.py`) mean the actual processor — OpenAI today,
  potentially AWS Bedrock / AWS Transcribe in `eu-central-1` for a real
  deployment — is a swappable implementation behind one interface, not
  something wired through the whole codebase. Moving to a processor covered
  by a signed agreement is a new class, not a rewrite.
- **Audit logging is a first-class step, not an afterthought.**
  `QualityControlTask` logs every quality-control event via
  `logger.log_audit_event` (see `src/tools/logging_tools.py`,
  `src/tools/database_interface.py`), which is the kind of accountability
  trail NEN 7513 expects — currently backed by a mock/in-memory
  implementation, but behind the same `HealthcareDatabase` interface a real
  audit store would use.

## What's genuinely missing

- No multi-tenant isolation model (single-tenant PoC).
- No AWS deployment (local/dev only).
- No signed data processing agreements with the LLM/transcription providers
  in use here — do not run real patient data through this code as-is.
- No formal risk assessment or ISMS documentation (NEN 7510 is an
  organizational standard as much as a technical one).
