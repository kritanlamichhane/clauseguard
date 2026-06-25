import sys
sys.path.append(".")

import os
from backend.extractor import extract_text

def test_pdf_extraction():
    pdf_path = "tests/sample_contract.pdf"
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF file not found: {pdf_path}")
        sys.exit(1)
        
    text = extract_text(pdf_path)
    assert text is not None, "Extraction returned None"
    assert len(text) > 0, "Extracted text is empty"
    assert "SAMPLE SERVICE AGREEMENT" in text, "Key heading not found in extracted text"
    print("[SUCCESS] PDF extraction test passed!")

def test_txt_extraction():
    temp_txt_path = "tests/temp_test_contract.txt"
    test_content = "This is a temporary test contract.\nSection 1: Details."
    
    with open(temp_txt_path, "w", encoding="utf-8") as f:
        f.write(test_content)
        
    try:
        text = extract_text(temp_txt_path)
        assert text == test_content, f"Expected {repr(test_content)} but got {repr(text)}"
        print("[SUCCESS] TXT extraction test passed!")
    finally:
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)

if __name__ == "__main__":
    print("Running extractor tests...")
    test_pdf_extraction()
    test_txt_extraction()
    print("All extractor tests passed successfully!")
