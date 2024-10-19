import asyncio
import json
import os
from typing import List, Dict, Optional
from telegram import Update
from telegram.ext import CallbackContext
from openai import OpenAI
from AIModels.tts import generate_tts
from config import OPENAI_API_KEY
from utils.database import execute_query, get_data
from utils.user_management import get_user_setting

client = OpenAI(api_key=OPENAI_API_KEY)


class ChatGPT:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    async def chat_with_assistant(
        self,
        user_id: int,
        user_message: str = "",
        update: Update = None,
        context: CallbackContext = None,
        system_message: str = "",
        save_history: bool = True,
        use_response_mode: bool = True,
        return_as_text: bool = False,
        **kwargs,  # Passing extra parameters to generate_response
    ) -> Optional[str]:
        """
        Centralized function to handle chatting with the assistant.

        Args:
            user_id: The ID of the user.
            user_message: The user's message.
            update: The Telegram Update.
            context: The Telegram CallbackContext.
            system_message: An optional system message to set the assistant's behavior.
            save_history: Whether to save the chat history to the database.
            use_response_mode: The desired response mode ("text" or "voice").
            **kwargs: Additional keyword arguments to pass to the OpenAI API.

        Returns:
            The assistant's response (text or audio file path), or None if an error occurred.
        """
        messages = []
        if context:
            messages = context.user_data.get("messages", [])
        if not messages and system_message:
            messages = [{"role": "system", "content": system_message}]
        if user_message:
            messages.append({"role": "user", "content": user_message})

        try:
            message = None
            if not return_as_text:
                message = await update.message.reply_text("جارٍ التفكير في رد... 🤔")

            assistant_response = await self.generate_response(messages, **kwargs)

            if return_as_text:
                return assistant_response

            messages.append({"role": "assistant", "content": assistant_response})

            if save_history:
                await self.save_chat_history(user_id, messages)
            context.user_data["messages"] = messages

            if use_response_mode:
                response_mode = await get_user_setting(user_id, "voice_written")
            else:
                response_mode = "written"

            if response_mode == "voice":
                await _voice_response_processor(assistant_response, message)
            else:
                await _written_response_processor(assistant_response, message)
            return True
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None

    async def generate_response(self, messages, **kwargs) -> str:
        try:
            completion = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=messages,
                **kwargs,
            )
            assistant_response = completion.choices[0].message.content
            return assistant_response
        except Exception as e:
            print(f"Error calling generate_response: {e}")
            return None

    @staticmethod
    async def get_chat_history(
        user_id: int,
    ) -> List[Dict[str, str]]:  # Make this asynchronous
        result = await asyncio.to_thread(
            get_data,  # Run database query in a separate thread
            "SELECT messages FROM chat_history WHERE user_id = ?",
            (user_id,),
        )
        return json.loads(result[0][0]) if result else []

    @staticmethod
    async def save_chat_history(
        user_id: int, messages: List[Dict[str, str]]
    ) -> None:  # Make this asynchronous
        existing_history = await ChatGPT.get_chat_history(user_id)
        if existing_history:
            # Update existing chat history
            await asyncio.to_thread(
                execute_query,  # Run database query in a separate thread
                "UPDATE chat_history SET messages = ? WHERE user_id = ?",
                (json.dumps(messages), user_id),
            )
        else:
            # Insert new chat history if it doesn't exist
            await asyncio.to_thread(
                execute_query,  # Run database query in a separate thread
                "INSERT INTO chat_history (user_id, messages) VALUES (?, ?)",
                (user_id, json.dumps(messages)),
            )

    @staticmethod
    async def clear_user_history(user_id: int) -> None:  # Make this asynchronous
        """Clears the chat history for a specific user."""
        await asyncio.to_thread(
            execute_query,  # Run database query in a separate thread
            "DELETE FROM chat_history WHERE user_id = ?",
            (user_id,),
        )


def get_chatgpt_instance(model: Optional[str] = None) -> ChatGPT:
    return ChatGPT(model) if model else ChatGPT()


async def _written_response_processor(response: str, message: Update):
    """Sends the response as a text message."""
    await message.edit_text(response)


async def _voice_response_processor(response: str, message: Update):
    """Sends the response as a voice message."""
    audio_file_path = await generate_tts(response)
    await message.reply_voice(voice=open(audio_file_path, "rb"))
    os.remove(audio_file_path)
