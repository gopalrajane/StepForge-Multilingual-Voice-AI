import re

# ---------------------------------------------------------
# 1. GLOSSARY DICTIONARY
# Add technical terms here. Each term can either:
#   - stay untouched (set value to None) -> keeps original English word
#   - have a specific preferred word per language
# ---------------------------------------------------------
GLOSSARY = {
    "torque wrench": {
        "hindi": "टॉर्क रिंच",
        "tamil": "டார்க் ரென்ச்",
        "telugu": None,   # None = leave as English
    },
    "bolt": {
        "hindi": "बोल्ट",
        "tamil": "பொல்ட்",
    },
    "clutch plate": {
        "hindi": "क्लच प्लेट",
    },
    # Add more terms as needed...
}

# Patterns that should NEVER be translated (part numbers, units, measurements)
PROTECT_PATTERNS = [
    r"\bM\d+\b",              # bolt sizes like M8, M10
    r"\b\d+\s?Nm\b",          # torque units like 25 Nm
    r"\b\d+\s?mm\b",          # measurements like 10mm
    r"\b[A-Z]{2,}-\d+\b",     # part codes like ABC-123
]


def protect_terms(text: str):
    """
    Replaces protected terms/patterns with placeholders before translation.
    Returns: (modified_text, replacements_dict)
    """
    replacements = {}
    counter = 0

    def _replace(match):
        nonlocal counter
        placeholder = f"§{counter}§"
        replacements[placeholder] = match.group(0)
        counter += 1
        return placeholder

    # Protect pattern-based terms (part numbers, units)
    for pattern in PROTECT_PATTERNS:
        text = re.sub(pattern, _replace, text)

    # Protect glossary terms (case-insensitive match)
    for term in GLOSSARY:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(_replace, text)

    return text, replacements


def restore_terms(translated_text: str, replacements: dict, target_lang: str):
    """
    Puts protected terms back into the translated text.
    Uses glossary preferred translation if available, otherwise keeps original English.
    """
    for placeholder, original in replacements.items():
        lower_original = original.lower()
        if lower_original in GLOSSARY:
            preferred = GLOSSARY[lower_original].get(target_lang)
            replacement = preferred if preferred else original
        else:
            # Not a glossary word -> must be a protected pattern (part number/unit)
            replacement = original
        translated_text = translated_text.replace(placeholder, replacement)
    return translated_text


# Quick test when this file is run directly
if __name__ == "__main__":
    sample = "Torque the M8 bolt to 25 Nm using the torque wrench."
    protected_text, repl = protect_terms(sample)
    print("Protected text (ready for translation):")
    print(protected_text)
    print("\nReplacements found:")
    print(repl)

    # Simulate translation not touching placeholders, then restoring
    fake_translated = protected_text  # pretend this went through translation
    restored = restore_terms(fake_translated, repl, "hindi")
    print("\nRestored text:")
    print(restored)