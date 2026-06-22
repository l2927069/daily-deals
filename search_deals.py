import json
import os
import re
from datetime import date
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

today = date.today()
date_str = today.isoformat()
filename = f"daily-deals/{date_str}.md"
os.makedirs("daily-deals", exist_ok=True)

# 如果今天已经生成过，跳过
if os.path.exists(filename):
    print(f"{filename} 已存在，跳过")
    exit(0)

prompt = f"""今天是{date_str}。请搜索并整理今天各主流平台的最新优惠活动信息。

要求：
1. 联网搜索以下关键词：
   - 今日羊毛 秒杀 0.01元
   - 淘宝 百亿补贴
   - 京东 百亿补贴
   - 拼多多 限时秒杀
   - 美团 饿了么 优惠
   - 抖音 今日福利

2. 排除领券类活动（满减券、优惠券等）
3. 排除签到类活动（连续签到领奖励等）
4. 只保留直接优惠：0.01元秒杀、百亿补贴价、直降、限时折扣等

5. 按这个格式输出 Markdown：

# {date_str} 各平台优惠活动

| 平台 | 活动名称 | 参与方式 | 活动日期 | 备注 |
|------|---------|---------|---------|------|
| 淘宝/天猫 | xxx | 直接下单 | xxx | xxx |
| 京东 | xxx | xxx | xxx | xxx |
| 拼多多 | xxx | xxx | xxx | xxx |
| 美团 | xxx | xxx | xxx | xxx |
| 饿了么 | xxx | xxx | xxx | xxx |
| 抖音 | xxx | xxx | xxx | xxx |
| 其他 | xxx | xxx | xxx | xxx |

如果当天没有搜到有效活动，如实说明原因。
"""

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是活动信息整理助手，用中文回复。"},
        {"role": "user", "content": prompt}
    ],
    stream=False
)

content = response.choices[0].message.content

# 提取表格部分（如果返回内容包含markdown代码块）
match = re.search(r'```(?:markdown)?\n(.*?)```', content, re.DOTALL)
if match:
    content = match.group(1).strip()

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ 已生成: {filename}")
print(f"   文件大小: {len(content)} 字符")
