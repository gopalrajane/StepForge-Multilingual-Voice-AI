from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from app.translate import translate_text
from app.tts import synthesize_speech
from app.asr import transcribe_audio
import uuid
import os
import shutil
import hashlib

app = FastAPI(title="StepForge3D Voice Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("generated_audio", exist_ok=True)
os.makedirs("uploaded_audio", exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "StepForge3D Voice Service is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hindi"

@app.post("/translate")
def translate(request: TranslateRequest):
    translated = translate_text(request.text, request.target_lang)
    return {
        "original_text": request.text,
        "target_lang": request.target_lang,
        "translated_text": translated
    }

class SynthesizeRequest(BaseModel):
    text: str
    language: str = "hindi"

@app.post("/synthesize")
def synthesize(request: SynthesizeRequest):
    filename = f"audio_{uuid.uuid4().hex}.wav"
    output_path = os.path.join("generated_audio", filename)
    synthesize_speech(request.text, request.language, output_path)
    return FileResponse(output_path, media_type="audio/wav", filename=filename)

class GenerateAudioRequest(BaseModel):
    text: str
    target_lang: str = "hindi"

def _cache_key(text: str, target_lang: str) -> str:
    raw = f"{text.strip().lower()}|{target_lang.lower()}"
    return hashlib.md5(raw.encode()).hexdigest()

@app.post("/generate-audio")
def generate_audio(request: GenerateAudioRequest):
    """
    Pipeline B: English text -> translated text -> spoken audio
    Cached: identical text+language requests reuse the saved file.
    """
    cache_id = _cache_key(request.text, request.target_lang)
    cached_path = os.path.join("generated_audio", f"cache_{cache_id}.wav")

    if os.path.exists(cached_path):
        return FileResponse(cached_path, media_type="audio/wav", filename=f"cache_{cache_id}.wav")

    translated_text = translate_text(request.text, request.target_lang)
    synthesize_speech(translated_text, request.target_lang, cached_path)

    return FileResponse(cached_path, media_type="audio/wav", filename=f"cache_{cache_id}.wav")


@app.post("/speech-to-speech")
def speech_to_speech(
    audio: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    """
    Pipeline A: spoken audio (or video with audio) -> translated spoken audio.
    Accepts audio files, video files, or live recordings.
    Auto-detects the spoken language and compares it to the user's selection,
    returning a clear warning instead of garbled output if they don't match.
    """
    # Keep the original file extension so ffmpeg/Whisper reads it correctly
    original_ext = os.path.splitext(audio.filename)[1] or ".wav"
    input_path = os.path.join("uploaded_audio", f"input_{uuid.uuid4().hex}{original_ext}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    transcription = transcribe_audio(input_path, expected_language=source_lang)

    if transcription["warning"] == "unclear_audio":
        return JSONResponse(status_code=400, content={
            "error": "unclear_audio",
            "message": "We couldn't understand the audio clearly. Please speak clearly and try again."
        })

    if transcription["warning"] == "language_mismatch":
        return JSONResponse(status_code=400, content={
            "error": "language_mismatch",
            "message": f"It sounds like you spoke {transcription['detected_language']}, but you selected {source_lang}. Please select the correct language and try again.",
            "detected_language": transcription["detected_language"]
        })

    recognized_text = transcription["text"]
    translated_text = translate_text(recognized_text, target_lang)

    output_filename = f"speech_{uuid.uuid4().hex}.wav"
    output_path = os.path.join("generated_audio", output_filename)
    synthesize_speech(translated_text, target_lang, output_path)

    return FileResponse(output_path, media_type="audio/wav", filename=output_filename)