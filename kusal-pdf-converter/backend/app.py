from flask import Flask, request, jsonify, send_file, render_template_string, send_from_directory
from flask_cors import CORS
import os
import logging
import threading
from config import Config
from utils.converter import PDFToDocxConverter
from utils.file_handler import FileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize components
converter = PDFToDocxConverter()
file_handler = FileHandler(app.config['UPLOAD_FOLDER'], app.config['ALLOWED_EXTENSIONS'])

# Serve frontend files
@app.route('/')
def index():
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'index.html')
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return jsonify({
            "service": "KUSAL PDF to DOCX Converter",
            "status": "active",
            "endpoints": {
                "convert": "/api/convert",
                "health": "/api/health"
            }
        })

@app.route('/css/<path:filename>')
def serve_css(filename):
    css_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'css')
    return send_from_directory(css_dir, filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    js_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'js')
    return send_from_directory(js_dir, filename)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "KUSAL PDF Converter"})

@app.route('/api/convert', methods=['POST'])
def convert_pdf():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save uploaded file
        pdf_path, filename = file_handler.save_uploaded_file(file)
        if not pdf_path:
            return jsonify({"error": "Invalid file type. Only PDF files are allowed"}), 400
        
        # Convert PDF to DOCX
        docx_path = converter.convert(pdf_path)
        
        # Prepare response filename
        response_filename = filename.rsplit('.', 1)[0] + '.docx'
        
        # Send file and cleanup
        def remove_files():
            try:
                os.remove(pdf_path)
                os.remove(docx_path)
            except:
                pass
        
        # Schedule cleanup after sending file
        threading.Timer(10, remove_files).start()
        
        return send_file(
            docx_path,
            as_attachment=True,
            download_name=response_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)