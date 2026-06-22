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

prompt = f"""今天是{date_str}。请搜索并整理今天各平台的最新优惠活动，**重点覆盖本地吃喝玩乐类的超低价活动**。

要求：
1. 联网搜索以下关键词：
   - 1分钱奶茶 1分钱咖啡 1分钱美食 0.01元饮品
   - 美团 本地生活 秒杀 餐饮折扣 团购特价
   - 饿了么 美食优惠 限时特价 1分钱
   - 抖音 本地生活 团购 探店 超低价套餐
   - 拼多多 限时秒杀 0.01 超低价
   - 淘宝/天猫 限时秒杀 1分钱
   - 京东 限时折扣 超低价
   - 本地吃喝玩乐 今日特价 电影票 火锅 自助餐 低于市场价

2. **排除**领券类活动（满减券、优惠券等）
3. **排除**签到类活动（连续签到领奖励等）
4. **排除**百亿补贴类活动
5. 只保留直接优惠：**1分钱秒杀、低于市场价、直降、限时折扣、团购特价**等
6. **优先收录"1分钱"类活动**（如1分钱奶茶、1分钱咖啡等）
7. **优先收录本地生活类活动**：美团/饿了么的餐饮秒杀、抖音本地团购、电影票特价等
8. **每条活动必须注明是否限新用户**，例如：`限新用户` / `新老用户均可` / `限新用户首单`

9. 按这个格式输出 Markdown：

# {date_str} 各平台优惠活动

## 🍜 本地吃喝玩乐

| 平台 | 活动名称 | 参与方式 | 活动日期 | 限新用户 |
|------|---------|---------|---------|---------|
| 美团 | xxx | xxx | xxx | 是/否 |
| 饿了么 | xxx | xxx | xxx | 是/否 |
| 抖音 | xxx | xxx | xxx | 是/否 |

## 🛒 其他平台

| 平台 | 活动名称 | 参与方式 | 活动日期 | 限新用户 |
|------|---------|---------|---------|---------|
| 淘宝/天猫 | xxx | xxx | xxx | 是/否 |
| 京东 | xxx | xxx | xxx | 是/否 |
| 拼多多 | xxx | xxx | xxx | 是/否 |
| 其他 | xxx | xxx | xxx | 是/否 |

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
