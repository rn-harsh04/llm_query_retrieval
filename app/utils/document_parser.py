from PyPDF2 import PdfReader
import docx
import requests
from io import BytesIO

def extract_text_from_pdf(url):
    response = requests.get(url)
    pdf_reader = PdfReader(BytesIO(response.content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(url):
    response = requests.get(url)
    doc = docx.Document(BytesIO(response.content))
    return "\n".join([p.text for p in doc.paragraphs])

def parse_document(url):
    if url.endswith(".pdf"):
        return extract_text_from_pdf(url)
    elif url.endswith(".docx"):
        return extract_text_from_docx(url)
    else:
        raise ValueError("Unsupported format")
