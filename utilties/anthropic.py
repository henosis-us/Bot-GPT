import anthropic
async def anthropicResponse(model, messages):
    client = anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="ANTHROPIC_API_KEY",
    )
    message = anthropic.Anthropic().messages.create(
        model,
        max_tokens=3096,
        temperature= .2,
        messages
    )
    return message