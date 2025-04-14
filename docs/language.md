# Language Use Guidelines for the Project

## Primary Language: English

All code, documentation, and communication in this project must be written in English. This includes, but is not limited to:

- Source code and inline comments  
- Test files and test documentation  
- Project documentation and README files  
- Commit messages  
- Issue and pull request descriptions  
- Agent interactions and AI assistant prompts  
- Log messages and error reporting

## Language Complexity Level

### Target Level: CEFR B2 (Upper Intermediate)

To ensure accessibility for all team members, including non-native English speakers:

- Aim for clear, professional language aligned with CEFR B2 standards  
- Prefer simple sentence structures over complex or nested clauses  
- Avoid unnecessarily formal, academic, or idiomatic expressions  
- Use active voice where appropriate  
- Break complex ideas into smaller, understandable parts

### Domain-Specific Terminology

While maintaining linguistic simplicity, domain-specific terms should be used where appropriate:

- **Healthcare and technical terminology** (e.g., “diarization”, “anomaly detection”) is acceptable and encouraged  
- When introducing such terms, provide brief inline explanations in parentheses  
  - Example: “The system uses diarization (speaker separation) to identify different voices in the recording”  
- Do not oversimplify technical terms with established, precise meanings in the field

## Exceptions for Test Data

Test data may contain Dutch-language content to reflect real-world use cases in Dutch healthcare. This includes:

- Simulated patient complaints and symptoms  
- Medical records and clinical documentation  
- Doctor’s notes and instructions  
- Patient-provider communication samples  
- Dutch healthcare-specific terminology

This exception applies only to test data and should not affect code comments, documentation, or system-level communication.

## Rationale

Adopting English as the primary project language supports the following goals:

1. **Consistency** – Promotes uniformity across all components and contributors  
2. **Accessibility** – Makes the project easier to understand and adopt globally  
3. **Maintainability** – Enables long-term maintenance by a broader developer base  
4. **Integration** – Simplifies the use of international tooling, libraries, and AI models

## Implementation Guidelines

When working with AI agents or assistants:

**Do:**

1. Communicate exclusively in English  
2. Write all prompts, instructions, and output handling in English  
3. Clearly mark and explain any use of Dutch test content, with its intended purpose  
4. Maintain B2-level clarity and structure  
5. Preserve domain-specific terminology with appropriate contextualization

**Don’t:**

- Don’t use Dutch in commit messages, comments, documentation, or system instructions  
- Don’t oversimplify technical language in a way that reduces clarity or changes meaning  
- Don’t introduce non-standard abbreviations or slang

## Final Note

This document serves as the authoritative reference for all language-related expectations in the project. All contributors are expected  
to follow these guidelines to ensure communication remains consistent, accessible, and professional.
