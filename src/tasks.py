"""Task definitions for the healthcare multi-agent system."""

from crewai import Task

from .agents import (
    clinical_extractor_agent,
    patient_language_agent,
    preprocessing_agent,
    quality_control_agent,
    summarization_agent,
)

# Define tasks
task_preprocess = Task(
    description=(
        "Analyseer de transcriptie: identificeer Spreker A (professional) en "
        "Spreker B (patiënt), bepaal het type gesprek. Geef de geannoteerde "
        "transcriptie door."
    ),
    agent=preprocessing_agent,
)


task_assess_language = Task(
    description=(
        "Analyseer de uitingen van Spreker B (patiënt) uit de geannoteerde "
        "transcriptie. Schat de medische geletterdheid in (laag/gemiddeld/hoog) "
        "en identificeer de taal. Geef deze inschatting door."
    ),
    agent=patient_language_agent,
    context=[task_preprocess],
)


task_extract_info = Task(
    description=(
        "Extraheer alle relevante klinische informatie (symptomen, diagnoses, "
        "medicatie, etc.) uit de transcriptie. Gebruik de patiënt database tool "
        "indien een ID beschikbaar is. Verifieer eventueel medicatie met de web "
        "search tool. Geef de gestructureerde extracties door."
    ),
    agent=clinical_extractor_agent,
    context=[task_preprocess],
)


task_summarize_soap = Task(
    description=(
        "Genereer een SOAP-notitie gebaseerd op de transcriptie en de "
        "geëxtraheerde klinische informatie. Zorg voor een professionele toon."
    ),
    agent=summarization_agent,
    context=[task_preprocess, task_extract_info],
)


task_summarize_patient = Task(
    description=(
        "Genereer een eenvoudige samenvatting (B1-niveau) van de belangrijkste "
        "punten en aanbevelingen voor de patiënt, rekening houdend met de "
        "ingeschatte taal/geletterdheid. Gebruik de transcriptie en "
        "geëxtraheerde info."
    ),
    agent=summarization_agent,
    context=[task_preprocess, task_assess_language, task_extract_info],
)


task_quality_check_and_propose_update = Task(
    description=(
        "Controleer de geëxtraheerde informatie en de SOAP-notitie op "
        "consistentie en volledigheid. Bereid een voorstel voor om de nieuwe "
        "diagnose/medicatie bij te werken in het EPD via de database update tool. "
        "Log deze actie."
    ),
    agent=quality_control_agent,
    context=[task_extract_info, task_summarize_soap],
)
