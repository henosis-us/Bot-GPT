import unittest
from unittest.mock import patch, MagicMock
from utilties.Openai_Utils import generate_response

class TestGenerateResponse(unittest.TestCase):
    def setUp(self):
        self.model_name = "gpt-3.5-turbo"
        self.prompt = "Hello, world!"
        self.chat_history = [{"role": "user", "content": "Hello, bot!"}]
        self.preprompt = "You are an autoregressive language model..."

    @patch('discord.Thread')
    @patch('discord.Message')
    async def test_generate_response(self, mock_thread, mock_message):
        # Mock the thread's messages
        mock_message.content = "Hello, bot!"
        mock_message.author = MagicMock()
        mock_message.author.bot = False
        mock_thread.history.return_value.flatten.return_value = [mock_message]

        # Fetch the chat history from the thread
        chat_history = [{"role": "user" if message.author.bot else "assistant", "content": message.content} for message in await mock_thread.history().flatten()]

        response = await generate_response(self.model_name, self.prompt, chat_history, preprompt=self.preprompt)

        # Test that the preprompt is not in the chat history
        self.assertNotIn(self.preprompt, [message['content'] for message in chat_history])

        # Test that the response is not None
        self.assertIsNotNone(response)

        # Test that the response is a string
        self.assertIsInstance(response, str)

        # Test that the response contains the prompt
        self.assertIn(self.prompt, response)

if __name__ == '__main__':
    unittest.main()