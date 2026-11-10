# StudyBridge — Course Notes Study Assistant

## Overview

StudyBridge is a proposed LLM study assistant for students reviewing their own course notes. It turns a question and selected notes into a concise, source-grounded explanation, with clear limits when the notes do not contain the answer.

> **Project status:** This repository currently contains only this README. StudyBridge is a project design, not a running application; the model integration, prompts, evaluation materials, and application structure below describe the intended implementation.

## Problem & Use Case

- **Problem:** Students may have trouble finding relevant material in long or fragmented course notes and turning it into a useful review explanation.
- **Who it helps:** Students studying from material they are permitted to use.
- **Use case:** A student selects or pastes course notes, asks a study question, and receives an explanation grounded in those notes for review.
- **Why an LLM:** An LLM can interpret questions phrased in different ways and summarize relevant passages conversationally. Source-grounding and an explicit “not found” response help limit unsupported answers.

## LLM Integration

- **Model/API/platform:** Intended initial target is OpenAI's API using `gpt-4o-mini`; this choice is not yet implemented or validated.
- **How integrated:** The planned application will send a question and relevant user-provided notes from a backend to the model API. API credentials must remain server-side.
- **Where used in workflow:** After input validation and note selection, the model generates a structured study response; the application will check that the response includes supporting references or an uncertainty statement before showing it.
- **Configuration:** The planned backend will read `OPENAI_API_KEY` and `OPENAI_MODEL` from environment variables, typically loaded from a local `.env` file. Do not commit `.env` or real credentials. Use `.env.example` to document variable names without secret values when implementation is added.

## Prompt & Instruction Strategy

The planned prompt design will use:

- **System instructions:** Act as a study aid; use only the supplied course notes for course-specific claims, cite the relevant note section, and say when the notes do not support an answer.
- **Prompt template:** Provide the student's question and selected notes in clearly separated fields. Ask for a direct answer, a short explanation, supporting references, and any uncertainty.
- **Few-shot examples:** None are currently defined. Examples may be added after evaluation to demonstrate grounded answers and appropriate abstention.
- **Structured output:** Return `answer`, `evidence`, and `limitations` fields so the application can display the response consistently.

Planned prompt and evaluation materials:

- `prompts/system_prompt.md` — system instructions and answer boundaries.
- `prompts/templates.md` — reusable question-and-notes templates.
- `appendix/prompt-testing.md` — evaluation cases, rubric, and selected outputs.

These files do not exist yet; this README records their intended roles.

## Additional Design Feature

**Context handling and evaluation:** StudyBridge is intended to answer from user-selected course notes rather than general model knowledge. A planned evaluation set will include answerable questions, questions with missing evidence, and ambiguous questions. Responses will be scored for evidence use, correctness relative to the notes, clarity, and appropriate uncertainty.

**Safety boundaries:** The assistant is for study and review, not a substitute for course staff or a source of authoritative academic advice. It should not invent citations or claim that unsupported material came from the notes. Users should avoid uploading sensitive personal information and follow their institution's rules on sharing course materials.

## System Workflow

1. The student submits a study question and permitted course notes.
2. The application validates the inputs and selects or prepares relevant note context.
3. The backend sends the question, context, and custom instructions to the configured LLM.
4. The application validates the expected response fields and checks for evidence or an explicit limitation.
5. The student receives the explanation, supporting note references, and caveats; unsupported questions should receive a clear statement that the notes do not provide an answer.

## Repository Structure

The repository currently contains only `README.md`. The following is the proposed structure as the project is implemented:

```text
.
├── src/                      # Application source code
├── prompts/                  # System prompts and templates
├── tests/                    # Test cases and evaluation scripts/materials
├── appendix/                 # Prompt/testing appendix and selected outputs
├── docs/                     # Project documentation and ethical reflection
├── assets/                   # Screenshots/demo materials
├── .env.example              # Required environment variables (no secrets)
└── README.md
```
