from mitmproxy import http
import json

TARGET_HOSTS = [
    "chatgpt.com",
    "chat.openai.com",
    "api.openai.com",
]

BLOCK_KEYWORD = "pies"
CENSOR = "[CENZURA]"


def censor_text(text: str) -> str:
    return text.replace(BLOCK_KEYWORD, CENSOR).replace(
        BLOCK_KEYWORD.capitalize(), CENSOR
    )


def extract_prompts(data: dict) -> list[str]:
    prompts = []

    # === RESPONSES API / CODEX ===
    if isinstance(data.get("input"), list):
        for item in data["input"]:
            if not isinstance(item, dict):
                continue

            content = item.get("content")
            if not isinstance(content, list):
                continue

            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    prompts.append(c["text"])

    # === STARE CHAT API ===
    messages = data.get("messages")
    if isinstance(messages, list) and len(messages) > 0:
        last_msg = messages[-1]

        if isinstance(last_msg, dict):
            content = last_msg.get("content")

            if isinstance(content, str):
                prompts.append(content)
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and isinstance(c.get("text"), str):
                        prompts.append(c["text"])

    # === CHATGPT UI (PRZEGLĄDARKA) ===
    if isinstance(data.get("messages"), list):
        for msg in reversed(data["messages"]):
            if not isinstance(msg, dict):
                continue

            content = msg.get("content")
            if not isinstance(content, dict):
                continue

            parts = content.get("parts")
            if isinstance(parts, list):
                for p in parts:
                    if isinstance(p, str):
                        prompts.append(p)
                break  # tylko ostatnia wiadomość użytkownika

    return prompts


def request(flow: http.HTTPFlow):
    host = flow.request.pretty_host

    if not any(h in host for h in TARGET_HOSTS):
        return

    if not flow.request.content:
        return

    try:
        raw_text = flow.request.get_text()
        data = json.loads(raw_text)
    except Exception:
        return

    prompts = extract_prompts(data)
    if not prompts:
        return

    print("\n" + "=" * 80)
    print(f"🎯 ANALIZA PROMPTU ({host})")

    censored = False

    # === LOG ===
    for p in prompts:
        print("— Oryginał:", p)

    # =====================================================
    # 1️⃣ CODEX / RESPONSES API  (ZOSTAWIONE 1:1)
    # =====================================================
    if isinstance(data.get("input"), list):
        for item in data["input"]:
            if not isinstance(item, dict):
                continue

            content = item.get("content")
            if not isinstance(content, list):
                continue

            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    if BLOCK_KEYWORD.lower() in c["text"].lower():
                        c["text"] = censor_text(c["text"])
                        censored = True
                        print("✏️ Codex po cenzurze:", c["text"])

    # =====================================================
    # 2️⃣ STARE CHAT API
    # =====================================================
    if isinstance(data.get("messages"), list) and data["messages"]:
        last_msg = data["messages"][-1]
        content = last_msg.get("content")

        if isinstance(content, str):
            if BLOCK_KEYWORD.lower() in content.lower():
                last_msg["content"] = censor_text(content)
                censored = True
                print("✏️ Chat API po cenzurze:", last_msg["content"])

        elif isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    if BLOCK_KEYWORD.lower() in c["text"].lower():
                        c["text"] = censor_text(c["text"])
                        censored = True
                        print("✏️ Chat API po cenzurze:", c["text"])

    # =====================================================
    # 3️⃣ CHATGPT UI (PRZEGLĄDARKA)
    # =====================================================
    if isinstance(data.get("messages"), list):
        for msg in data["messages"]:
            content = msg.get("content")
            if isinstance(content, dict) and isinstance(content.get("parts"), list):
                new_parts = []
                for p in content["parts"]:
                    if isinstance(p, str) and BLOCK_KEYWORD.lower() in p.lower():
                        p = censor_text(p)
                        censored = True
                        print("✏️ UI po cenzurze:", p)
                    new_parts.append(p)
                content["parts"] = new_parts

    # =====================================================
    # 4️⃣ ZAPIS ZMIAN
    # =====================================================
    if censored:
        flow.request.set_text(json.dumps(data))
        print("🛡️ Prompt ocenzurowany — wysłany dalej")
    else:
        print("✅ Prompt czysty — puszczam dalej")
