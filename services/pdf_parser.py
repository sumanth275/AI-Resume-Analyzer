import pymupdf  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text content from a PDF file using PyMuPDF (pymupdf).
    Handles exceptions, unreadable PDFs, and multi-page documents.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    extracted_text = []
    try:
        doc = pymupdf.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                extracted_text.append(text)
        doc.close()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    full_text = "\n".join(extracted_text).strip()
    
    # Remove null characters or malformed unicode
    full_text = full_text.replace('\x00', '')
    
    if not full_text:
        raise ValueError("Could not extract any readable text from the PDF. It may be a scanned image or protected file.")

    return full_text
