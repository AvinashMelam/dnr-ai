import fitz  # PyMuPDF


def extract_resume_text(file_path):
    """
    Extracts text from a PDF resume.

    Args:
        file_path (str): Absolute path of the uploaded PDF.

    Returns:
        str: Extracted text from the PDF.
    """

    try:
        document = fitz.open(file_path)

        extracted_text = ""

        for page in document:
            extracted_text += page.get_text()

        document.close()

        return extracted_text.strip()

    except Exception as e:
        print(f"PDF Extraction Error: {e}")
        return ""