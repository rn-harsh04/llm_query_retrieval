import PyPDF2
import docx
import aiohttp
import os
from urllib.parse import urlparse

async def download_file(url: str, local_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(local_path, 'wb') as f:
                    f.write(await response.read())
                return local_path
    return None

def extract_text_from_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")

async def parse_document(document_url: str) -> str:
    parsed_url = urlparse(document_url)
    file_extension = parsed_url.path.lower().split('.')[-1]
    if file_extension not in ['pdf', 'docx']:
        raise ValueError(f"Unsupported file type: {file_extension}")
    local_path = f"temp_document.{file_extension}"
    try:
        downloaded_path = await download_file(document_url, local_path)
        if not downloaded_path:
            raise Exception("Failed to download document")
        if file_extension == 'pdf':
            text = extract_text_from_pdf(local_path)
        elif file_extension == 'docx':
            text = extract_text_from_docx(local_path)
        return text
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)