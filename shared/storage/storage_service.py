import os
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"}
# Max upload size: 50MB (should match nginx/apache config if behind one)
MAX_CONTENT_LENGTH = 50 * 1024 * 1024


class StorageService:

    @staticmethod
    def save(file, folder="general"):
        
        # Save a file locally and return its URL.
        
        # Validate file extension
        extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '.{extension}' is not allowed. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        filename = StorageService._generate_filename(
            file.filename
        )

        upload_folder = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            folder
        )

        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(
            upload_folder,
            filename
        )

        file.save(filepath)

        return f"/uploads/{folder}/{filename}"

    @staticmethod
    def _generate_filename(original_name):
        extension = original_name.rsplit(".", 1)[-1]
        
        return f"{uuid4().hex}.{extension}"    