# SpeakerVerse: Real-Time Audio Diarization & Transcription Pipeline

This is a partial and simplified implementation of the speech part of the healthcare aigent.

## Project Description

SpeakerVerse is a Python program that analyzes audio recordings.
It identifies who is speaking and what they are saying. The program uses advanced technologies like
Whisper for converting speech to text and PyAnnote.audio for separating different speakers.
This project aims to create a working pipeline that can be used locally on computers with powerful
graphics cards (NVIDIA RTX 3090/4090/5090, etc.). We want to make it easy to use and deploy.

## Work Breakdown

This project is divided into the following stages:

* **Phase 1: Core Pipeline Development (Estimated 2-3 Days)**
    * Implement audio transcription using Whisper.
    * Integrate PyAnnote.audio for speaker diarization.
    * Create a basic data pipeline to connect transcription and diarization.
    * Apply LLMs to the resulting texts for error detection and summarization.
* **Phase 2: API Development (Estimated 1-2 Days)**
    * Design and implement a RESTful API using FastAPI.
    * Define API endpoints for uploading audio and retrieving results.
    * Implement error handling and validation.
* **Phase 3: Optimization & Testing (Estimated 1-2 Days)**
    * Optimize the pipeline for performance on NVIDIA GPUs.
    * Write unit and integration tests using pytest.
    * Document the API and pipeline architecture.

## Technology & Architecture Decisions

* **Programming Language:** Python (because of its many useful libraries)
* **ASR (Automatic Speech Recognition):** Whisper (high accuracy and can run locally on GPUs)
* **Diarization:** PyAnnote.audio (a powerful tool for separating different speakers in audio)
* **API Framework:** FastAPI (used to create a web interface for the pipeline)

## Trade-offs

* We are focusing on a local setup to have more control and speed
* This means we will need a computer with a good graphics card
* We may explore cloud deployment later
* Cloud deployment also introduces privacy concerns

## Task List

### Core Pipeline Development

    - [ ] Implement audio transcription using Whisper
    - [ ] Integrate PyAnnote.audio for speaker diarization
    - [ ] Create a Python script that passes audio data from Whisper to PyAnnote.audio and get the results
    - [ ] Pass the annotated text to a LLM model to catch annotation errors
    - [ ] Pass the annotated text to a LLM that summarizes the text
    - [ ] Test the end-to-end pipeline with a simple audio file

### API Development

    - [ ] Define API endpoints (Upload, Process, Results)
    - [ ] Implement audio file upload endpoint
    - [ ] Implement pipeline execution endpoint
    - [ ] Implement results retrieval endpoint
    - [ ] Test the API with integration tests

### Optimization & Testing

    - [ ] Profile pipeline performance
    - [ ] Optimize pipeline for GPU utilization
    - [ ] Write unit tests for core components
    - [ ] Write integration tests for end-to-end pipeline
    - [ ] Document API endpoints and usage

### Containerization & Deployment

    - [ ] Create Dockerfile for building pipeline image
    - [ ] Build Docker image
    - [ ] Test Docker image locally
    - [ ] Write documentation (README.md)
    - [ ] Push Docker image to Docker Hub (Optional)

## License

This project is licensed under the [MIT License](LICENSE).

