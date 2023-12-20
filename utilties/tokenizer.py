import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4")

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    if isinstance(string, bytes):
        string = string.decode('utf-8')
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    # Always use cl100k_base encoding
    encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = 4  # every message follows <|im_start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = -1  # if there's a name, the role is omitted

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|im_start|>assistant<|im_sep|>
    return num_tokens