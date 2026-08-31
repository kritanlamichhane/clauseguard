import re

def remove_extra_whitespace(text):
    """Collapse multiple spaces/tabs into a single space"""
    return re.sub(r'[ \t]+', ' ', text)

def remove_extra_newlines(text):
    """Collapse 3+ newlines into just 2 (keep paragraph breaks)"""
    return re.sub(r'\n{3,}', '\n\n', text)

def fix_broken_lines(text):
    """
    PDFs often break a sentence across lines like:
    "The vendor shall not be liable for any
    damages arising from this agreement."
    We join lines that don't end with punctuation, but we avoid merging
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
            # Check for structural markdown/bullet elements starting the new line
            if (line.startswith('#') or 
                line.startswith('**') or 
                line.startswith('-') or 
                line.startswith('*') or 
                re.match(r'^\d+\.', line) or 
                re.match(r'^[A-Za-z]\)\s+', line)):
                is_new_block = True
            # Check if buffer ends with sentence-ending punctuation
            elif buffer.endswith(('.', ':', ';', '?', '!')):
                is_new_block = True
            else:
                # Decide based on continuation indicators
                last_word = buffer.split()[-1].lower() if buffer.split() else ""
                last_word_clean = re.sub(r'[^a-z0-9]', '', last_word)
                continuation_words = {
                    "and", "or", "the", "a", "an", "of", "to", "for", "with", "in", "on", 
                    "at", "by", "from", "any", "this", "shall", "be", "is", "are", "that", 
                    "which", "would", "should", "could", "may", "been", "have", "has", "had",
                    "not", "neither", "either", "such", "under", "between", "specifically"
                }
                
                # Join if the current line starts with lowercase or digit/symbol (non-uppercase)
                if not line[0].isupper():
                    is_new_block = False
                # Join if the previous line ended with a continuation word
                elif last_word_clean in continuation_words:
                    is_new_block = False
                # Otherwise, it starts a new block (e.g. capitalized new item/heading)
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

def remove_page_numbers(text):
    """Remove standalone numbers on their own line (page numbers)"""
    return re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)

def normalize_quotes(text):
    """Convert fancy quotes to normal quotes"""
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    return text


def clean_text(raw_text):
    """Main function — runs all cleaning steps in order"""
    text = raw_text
    text = normalize_quotes(text)
    text = remove_page_numbers(text)
    text = fix_broken_lines(text)
    text = remove_extra_whitespace(text)
    text = remove_extra_newlines(text)
    return text.strip()