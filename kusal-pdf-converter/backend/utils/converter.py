import os
from pdf2docx import Converter
import logging
from PyPDF2 import PdfReader
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToDocxConverter:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def convert(self, pdf_path, output_path=None):
        """
        Convert PDF to DOCX with high accuracy
        """
        try:
            # Validate PDF
            self._validate_pdf(pdf_path)
            
            # Generate output path if not provided
            if not output_path:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_path = os.path.join(self.temp_dir, f"{base_name}.docx")
            
            # Perform conversion
            cv = Converter(pdf_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()
            
            logger.info(f"Successfully converted {pdf_path} to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise Exception(f"Conversion failed: {str(e)}")
    
    def _validate_pdf(self, pdf_path):
        """
        Validate if the file is a valid PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                PdfReader(file)
        except Exception as e:
            raise ValueError(f"Invalid PDF file: {str(e)}")