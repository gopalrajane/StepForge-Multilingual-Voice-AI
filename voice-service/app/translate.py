from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from app.glossary import protect_terms, restore_terms

MODEL_NAME = "facebook/nllb-200-distilled-600M"

print("Loading translation model... (this may take a minute the first time)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

print("Translation model loaded successfully!")

LANGUAGE_CODES = {
    "hindi": "hin_Deva",
    "marathi": "mar_Deva",
    "tamil": "tam_Taml",
    "telugu": "tel_Telu",
    "kannada": "kan_Knda",
    "bengali": "ben_Beng",
    "gujarati": "guj_Gujr",
}

def translate_text(text: str, target_lang: str = "hindi") -> str:
    """
    Translates English text to the target Indian language,
    protecting technical terms/part numbers via the glossary layer.
    """
    tgt_code = LANGUAGE_CODES.get(target_lang.lower())
    if not tgt_code:
        raise ValueError(f"Unsupported language: {target_lang}")

    # Step 1: protect technical terms before translation
    protected_text, replacements = protect_terms(text)

    # Step 2: translate the protected text
    tokenizer.src_lang = "eng_Latn"
    inputs = tokenizer(protected_text, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
            max_length=256
        )

    translated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Step 3: restore protected terms with correct glossary translations
    final_text = restore_terms(translated, replacements, target_lang.lower())

    return final_text

# Quick test when this file is run directly
if __name__ == "__main__":
    sample = "Torque the M8 bolt to 25 Nm using the torque wrench."
    result = translate_text(sample, "hindi")
    print(f"English: {sample}")
    print(f"Hindi (glossary-protected): {result}")