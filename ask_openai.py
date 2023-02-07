import os
import openai
openai.api_key = "YOUR OPEN AI API KEY HERE"

#MODEL="text-babbage-001"
#MODEL="text-curie-001"
MODEL="text-davinci-003"
## SELECT WHAT MODEL TO USE


def ask_prompt(prompt, model=MODEL, num_results=1, max_tokens=1024, stopSequences=["You:", "Conrad:"],
                  temperature=0.8, topP=1.0, topKReturn=1):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=topP,
        frequency_penalty=1,
        presence_penalty=0,
        stop=stopSequences
    )
    if response != 0:
        for choice in response.choices:
            return choice.text
    return "[idk]"
