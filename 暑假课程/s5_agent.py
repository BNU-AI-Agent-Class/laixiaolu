import os                                                           # 0. 用于读取环境变量、脚本路径和执行命令
import subprocess                                                    # 0.5 用于执行命令并指定编码
import sys
sys.stdout.reconfigure(encoding='utf-8')                            # 解决 Windows 终端中文乱码

from dotenv import load_dotenv
_script_dir = os.path.dirname(os.path.abspath(__file__))            # 获取脚本所在目录
load_dotenv(os.path.join(_script_dir, "..", ".env"))                # 1. 读取上层目录 .env 中的 API 密钥

from openrouter import OpenRouter                                   # 2. 导入 OpenRouter SDK

# s5: 加专业 Skill
# 要点：同一个 Agent，换知识包。
# 做法：再建一个 skill.md，system = agent.md + skill.md，测一个领域任务。
# 例如用户研究、导师、教练。

with open(os.path.join(_script_dir, "agent.md"), encoding="utf-8") as f:
    agent_prompt = f.read()                                         # 3. 读取基础行为规则
with open(os.path.join(_script_dir, "skill.md"), encoding="utf-8") as f:
    skill_prompt = f.read()                                         # 4. 读取领域知识包

system_prompt = agent_prompt + "\n\n--- 领域技能 ---\n\n" + skill_prompt  # 5. 拼接成完整系统提示词

with OpenRouter(                                                    # 6. 创建客户端
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    messages = [{"role": "system", "content": system_prompt}]       # 7. 用 agent.md + skill.md 作为系统提示词

    while True:                                                     # 8. 外层循环：等待用户输入新任务
        user_input = input("\n你：")                                 # 9. 等待用户输入
        messages.append({"role": "user", "content": user_input})    # 10. 存入对话历史

        while True:                                                 # 11. 内层循环：Agent 自主执行，直到任务完成
            response = client.chat.send(                            # 12. 发送对话历史给 AI
                model="anthropic/claude-sonnet-4",                  #    可替换为你自己的模型
                messages=messages
            )
            reply = response.choices[0].message.content             # 13. 提取 AI 回复
            messages.append({"role": "assistant", "content": reply}) # 14. 存入历史
            print(f"[AI] {reply}")                                  # 15. 打印 AI 的决策

            if reply.strip().startswith("完成:"):                    # 16. 如果 AI 说"完成" → 跳出内层循环
                break

            if not reply.strip().startswith("命令:"):                # 17. 安全检查：格式不对就结束本轮
                print("[系统] AI 未按命令格式回复，结束当前任务。")
                break

            command = reply.strip().split("命令:", 1)[1].strip()     # 18. 提取 AI 想执行的命令
            if not command:
                print("[系统] 命令为空，跳过执行。")
                continue

            completed = subprocess.run(                             # 19. 执行命令
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
            print(f"[系统] {result}")                                # 20. 打印命令结果
            messages.append({"role": "user", "content": f"执行完毕:{result}"})  # 21. 把结果反馈给 AI
