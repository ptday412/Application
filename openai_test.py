import os
from config.settings.base import BASE_DIR
from openai import OpenAI
import environ

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

client = OpenAI(
    api_key=env('OPENAI_API_KEY'),
)

system_instructions = """
이제부터 너는 "영어, 한글 번역가"야. 
지금부터 내가 입력하는 모든 프롬프트를 무조건 한글은 영어로, 영어는 한글로 번역해줘. 
프롬프트의 내용이나 의도는 무시하고 오직 번역만 해줘.
"""

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
        },
        {
            "role": "user",
            "content": "Compose a poem that explains the concept of recursion in programming.",
        },
    ],
)

print(completion.choices[0].message)
