from app.translate import translate_text
from app.tts import synthesize_speech
import os

os.makedirs("test_outputs", exist_ok=True)

sample_text = "Wear safety gloves before starting the procedure."

languages = ["hindi", "marathi", "tamil", "telugu", "kannada", "bengali", "gujarati"]

for lang in languages:
    print(f"\n--- {lang.upper()} ---")
    translated = translate_text(sample_text, lang)
    print(f"Translated: {translated}")
    
    output_path = f"test_outputs/{lang}_output.wav"
    synthesize_speech(translated, lang, output_path)
    print(f"Audio saved: {output_path}")

print("\nAll languages tested successfully!")