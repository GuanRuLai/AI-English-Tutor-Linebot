import subprocess
import json

# Provide methods for audio format conversion and audio length calculation
class Audio():
    def convert_to_aac(self, input_file, output_file):
        """
        Convert audio files to AAC format(.m4a or .aac)
        'ffmpeg': Call the FFmpeg program
        '-i', input_file: Specify the input file
        '-c:a', 'aac': Use AAC audio encoding format
        output_file: Output the converted file
        '-y': If the file already exists, automatically overwrite it.
        """
        subprocess.run(['ffmpeg', '-i', input_file, '-c:a', 'aac', output_file, '-y'])

    def convert_to_wav(self, input_file, output_file):
        """
        Convert audio files to WAV format(.wav)
        'ffmpeg': Call the FFmpeg program
        '-i', input_file: Specify the input file
        output_file: Output the converted file
        '-y': If the file already exists, automatically overwrite it.
        """
        subprocess.run(['ffmpeg', '-i', input_file, output_file, '-y'])

    def get_audio_duration(self, input_file):
        """
        Get the audio duration of a file
        'ffprobe': FFmpeg's analysis tool (specially used to read audio/video information)
        '-v', 'quiet': Hide unnecessary output
        '-show_format': Display audio format information (including duration)
        '-print_format', 'json': output in JSON format
        """
        out = subprocess.check_output(['ffprobe', '-v', 'quiet', '-show_format', '-print_format', 'json', input_file])
        ffprobe_data = json.loads(out)
        return float(ffprobe_data['format']['duration'])

# Create audio processing object
audio = Audio()