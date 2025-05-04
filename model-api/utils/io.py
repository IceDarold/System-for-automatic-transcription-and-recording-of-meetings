import uuid
import os

def save_temp_file(upload_file):
    filename = f"/tmp/{uuid.uuid4()}.wav"
    with open(filename, "wb") as f:
        f.write(upload_file.file.read())
    return filename
