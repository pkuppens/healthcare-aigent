# System Architecture

## Component Diagram
```mermaid
graph TD
    subgraph Frontend
        UI[Web Interface]
        API[API Gateway]
    end

    subgraph Backend
        subgraph AS[CrewAI System]
            subgraph Crews
                PA[Preprocessing Crew]
                LA[Language Assessment Crew]
                CA[Clinical Extraction Crew]
                SA[Summarization Crew]
                QA[Quality Control Crew]
            end

            subgraph Flows
                DP[Data Processing Flow]
                AL[Audit Logging Flow]
                DB[Database Operations Flow]
            end
        end

        subgraph LLML[LLM Layer]
            LLMF[LLM Factory]
            OLL[Ollama LLM]
            OAI[OpenAI LLM]
        end

        subgraph Tools
            DB[(Database)]
            WS[Web Search]
            AL[Audit Log]
        end
    end

    UI --> API
    API --> AS
    AS --> LLML
    AS --> Tools
    LLMF --> OLL
    LLMF --> OAI
```

## Class Diagram
```mermaid
classDiagram
    class HealthcareDatabase {
        <<interface>>
        +read_patient_data(patient_id: str) Dict[str, Any]
        +update_patient_data(patient_id: str, data: Dict[str, Any]) bool
        +log_audit_event(event_type: str, patient_id: str, user_id: str) bool
    }

    class MockHealthcareDatabase {
        -_patient_data: Dict
        -_audit_log: List
        +read_patient_data(patient_id: str) Dict[str, Any]
        +update_patient_data(patient_id: str, data: Dict[str, Any]) bool
        +log_audit_event(event_type: str, patient_id: str, user_id: str) bool
    }

    class LLMFactory {
        <<static>>
        +create_llm(llm_type: LLMType) LLM
        +get_llm_for_task(task_type: str, sensitive_data: bool) LLM
    }

    class Agent {
        <<abstract>>
        -role: str
        -goal: str
        -backstory: str
        -tools: List[Tool]
        +execute_task(task: Task) Result
    }

    class PreprocessingAgent {
        +execute_task(task: Task) Result
    }

    class LanguageAssessmentAgent {
        +execute_task(task: Task) Result
    }

    class ClinicalExtractionAgent {
        +execute_task(task: Task) Result
    }

    class SummarizationAgent {
        +execute_task(task: Task) Result
    }

    class QualityControlAgent {
        +execute_task(task: Task) Result
    }

    HealthcareDatabase <|.. MockHealthcareDatabase
    Agent <|-- PreprocessingAgent
    Agent <|-- LanguageAssessmentAgent
    Agent <|-- ClinicalExtractionAgent
    Agent <|-- SummarizationAgent
    Agent <|-- QualityControlAgent
```

## Sequence Diagram
```mermaid
sequenceDiagram
    participant UI as Web Interface
    participant API as API Gateway
    participant PA as Preprocessing Agent
    participant LA as Language Assessment Agent
    participant CA as Clinical Extraction Agent
    participant SA as Summarization Agent
    participant QA as Quality Control Agent
    participant DB as Database
    participant LLM as LLM Factory

    UI->>API: Submit Medical Conversation
    API->>PA: Process Text
    PA->>LLM: Request Context Analysis
    LLM-->>PA: Return Context
    PA->>LA: Assess Language & Literacy
    LA->>LLM: Request Assessment
    LLM-->>LA: Return Assessment
    LA->>CA: Extract Clinical Info
    CA->>LLM: Request Extraction
    LLM-->>CA: Return Clinical Data
    CA->>SA: Create Summary
    SA->>LLM: Request Summarization
    LLM-->>SA: Return Summary
    SA->>QA: Verify Quality
    QA->>DB: Update Records
    QA-->>API: Return Results
    API-->>UI: Display Results
```

## Component Descriptions

### Frontend Components
- **Web Interface**: User-facing application for submitting medical conversations and viewing results
- **API Gateway**: Handles authentication, request routing, and response formatting

### Backend Components
- **CrewAI System**: Core orchestration layer managing agents and workflows
  - **Crews**: Autonomous agent teams for complex tasks
  - **Flows**: Structured processes for deterministic operations
- **LLM Layer**: Language model management and selection
- **Tools**: External service integrations and utilities

### Data Flow
1. Medical conversations enter through the Web Interface
2. API Gateway validates and routes requests
3. CrewAI System processes the conversation through specialized agents
4. Results are stored in the database and returned to the user 