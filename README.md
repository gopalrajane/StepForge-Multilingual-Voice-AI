# StepForge — Multilingual Voice AI

A voice-powered multilingual assistant service for **StepForge3D**. It translates English technical instructions (audio or text) into spoken Indian languages, while protecting technical terms — part numbers, bolt sizes, torque values — from being mistranslated.

## Features

- **Speech-to-speech** (`/speech-to-speech`): upload spoken audio (or video with audio) → transcribe → translate → return spoken audio in the target language
- **Text-to-speech** (`/generate-audio`): English text → translated speech, with response caching (identical text+language requests reuse saved audio)
- **Text translation** (`/translate`): English → Hindi, Marathi, Tamil, Telugu, Kannada, Bengali, or Gujarati
- **Glossary protection**: technical terms (`M8`, `25 Nm`, `ABC-123`, "torque wrench"…) are masked with placeholders before translation and restored afterwards, using per-language preferred glossary translations
- **Language mismatch detection**: Whisper auto-detects the spoken language and returns a clear warning if the user selected the wrong one — instead of producing garbled output
- **Unclear audio detection** for low-quality input

## Tech stack

- **Backend:** FastAPI + Uvicorn
- **ASR:** OpenAI Whisper (`base`)
- **Translation:** `facebook/nllb-200-distilled-600M` (NLLB-200)
- **TTS:** Facebook MMS-TTS (per-language VITS checkpoints)
- **Frontend:** lightweight browser demo (`frontend-hook/index.html`)

## Architecture

```
Audio/Text input
      │
      ▼
  [Whisper ASR] ──► language check (mismatch → clear warning)
      │
      ▼
[Glossary protection] ── mask part numbers, units, technical terms
      │
      ▼
[NLLB-200 translation] ── English → target Indian language
      │
      ▼
[Glossary restoration] ── restore terms with per-language glossary words
      │
      ▼
   [MMS-TTS] ──► spoken audio (.wav)
```

## Setup

Requires Python 3.9+ and ~4 GB free disk space (models download on first run).

```bash
cd voice-service
pip install -r requirements.txt
pip install openai-whisper
uvicorn app.main:app --reload
```

The frontend demo is a single self-contained HTML page: open `frontend-hook/index.html` in any browser, point it at the running API, and start speaking.

## Project structure

```
├── frontend-hook/            # browser demo UI (single HTML page)
└── voice-service/
    ├── app/
    │   ├── main.py          # FastAPI routes (/translate, /synthesize, /generate-audio, /speech-to-speech)
    │   ├── asr.py           # Whisper speech recognition + language mismatch detection
    │   ├── translate.py     # NLLB-200 translation with glossary protection
    │   ├── glossary.py      # technical-term glossary + protect/restore logic
    │   ├── tts.py           # MMS-TTS speech synthesis (per-language, cached)
    │   └── test_all_languages.py
    └── requirements.txt
```

## Roadmap

- [ ] Add `ffmpeg` setup note for video/audio decoding
- [ ] Unit tests for the glossary protect/restore cycle
- [ ] Docker setup for one-command deployment
- [ ] Support for more Indian languages
