import openai
import json
from Openai_Utils import generate_response
input = "I drank 3 32oz glasses today"
model_name = "gpt-3.5-turbo"
preprompt = "Parse the user string and return the total amount of water consumed in oz"
output = generate_response(model_name, input, preprompt)
print(output)

