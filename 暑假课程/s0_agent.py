import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

_script_dir = os.path.dirname(os.path.abspath(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(_script_dir, "..", ".env"))

from openrouter import OpenRouter

# s0: 最小 API 调用
# 要点：只验证"模型能跑"。
# 只发一条 user message，只调用一次，不循环、不保留历史。

with OpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    response = client.chat.send(
        model="anthropic/claude-sonnet-4",
        messages=[
            {"role": "user", "content": "你好，请回复一个简短的问候。"}
        ]
    )
    print(response.choices[0].message.content)
