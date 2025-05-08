import subprocess
import os
import shutil
from typing import Optional, Tuple, Dict, Any
import logging # Import logging

logger = logging.getLogger(__name__) # Initialize logger

def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed and available in PATH"""
    try:
        result = shutil.which('ffmpeg')
        if result is None:
            return False
        # Verify it's actually executable
        subprocess.run([result, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        return False

def convert_to_wav(input_path: str, output_path: str) -> bool:
    """
    Convert any audio/video file to WAV format using ffmpeg.
    Returns True if conversion was successful, False otherwise.
    """
    if not os.path.exists(input_path):
        # print(f"[convert_to_wav] Error: Input file '{input_path}' does not exist.")
        logger.error(f"Input file '{input_path}' does not exist for WAV conversion.")
        return False
    
    if not check_ffmpeg():
        # print(f"[convert_to_wav] Error: ffmpeg is not installed or not available in PATH.")
        logger.error("ffmpeg is not installed or not available in PATH for WAV conversion.")
        return False
    
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # Use ffmpeg to convert the file to WAV
        command = [
            'ffmpeg',
            '-i', input_path,  # Input file
            '-acodec', 'pcm_s16le',  # Audio codec (16-bit PCM)
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Number of channels (stereo)
            '-y',  # Overwrite output file if it exists
            output_path
        ]
        
        # Run ffmpeg and capture output
        # print(f"[convert_to_wav] Running command: {' '.join(command)}")
        logger.info(f"Running ffmpeg command for WAV conversion: {' '.join(command)}")
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            # print(f"[convert_to_wav] Error: ffmpeg command failed with code {result.returncode}")
            # print(f"[convert_to_wav] Error output: {result.stderr}")
            logger.error(f"ffmpeg WAV conversion command failed with code {result.returncode}. Stderr: {result.stderr}")
            return False
            
        if not os.path.exists(output_path):
            # print(f"[convert_to_wav] Error: Output file '{output_path}' was not created.")
            logger.error(f"Output file '{output_path}' was not created after ffmpeg WAV conversion.")
            return False
            
        # print(f"[convert_to_wav] Successfully converted '{input_path}' to '{output_path}'")
        logger.info(f"Successfully converted '{input_path}' to WAV: '{output_path}'")
        return True
        
    except Exception as e:
        # print(f"[convert_to_wav] Error: {str(e)}")
        logger.exception(f"Error during WAV conversion of '{input_path}': {str(e)}")
        return False

def get_audio_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an audio file using ffmpeg.
    Returns a dictionary of metadata.
    """
    if not check_ffmpeg():
        return {"error": "ffmpeg not available"}
        
    try:
        # Run ffprobe to get file information
        command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            return {"error": f"ffprobe command failed: {result.stderr}"}
            
        # Parse the JSON output
        import json
        metadata = json.loads(result.stdout)
        return metadata
        
    except Exception as e:
        return {"error": str(e)} 