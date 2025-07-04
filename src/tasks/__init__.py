"""Initializes the tasks package for the healthcare AI agent system.

This module aggregates all specialized task classes from the `tasks` package,
making them easily accessible for use in defining agent workflows (crews).
Each task class represents a specific, self-contained unit of work that an
agent can execute.
"""

from .assess_language_task import AssessPatientLanguageTask
from .extract_clinical_task import ExtractClinicalInfoTask
from .preprocess_task import PreprocessMedicalTextTask
from .quality_control_task import QualityControlTask
from .summarize_task import GenerateSummaryTask


__all__ = [
    "AssessPatientLanguageTask",
    "ExtractClinicalInfoTask",
    "PreprocessMedicalTextTask",
    "QualityControlTask",
    "GenerateSummaryTask",
]
