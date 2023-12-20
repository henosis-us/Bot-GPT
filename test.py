import unittest
from unittest.mock import Mock
import asyncio
from main import gpt3

class TestBotCommands(unittest.TestCase):
    def test_gpt3(self):
        # Set up a mock context
        ctx = Mock()

        # Set up a mock message
        message = Mock()
        message.attachments = []
        ctx.message = message

        # Set up a mock author
        author = Mock()
        author.mention = "@testuser"
        ctx.author = author

        # Call the gpt3 command
        asyncio.run(gpt3(ctx, prompt="Test prompt"))

        # Check that the send function was called with the correct arguments
        ctx.send.assert_called_once()

if __name__ == '__main__':
    unittest.main()