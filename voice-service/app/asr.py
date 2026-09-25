import whisper

print("Loading ASR (speech recognition) model... (this may take a minute the first time)")

model = whisper.load_model("base")

print("ASR model loaded successfully!")

LANG_NAME_TO_CODE = {
    "hindi": "hi", "marathi": "mr", "tamil": "ta",
    "telugu": "te", "kannada": "kn", "bengali": "bn", "gujarati": "gu"
}
LANG_CODE_TO_NAME = {v: k for k, v in LANG_NAME_TO_CODE.items()}

def transcribe_audio(audio_path: str, expected_language: str = None) -> dict:
    """
    Transcribes audio, auto-detecting the spoken language.
    Compares against expected_language (what the user selected) to catch mismatches.
    Returns: {"text": ..., "detected_language": ..., "warning": None/"unclear_audio"/"language_mismatch"}
    """
    result = model.transcribe(audio_path)
    detected_code = result.get("language")
    detected_name = LANG_CODE_TO_NAME.get(detected_code, detected_code)
    text = result["text"].strip()

    warning = None
    if not text or len(text) < 2:
        warning = "unclear_audio"
    elif expected_language and detected_name != expected_language.lower():
        warning = "language_mismatch"

    return {
        "text": text,
        "detected_language": detected_name,
        "warning": warning
    }

# Quick test when this file is run directly
if __name__ == "__main__":
    test_file = "test_outputs/hindi_output.wav"
    result = transcribe_audio(test_file, expected_language="hindi")
    print(f"Transcribed text: {result['text']}")
    print(f"Detected language: {result['detected_language']}")
    print(f"Warning: {result['warning']}")