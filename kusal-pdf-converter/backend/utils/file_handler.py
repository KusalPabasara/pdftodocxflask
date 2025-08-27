import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import threading
import time

class FileHandler:
    def __init__(self, upload_folder, allowed_extensions):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
        self._start_cleanup_thread()
    
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_uploaded_file(self, file):
        """
        Save uploaded file with unique name
        """
        if file and self.allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{unique_id}_{original_filename}"
            
            filepath = os.path.join(self.upload_folder, filename)
            file.save(filepath)
            return filepath, filename
        return None, None
    
    def cleanup_old_files(self, hours=1):
        """
        Remove files older than specified hours
        """
        now = time.time()
        cutoff = now - (hours * 3600)
        
        for filename in os.listdir(self.upload_folder):
            filepath = os.path.join(self.upload_folder, filename)
            if os.path.isfile(filepath):
                if os.path.getmtime(filepath) < cutoff:
                    try:
                        os.remove(filepath)
                    except:
                        pass
    
    def _start_cleanup_thread(self):
        """
        Start background thread for file cleanup
        """
        def cleanup_loop():
            while True:
                time.sleep(3600)  # Run every hour
                self.cleanup_old_files()
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()