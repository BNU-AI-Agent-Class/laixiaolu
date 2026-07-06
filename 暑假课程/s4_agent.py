import os                                                           # 0. 用于读取环境变量、脚本路径和执行命令
import subprocess                                                    # 0.5 用于执行命令并指定编码
import sys
sys.stdout.reconfigure(encoding='utf-8')                            # 解决 Windows 终端中文乱码

from dotenv import load_dotenv
_script_dir = os.path.dirname(os.path.abspath(__file__))            # 获取脚本所在目录
load_dotenv(os.path.join(_script_dir, "..", ".env"))                # 1. 读取上层目录 .env 中的 API 密钥

from openrouter import OpenRouter                                   # 2. 导入 OpenRouter SDK

# s4: 把规则放进 md
# 要点：系统提示词不再写死。
# 做法：新建 agent.md，open("agent.md").read()，其他循环基本不变。
# 改能力时先改文档。

with open(os.path.join(_script_dir, "agent.md"), encoding="utf-8") as f:
    system_prompt = f.read()                                        # 3. 从 agent.md 读取系统提示词

with OpenRouter(                                                    # 4. 创建客户端
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    messages = [{"role": "system", "content": system_prompt}]       # 5. 用外置文档作为系统提示词

    while True:                                                     # 6. 外层循环：等待用户输入新任务
        user_input = input("\n你：")                                 # 7. 等待用户输入
        messages.append({"role": "user", "content": user_input})    # 8. 存入对话历史

        while True:                                                 # 9. 内层循环：Agent 自主执行，直到任务完成
            response = client.chat.send(                            # 10. 发送对话历史给 AI
                model="anthropic/claude-sonnet-4",                  #    可替换为你自己的模型
                messages=messages
            )
            reply = response.choices[0].message.content             # 11. 提取 AI 回复
            messages.append({"role": "assistant", "content": reply}) # 12. 存入历史
            print(f"[AI] {reply}")                                  # 13. 打印 AI 的决策

            if reply.strip().startswith("完成:"):                    # 14. 如果 AI 说"完成" → 跳出内层循环
                break

            if not reply.strip().startswith("命令:"):                # 15. 安全检查：格式不对就结束本轮
                print("[系统] AI 未按命令格式回复，结束当前任务。")
                break

            command = reply.strip().split("命令:", 1)[1].strip()     # 16. 提取 AI 想执行的命令
            if not command:
                print("[系统] 命令为空，跳过执行。")
                continue

            completed = subprocess.run(                             # 17. 执行命令
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
            print(f"[系统] {result}")                                # 18. 打印命令结果
            messages.append({"role": "user", "content": f"执行完毕:{result}"})  # 19. 把结果反馈给 AI
