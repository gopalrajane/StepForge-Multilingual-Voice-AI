import torch
from transformers import VitsModel, AutoTokenizer
import soundfile as sf

# One model per language (MMS-TTS uses separate checkpoints per language)
MODEL_MAP = {
    "hindi": "facebook/mms-tts-hin",
    "tamil": "facebook/mms-tts-tam",
    "telugu": "facebook/mms-tts-tel",
    "marathi": "facebook/mms-tts-mar",
    "bengali": "facebook/mms-tts-ben",
    "gujarati": "facebook/mms-tts-guj",
    "kannada": "facebook/mms-tts-kan",
}

_loaded_models = {}  # cache so we don't reload the same language model repeatedly

def _get_model_and_tokenizer(language: str):
    if language not in _loaded_models:
        model_name = MODEL_MAP.get(language.lower())
        if not model_name:
            raise ValueError(f"Unsupported language: {language}")
        print(f"Loading TTS model for {language}...")
        model = VitsModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        _loaded_models[language] = (model, tokenizer)
        print(f"TTS model for {language} loaded successfully!")
    return _loaded_models[language]

def synthesize_speech(text: str, language: str = "hindi", output_path: str = "output.wav"):
    """
    Converts text (already in the target language) into speech and saves as .wav
    """
    model, tokenizer = _get_model_and_tokenizer(language)
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs).waveform

    audio_arr = output.squeeze().cpu().numpy()
    sf.write(output_path, audio_arr, model.config.sampling_rate)
    return output_path

# Quick test when this file is run directly
if __name__ == "__main__":
    sample_hindi = "25 न्यूटन मीटर तक टॉर्क को चालू करें"
    path = synthesize_speech(sample_hindi, "hindi", "test_output.wav")
    print(f"Audio saved to: {path}")