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
    We join lines that don't end with punctuation.
    """
    lines = text.split('\n')
    fixed_lines = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            fixed_lines.append(buffer)
            buffer = ""
            continue

        buffer += (" " + line if buffer else line)

        # If line ends with sentence-ending punctuation, close the buffer
        if line.endswith(('.', ':', ';')):
            fixed_lines.append(buffer)
            buffer = ""

    if buffer:
        fixed_lines.append(buffer)

    return '\n'.join(fixed_lines)

def remove_page_numbers(text):
    """Remove standalone numbers on their own line (page numbers)"""
    return re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)

def normalize_quotes(text):
    """Convert fancy quotes to normal quotes"""
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
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