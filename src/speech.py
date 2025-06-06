import os
from google.cloud import texttospeech
from google.oauth2.service_account import Credentials
import re

# Use Google Text-To-Speech to generate audio
class Speech():
    def __init__(self):
        """
        Load service account credentials from environment variables
        """
        credentials = Credentials.from_service_account_info({
            'type': os.getenv('type'),
            'project_id': os.getenv('project_id'),
            'private_key_id': os.getenv('private_key_id'),
            'private_key': os.getenv('private_key'),
            'client_email': os.getenv('client_email'),
            'client_id': os.getenv('client_id'),
            'auth_uri': os.getenv('auth_uri'),
            'token_uri': os.getenv('token_uri'),
            'auth_provider_x509_cert_url': os.getenv('auth_provider_x509_cert_url'),
            'client_x509_cert_url': os.getenv('client_x509_cert_url'),
        })
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)

    def clean_text(self, text):
        """
        Remove symbols that may affect speech synthesis
        """
        # Remove ** or * symbols
        text = re.sub(r'\*\*|\*', '', text)
        # Remove Markdown link format [text](url)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)
        return text
    
    def text_to_speech(self, text, voice_name, translate_language, audio_path):
        """
        Use Google Text-To-Speech to generate audio content
        """
        cleaned_text = self.clean_text(text)
        synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)

        # Define the voice selection parameters (name and language)
        voice = texttospeech.VoiceSelectionParams(
            name=voice_name,
            language_code=translate_language
        )

        # Set the audio configuration (in MP3 format)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(audio_path, 'wb') as out:
            out.write(response.audio_content)
