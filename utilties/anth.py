import anthropic
import os
async def anthropicResponse(model, messages):
    # Initialize the Anthropic client with your API key
    client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    try:
        # Use the client to create a message
        message = client.messages.create(
            model=model,
            max_tokens=3096,
            temperature=0.2,
            messages=messages
        )
        print(message)
        # Extract just the assistant's response from the message output
        assistant_response = message.content[0].text
        # Update the message variable with the assistant's response
        message = assistant_response
        return message
    except anthropic.exceptions.AnthropicAPIError as e:
        if e.status_code in [500, 529]:
            print("There was a system error with the Anthropic API. Please try again later.")
            return "System error with the Anthropic API."
        else:
            raise
