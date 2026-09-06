import re

def remove_extra_whitespace(text: str) -> str:
    """Collapse multiple spaces/tabs into a single space"""
    return re.sub(r'[ \t]+', ' ', text)

def remove_extra_newlines(text: str) -> str:
    """Collapse 3+ newlines into just 2 (keep paragraph breaks)"""
    return re.sub(r'\n{3,}', '\n\n', text)

def fix_broken_lines(text: str) -> str:
    """
    PDFs often break a sentence across lines.
    We join lines that don't end with punctuation, avoiding merging
    structural elements (headers, bold labels, bullet points).
    """
    lines = text.split('\n')
    fixed_lines = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                fixed_lines.append(buffer)
                buffer = ""
            continue

        is_new_block = False
        if not buffer:
            is_new_block = True
        else:
            if (line.startswith('#') or 
                line.startswith('**') or 
                line.startswith('-') or 
                line.startswith('*') or 
                re.match(r'^\d+\.', line) or 
                re.match(r'^[A-Za-z]\)\s+', line)):
                is_new_block = True
            elif buffer.endswith(('.', ':', ';', '?', '!')):
                is_new_block = True
            else:
                last_word = buffer.split()[-1].lower() if buffer.split() else ""
                last_word_clean = re.sub(r'[^a-z0-9]', '', last_word)
                continuation_words = {
                    "and", "or", "the", "a", "an", "of", "to", "for", "with", "in", "on", 
                    "at", "by", "from", "any", "this", "shall", "be", "is", "are", "that", 
                    "which", "would", "should", "could", "may", "been", "have", "has", "had",
                    "not", "neither", "either", "such", "under", "between", "specifically"
                }
                
                if not line[0].isupper():
                    is_new_block = False
                elif last_word_clean in continuation_words:
                    is_new_block = False
                else:
                    is_new_block = True

        if is_new_block:
            if buffer:
                fixed_lines.append(buffer)
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        fixed_lines.append(buffer)

    return '\n'.join(fixed_lines)

def remove_page_numbers(text: str) -> str:
    """Remove standalone numbers on their own line (page numbers)"""
    return re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)

def normalize_quotes(text: str) -> str:
    """Convert fancy quotes to standard ASCII quotes"""
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


def clean_text(raw_text: str) -> str:
    """Main function — runs all cleaning steps in order"""
    text = raw_text
    text = normalize_quotes(text)
    text = remove_page_numbers(text)
    text = fix_broken_lines(text)
    text = remove_extra_whitespace(text)
    text = remove_extra_newlines(text)
    return text.strip()
