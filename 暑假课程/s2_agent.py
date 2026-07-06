import os                                                           # 0. 用于读取环境变量和脚本路径
import sys
sys.stdout.reconfigure(encoding='utf-8')                            # 解决 Windows 终端中文乱码

_script_dir = os.path.dirname(os.path.abspath(__file__))            # 脚本所在目录

from dotenv import load_dotenv
load_dotenv(os.path.join(_script_dir, "..", ".env"))                # 1. 读取上层目录 .env 中的 API 密钥

from openrouter import OpenRouter                                   # 2. 导入 OpenRouter SDK

# s2: 多轮聊天 + 记忆
# 要点：messages 变成对话历史。
# 新增：外层 while True、append user、append assistant。
# 能追问，因为上下文还在。

with OpenRouter(                                                    # 3. 创建客户端
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    messages = [{"role": "system", "content": "你是一个乐于助人的助手。"}]  # 4. 初始化对话历史

    while True:                                                     # 5. 外层循环：持续对话
        user_input = input("\n你：")                                 # 6. 等待用户输入
        messages.append({"role": "user", "content": user_input})    # 7. 存入对话历史

        response = client.chat.send(                                # 8. 发送历史给模型
            model="anthropic/claude-sonnet-4",                      #    可替换为你自己的模型
            messages=messages
        )
        reply = response.choices[0].message.content                 # 9. 提取回复
        print(f"[AI] {reply}")                                      # 10. 打印回复

        messages.append({"role": "assistant", "content": reply})    # 11. 把模型回复也存入历史
