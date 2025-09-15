# Extract text from DOCX files

import docx

def extract_text(docx_path: str) -> str:
    doc = docx.Document(docx_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

if __name__ == "__main__":
    print(extract_text("app/ingestion/test.docx"))