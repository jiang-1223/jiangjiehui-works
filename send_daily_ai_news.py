#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# 从环境变量读取凭证
qq_email = os.getenv('QQ_EMAIL_ACCOUNT')
qq_auth_code = os.getenv('QQ_EMAIL_AUTH_CODE')

if not qq_email or not qq_auth_code:
    print("❌ 错误：缺少环境变量 QQ_EMAIL_ACCOUNT 或 QQ_EMAIL_AUTH_CODE")
    exit(1)

# 邮件内容
recipient = "1760893265@qq.com"
subject = "📡 今日AI动态 | 小龙虾·AI编程·具身智能 [4月3日]"

body = """📡 今日AI动态速递 | 2026年4月3日（周五）

侧重方向：小龙虾 / AI Coding / 具身智能

━━━━━━━━━━━━━━━━━━━━━━━━━━
🦞 【1】中国AI周调用量超越美国，3月彻底"变天"
━━━━━━━━━━━━━━━━━━━━━━━━━━
事件：3月份中国大模型周调用量突破7.359万亿Token，连续三周超过美国，创历史纪录。智能体AI（Agent）已从"执行工具"升级为"数字伙伴"，国产AI实现集群式崛起。

值得关注：这是中美AI竞赛格局转变的信号性节点。以WorkBuddy、QClaw等为代表的国产小龙虾生态，正是推动这一数字飙升的重要力量之一。

━━━━━━━━━━━━━━━━━━━━━━━━━━
💻 【2】Anthropic报告：2026年人类最大一次"编程革命"势不可挡
━━━━━━━━━━━━━━━━━━━━━━━━━━
事件：Anthropic发布2026年AI编码趋势报告，核心结论：编程门槛正在消失，非技术人员也能自主开发工具；AI智能体将组成"协同军团"，实现长时间自主开发；人类角色转向战略监督，软件开发周期被大幅压缩。

值得关注：这预示AI Coding赛道将从"辅助编程"迈向"自主开发"，Claude Code、Cursor等工具的竞争将更激烈，国产AI编程工具的窗口期正在加速压缩。

━━━━━━━━━━━━━━━━━━━━━━━━━━
🦞 【3】QClaw vs WorkBuddy 深度对比出炉：同是腾讯"小龙虾"差异解析
━━━━━━━━━━━━━━━━━━━━━━━━━━
事件：有深度测评文章对腾讯旗下两款小龙虾产品QClaw和WorkBuddy进行了对比分析（全文7715字）。两款产品均于2026年3月发布，但定位有所差异：WorkBuddy偏全场景智能体（企业级+个人），QClaw主打轻量快用。

值得关注：腾讯同时推两个"小龙虾"产品，显示其在AI Agent市场的布局策略正在多元化，用户选择有了新的参考维度。

━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 【4】GPT-5.4 vs Claude 4.6 vs Gemini 3.1 三大旗舰同期决战
━━━━━━━━━━━━━━━━━━━━━━━━━━
事件：3月底，OpenAI的GPT-5.4、Anthropic的Claude 4.6和Google的Gemini 3.1 Pro几乎同期发布，覆盖SWE-Bench编程、GPQA推理、多模态识别等多维度评分。其中Gemini 3以94.6分暂居领先，ChatGPT创作能力强，Claude 4稳定合规。

值得关注：三大模型近乎同时"放大招"，AI Coding能力对比迎来最直接的竞争，开发者的工具选型将在近期迎来重新洗牌。

━━━━━━━━━━━━━━━━━━━━━━━━━━
🦾 【5】具身智能首份强制标准发布：6月1日起正式实施
━━━━━━━━━━━━━━━━━━━━━━━━━━
事件：工信部发布具身智能领域首份强制性行业标准（含静态定位误差≤0.1°、动态响应等核心指标），6月1日起强制实施。同日，阿里发布Qwen3.5-Omni全模态大模型，视听理解能力超越Gemini-3.1。

值得关注：强制标准落地意味着具身智能正式从"概念竞争"走向"规范竞争"，对头部企业（智元、优必选、宇树）影响深远，产业化加速信号明确。

━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 今日重点一句话总结
→ 中国AI Agent调用量超越美国，三大顶级模型正面决战，具身智能强制标准落地——4月的AI战场，比想象的更激烈！

━━━━━━━━━━━━━━━━━━━━━━━━━━
🦐 虾米宝宝每日AI动态 · 自动推送
📅 2026年4月3日 08:00"""

# 创建邮件
msg = MIMEMultipart()
msg['From'] = qq_email
msg['To'] = recipient
msg['Subject'] = subject

msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 发送邮件
try:
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(qq_email, qq_auth_code)
    server.send_message(msg)
    server.quit()
    import sys
    sys.stdout.buffer.write(f"[OK] 邮件已成功发送到 {recipient}\n".encode('utf-8'))
    sys.stdout.buffer.write(f"[OK] 主题：{subject}\n".encode('utf-8'))
except Exception as e:
    import sys
    sys.stdout.buffer.write(f"[ERROR] 邮件发送失败：{str(e)}\n".encode('utf-8'))
    exit(1)
