from openai import OpenAI

# Use OpenAI models to deal with text and speech-to-text generation
class OpenAIModel:
    def __init__(self, api_key: str):
        """
        Initialize OpenAI client
        """
        self.client = OpenAI(api_key=api_key)

    def chat_completion(self, messages, model_engine):
        """
        Generate chat completion message
        """
        try:
            # Create chat completion
            response = self.client.chat.completions.create(
                model=model_engine,
                messages=messages
            )

            # Get the role and content from the response
            role = response.choices[0].message.role
            content = response.choices[0].message.content.strip()
            return role, content

        except Exception as e:
            raise e

    def audio_transcriptions(self, file_path, model_engine):
        """
        Use whisper to generate audio transcriptions(speech-to-text)
        """
        with open(file_path, 'rb') as f:
            audio_file = f.read()
            response = self.client.audio.transcriptions.create(model_engine, audio_file)
        return response.text