import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def extract_text_from_pdfs(pdf_paths):
    text = ""
    for path in pdf_paths:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                # Try to extract text normally
                page_text = page.extract_text()
                if page_text and len(page_text.strip()) > 30:
                    text += page_text + "\n"
                else:
                    # If little or no text, use OCR
                    try:
                        images = convert_from_path(path, first_page=i+1, last_page=i+1)
                        for image in images:
                            ocr_text = pytesseract.image_to_string(image)
                            if ocr_text.strip():
                                text += ocr_text + "\n"
                    except Exception as e:
                        print(f"OCR failed for {path} page {i+1}: {e}")
    return text

if __name__ == "__main__":
    pdf_files = [os.path.join('training_data', f) for f in os.listdir('training_data') if f.endswith('.pdf')]
    knowledge_base = extract_text_from_pdfs(pdf_files)
    with open("knowledge_base.txt", "w", encoding="utf-8") as out:
        out.write(knowledge_base)
    print("Knowledge base extracted and saved to knowledge_base.txt")