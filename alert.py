import os
from datetime import datetime, timedelta, timezone

import requests


DATA_URL = os.getenv(
    "DATA_URL", "https://premium.leo2026.cloud/api/runtime/page?category=qdii-lof"
)
WXPUSHER_URL = "https://wxpusher.zjiecode.com/api/send/message"

APP_TOKEN = os.environ["WXPUSHER_APP_TOKEN"]
UID = os.getenv("WXPUSHER_UID", "UID_ESoc1pNAZNtEBsGrSjbmHQzri9ni")
THRESHOLD = float(os.getenv("PREMIUM_THRESHOLD", "0"))
MAX_ITEMS = int(os.getenv("MAX_ITEMS", "10"))
DEBUG = os.getenv("DEBUG", "").lower() in {"1", "true", "yes"}


def pct(value):
    return f"{value * 100:.2f}%"


def cn_now():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))


def format_num(value, digits=4):
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return "-"


def is_purchase_paused(fund):
    fields = [
        fund.get("purchaseStatus"),
        fund.get("purchaseLimit"),
    ]
    return any("暂停申购" in str(value) for value in fields if value)


def build_message(funds, synced_at):
    candidates = [
        fund
        for fund in funds
        if isinstance(fund.get("premiumRate"), (int, float))
        and fund["premiumRate"] >= THRESHOLD
        and not is_purchase_paused(fund)
    ]
    candidates.sort(key=lambda fund: fund.get("premiumRate") or 0, reverse=True)

    now = cn_now().strftime("%Y-%m-%d %H:%M")
    lines = [f"基金套利提醒 {now}", f"数据时间：{synced_at or '-'}"]

    if not candidates:
        lines.append(f"暂无超过 {pct(THRESHOLD)} 且未暂停申购的 QDII-LOF 溢价机会。")
        return "\n".join(lines)

    lines.append(f"筛选：溢价率 >= {pct(THRESHOLD)}，排除暂停申购，按溢价率降序")
    for fund in candidates[:MAX_ITEMS]:
        lines.extend(
            [
                "",
                f"{fund.get('name') or '-'} ({fund.get('code') or '-'})",
                f"溢价率：{pct(fund['premiumRate'])}",
                f"限购：{fund.get('purchaseLimit') or '-'}",
                f"申赎状态：{fund.get('purchaseStatus') or '-'}",
                f"场内价：{format_num(fund.get('marketPrice'), 3)}",
                f"估算净值：{format_num(fund.get('estimatedNav'), 4)}",
                f"行情时间：{fund.get('marketDate') or '-'} {fund.get('marketTime') or ''}".strip(),
            ]
        )

    return "\n".join(lines)


def fetch_funds():
    response = requests.get(DATA_URL, timeout=20)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"data source returned not ok: {data}")
    return data


def send_message(content):
    response = requests.post(
        WXPUSHER_URL,
        json={
            "appToken": APP_TOKEN,
            "content": content,
            "summary": "基金套利提醒",
            "contentType": 1,
            "uids": [UID],
        },
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()
    if result.get("code") != 1000:
        raise RuntimeError(f"WxPusher send failed: {result}")
    return result


def main():
    data = fetch_funds()
    content = build_message(data.get("funds") or [], data.get("syncedAt"))
    result = send_message(content)

    if DEBUG:
        print(result)
    else:
        records = result.get("data") or []
        message_id = records[0].get("messageId") if records else "-"
        print(f"sent message_id={message_id}")


if __name__ == "__main__":
    main()
