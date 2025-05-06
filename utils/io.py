import tempfile
import os
import uuid

def save_temp_file(upload_file):
    temp_dir = tempfile.gettempdir()  # Получаем временную папку для текущей ОС
    filename = os.path.join(temp_dir, f"{uuid.uuid4()}.wav")
    try:
        with open(filename, "wb") as f:
            f.write(upload_file.file.read())
    except Exception as e:
        raise FileNotFoundError(f"Could not save file: {e}")
    return filename
