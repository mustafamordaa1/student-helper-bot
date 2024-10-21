import os
import uuid
from gtts import gTTS


async def generate_tts(text: str, lang: str = "ar") -> str:
    """Generates TTS audio using gTTS and returns the path to the audio file."""
    tts = gTTS(text=text, lang=lang, slow=False, tld="com.ar")
    file_name = f"{uuid.uuid4()}.mp3"  # Generate a unique file name
    file_path = os.path.join("temp", file_name)  # Save in a temporary directory
    tts.save(file_path)
    return file_path


async def diacritize_text(text: str) -> str:
    """Sends text to ChatGPT for diacritization and returns the cleaned result."""
    # prompt = f"Put diacritical marks on the following Arabic text: {text}\nReturn only the diacritized text."
    # response = client.chat.completions.create(engine="text-davinci-003", prompt=prompt, max_tokens=150)

    # diacritized_text = response.choices[0].text.strip()
    # # (Optional) Add more robust cleaning logic to ensure ONLY diacritized text is returned
    # return diacritized_text
    pass
