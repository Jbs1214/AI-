import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    api_key=os.environ["HF_TOKEN"],
)

q = input("질문을 입력해주세요 : ")
completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1:novita",
    messages=[
        {
            "role": "user",
            "content": q
        }
    ],
)

print(completion.choices[0].message)