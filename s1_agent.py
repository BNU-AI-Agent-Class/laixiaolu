import os                                                           # 0. 用于读取环境变量和脚本路径
import sys
sys.stdout.reconfigure(encoding='utf-8')                            # 解决 Windows 终端中文乱码

_script_dir = os.path.dirname(os.path.abspath(__file__))            # 脚本所在目录

from dotenv import load_dotenv
load_dotenv(os.path.join(_script_dir, "..", ".env"))                # 1. 读取上层目录 .env 中的 API 密钥

from openrouter import OpenRouter                                   # 2. 导入 OpenRouter SDK

# s1: 单轮聊天
# 要点：用户输入一次，模型回答一次。
# 没有历史，所以它"记不住"。

with OpenRouter(                                                    # 3. 创建客户端
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    user_input = input("\n你：")                                    # 4. 等待用户输入一次

    messages = [                                                    # 5. 只包含当前这一轮
        {"role": "system", "content": "你是一个乐于助人的助手。"},
        {"role": "user", "content": user_input}
    ]

    response = client.chat.send(                                    # 6. 发送给模型
        model="anthropic/claude-sonnet-4",                          #    可替换为你自己的模型
        messages=messages
    )
    reply = response.choices[0].message.content                     # 7. 提取回复
    print(f"[AI] {reply}")                                          # 8. 打印回复
