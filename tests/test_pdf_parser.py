import os
import pytest
import pymupdf  # PyMuPDF
from services.pdf_parser import extract_text_from_pdf

def test_extract_text_from_pdf(tmp_path):
    # Create a temporary PDF file with sample text
    pdf_path = os.path.join(tmp_path, "sample_resume.pdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "John Doe\nPython Developer\nSkills: Flask, SQL, Docker")
    doc.save(pdf_path)
    doc.close()

    text = extract_text_from_pdf(pdf_path)
    assert "John Doe" in text
    assert "Python Developer" in text
    assert "Flask" in text

def test_extract_text_non_existent_file():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("non_existent_path.pdf")
