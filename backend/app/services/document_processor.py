import os
import io
from typing import List, Dict, Any, Optional

class DocumentProcessor:
    """Processes uploaded PDF and DOCX brand guideline documents."""

    @staticmethod
    def extract_from_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        chunks = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text and text.strip():
                    # Segment by paragraphs or headings
                    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
                    if not paragraphs:
                        paragraphs = [text.strip()]
                    
                    for idx, para in enumerate(paragraphs):
                        # Extract first line as tentative section title if short
                        lines = para.split("\n")
                        section_name = lines[0][:60] if len(lines) > 1 and len(lines[0]) < 60 else f"Page {page_num + 1} Section {idx + 1}"
                        chunks.append({
                            "section_name": section_name,
                            "page_number": page_num + 1,
                            "content": para,
                            "chunk_index": len(chunks)
                        })
            doc.close()
        except ImportError:
            # Fallback if PyMuPDF not compiled yet
            chunks.append({
                "section_name": "Full Document",
                "page_number": 1,
                "content": file_bytes.decode("utf-8", errors="ignore"),
                "chunk_index": 0
            })
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")

        return chunks

    @staticmethod
    def extract_from_docx(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        chunks = []
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            current_heading = "General"
            current_buffer = []

            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue

                if para.style.name.startswith("Heading"):
                    if current_buffer:
                        chunks.append({
                            "section_name": current_heading,
                            "page_number": 1,
                            "content": "\n\n".join(current_buffer),
                            "chunk_index": len(chunks)
                        })
                        current_buffer = []
                    current_heading = text
                else:
                    current_buffer.append(text)

            if current_buffer:
                chunks.append({
                    "section_name": current_heading,
                    "page_number": 1,
                    "content": "\n\n".join(current_buffer),
                    "chunk_index": len(chunks)
                })
        except ImportError:
            chunks.append({
                "section_name": "Full Document",
                "page_number": 1,
                "content": file_bytes.decode("utf-8", errors="ignore"),
                "chunk_index": 0
            })
        except Exception as e:
            raise ValueError(f"Failed to process DOCX: {str(e)}")

        return chunks

    @classmethod
    def process_file(cls, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return cls.extract_from_pdf(file_bytes, filename)
        elif ext in [".docx", ".doc"]:
            return cls.extract_from_docx(file_bytes, filename)
        elif ext in [".txt", ".md"]:
            text = file_bytes.decode("utf-8", errors="ignore")
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            return [
                {
                    "section_name": f"Section {i+1}",
                    "page_number": 1,
                    "content": p,
                    "chunk_index": i
                }
                for i, p in enumerate(paras)
            ]
        else:
            raise ValueError(f"Unsupported document format '{ext}'. Supported formats: PDF, DOCX, TXT, MD.")
