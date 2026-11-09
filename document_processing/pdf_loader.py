
from pypdf import PdfReader


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    extracted_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            extracted_text.append(
                f"\n--- Page {page_number} ---\n{page_text}"
            )

    return "\n".join(extracted_text)
