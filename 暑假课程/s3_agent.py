import os                                                           # 0. 用于读取环境变量、脚本路径和执行命令
import subprocess                                                    # 0.5 用于执行命令并指定编码
import sys
sys.stdout.reconfigure(encoding='utf-8')                            # 解决 Windows 终端中文乱码

_script_dir = os.path.dirname(os.path.abspath(__file__))            # 脚本所在目录

from dotenv import load_dotenv
load_dotenv(os.path.join(_script_dir, "..", ".env"))                # 1. 读取上层目录 .env 中的 API 密钥

from openrouter import OpenRouter                                   # 2. 导入 OpenRouter SDK

# s3: Agent 循环（老师给的参照）
# 要点：Agent 会自己决定下一步。
# 机制：内层循环自动执行、命令: 执行 shell、完成: 结束任务。

with OpenRouter(                                                    # 3. 创建客户端
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    messages = [{"role":"system","content":"""你必须用以下两种格式之一回复：
- 需要执行命令：命令:XXX（纯命令，不要解释，每次一条）
- 任务完成时：完成:XXX（总结信息）"""}]                             # 4. 系统提示词：定义 AI 的输出格式

    while True:                                                     # 5. 外层循环：等待用户输入新任务
        user_input = input("\n你：")                                 # 6. 等待用户输入
        messages.append({"role": "user", "content": user_input})    # 7. 存入对话历史

        while True:                                                 # 8. 内层循环：Agent 自主执行，直到任务完成
            response = client.chat.send(                            # 9. 发送对话历史给 AI
                model="anthropic/claude-sonnet-4",                  #    可替换为你自己的模型
                messages=messages
            )
            reply = response.choices[0].message.content             # 10. 提取 AI 回复
            messages.append({"role": "assistant", "content": reply}) # 11. 存入历史
            print(f"[AI] {reply}")                                  # 12. 打印 AI 的决策

            if reply.strip().startswith("完成:"):                    # 13. 如果 AI 说"完成" → 跳出内层循环
                break

            if not reply.strip().startswith("命令:"):                # 14. 安全检查：格式不对就结束本轮
                print("[系统] AI 未按命令格式回复，结束当前任务。")
                break

            command = reply.strip().split("命令:", 1)[1].strip()     # 15. 提取 AI 想执行的命令
            if not command:
                print("[系统] 命令为空，跳过执行。")
                continue

            completed = subprocess.run(                             # 16. 执行命令
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            result = completed.stdout
            if completed.stderr:
                result += "\n[stderr]\n" + completed.stderr        # 错误输出也反馈给 AI
            print(f"[系统] {result}")                                # 17. 打印命令结果
            messages.append({"role": "user", "content": f"执行完毕:{result}"})  # 18. 把结果反馈给 AI
