import re
import spacy

# Load spaCy model and raise max length
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 20_000_000

def deidentify_text(text, chunk_size=100000):
    """
    Replaces personal and sensitive info using spaCy NER and regex fallback.
    Logs matches as they are found (before replacement).
    """
    spans = []

    # === Step 1: Chunk + NER ===
    start_idx = 0
    while start_idx < len(text):
        chunk = text[start_idx : start_idx + chunk_size]
        doc = nlp(chunk)
        for ent in doc.ents:
            label = None
            if ent.label_ == "PERSON":
                label = "[NAME]"
            elif ent.label_ == "EMAIL":
                label = "[EMAIL]"
        
            if label:
                global_start = start_idx + ent.start_char
                global_end = start_idx + ent.end_char
                spans.append((global_start, global_end, label))
                print(f"NER match: '{ent.text}' → {label}")
        start_idx += chunk_size

    # === Step 2: Regex Fallbacks ===
    # regex_patterns = [
    #     (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', "[NAME]"),
    #     (r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "[EMAIL]"),
    #     (r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', "[DATE]"),
    #     (r'\b\d{1,2}:\d{2}(?: ?[APap][Mm])?\b', "[TIME]"),
    #     (r'https?://\S+', "[URL]"),
    #     (r"\b[Mm]y name['’]?s (\w+)", "My name is [NAME]"),
    # ]

    # for pattern, label in regex_patterns:
    #     if pattern == r"\b[Mm]y name['’]?s (\w+)":
    #         matches = re.findall(pattern, text)
    #         for name in matches:
    #             print(f"Regex match: My name is {name} → My name is [NAME]")
    #         text = re.sub(pattern, "My name is [NAME]", text)
    #         continue

    #     for match in re.finditer(pattern, text):
    #         matched_text = match.group(0)
    #         spans.append((match.start(), match.end(), label))
    #         print(f"Regex match: '{matched_text}' → {label}")

    # === Step 3: Merge and Replace ===
    spans.sort()
    final_spans = []
    last_end = -1
    for start, end, label in spans:
        if start >= last_end:
            final_spans.append((start, end, label))
            last_end = end

    for start, end, label in reversed(final_spans):
        text = text[:start] + label + text[end:]

    return text
