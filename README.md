# StepForge Multilingual Voice AI

A voice-processing prototype with a FastAPI service for speech transcription, text translation, and speech synthesis.

## Features

- Audio transcription
- Text translation
- Text-to-speech generation
- Combined translation and audio-generation workflow
- Generated-audio caching
- Browser-based interface

## Tech Stack

Python, FastAPI, Transformers, PyTorch, Torchaudio, and JavaScript.

## Project Structure

```text
StepForge-Multilingual-Voice-AI/
├── frontend-hook/
│   └── index.html
└── voice-service/
    ├── app/
    │   ├── asr.py
    │   ├── translate.py
    │   ├── tts.py
    │   └── main.py
    └── requirements.txt
```

## Run the Voice Service

```bash
cd voice-service
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API provides endpoints for health checks, transcription, translation, speech synthesis, and combined audio generation.

