"""Agent definitions for the healthcare multi-agent system."""

from crewai import Agent

from .llm_config import get_llm
from .tools.database_tools import propose_database_update, read_patient_data
from .tools.logging_tools import log_audit_event
from .tools.web_tools import search_web_mock

# Initialize LLM
llm = get_llm()

# Initialize tools
db_reader_tool = read_patient_data
db_update_tool = propose_database_update
web_search_tool = search_web_mock
audit_log_tool = log_audit_event


# Define agents
preprocessing_agent = Agent(
    role="Pre-processing Specialist",
    goal="Clean and analyze medical transcripts, identify speakers and context",
    backstory=(
        "You are an expert in medical transcription analysis with years of "
        "experience in processing healthcare conversations. Your expertise lies "
        "in identifying key speakers, medical terminology, and conversation context."
    ),
    tools=[audit_log_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


patient_language_agent = Agent(
    role="Patient Communication Analyst",
    goal="Assess patient language proficiency and medical literacy",
    backstory=(
        "You specialize in analyzing patient communication patterns and "
        "determining appropriate language levels for medical information. "
        "Your expertise helps ensure patients receive information they can understand."
    ),
    tools=[audit_log_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


clinical_extractor_agent = Agent(
    role="Clinical Information Specialist",
    goal="Extract and validate medical information from conversations",
    backstory=(
        "You are a medical professional with expertise in extracting and "
        "validating clinical information from patient interactions. You "
        "ensure accurate recording of symptoms, diagnoses, and treatments."
    ),
    tools=[db_reader_tool, web_search_tool, audit_log_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


summarization_agent = Agent(
    role="Medical Documentation Specialist",
    goal="Create structured medical summaries and patient-friendly explanations",
    backstory=(
        "You are an expert in medical documentation with extensive experience "
        "in creating both professional medical records (SOAP notes) and "
        "patient-friendly summaries. You ensure information is accurate and "
        "appropriately formatted for different audiences."
    ),
    tools=[audit_log_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


quality_control_agent = Agent(
    role="Quality Assurance Specialist",
    goal="Ensure accuracy and completeness of medical information",
    backstory=(
        "You are a senior medical professional responsible for quality control "
        "in healthcare documentation. Your expertise ensures that all medical "
        "information is accurate, complete, and properly recorded."
    ),
    tools=[db_update_tool, audit_log_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)
