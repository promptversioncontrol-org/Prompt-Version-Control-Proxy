from mitmproxy import http
import json

TARGET_HOSTS = [
    "chatgpt.com",
    "chat.openai.com",
    "api.openai.com",
]

BLOCK_KEYWORD = "pies"

def extract_prompts(data: dict) -> list[str]:
    prompts = []

    # === NOWE RESPONSES API / CODEX (np. dla specyficznych endpointów) ===
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

    # === STANDARDOWE CHAT API (ChatGPT) ===
    # Sprawdzamy tylko OSTATNIĄ wiadomość, aby uniknąć blokowania przez historię rozmowy
    messages = data.get("messages")
    if isinstance(messages, list) and len(messages) > 0:
        last_msg = messages[-1]  # Pobranie ostatniego elementu listy
        
        if isinstance(last_msg, dict):
            content = last_msg.get("content")

            if isinstance(content, str):
                prompts.append(content)
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and isinstance(c.get("text"), str):
                        prompts.append(c["text"])

    return prompts

def request(flow: http.HTTPFlow):
    host = flow.request.pretty_host

    # Sprawdzenie czy host jest na liście
    if not any(h in host for h in TARGET_HOSTS):
        return

    # Sprawdzenie czy body nie jest puste
    if not flow.request.content:
        return

    try:
        data = json.loads(flow.request.get_text())
    except Exception:
        return

    prompts = extract_prompts(data)

    if not prompts:
        return

    # Logowanie w konsoli mitmproxy
    print("\n" + "=" * 80)
    print(f"🎯 ANALIZA PROMPTU ({host}):")
    for p in prompts:
        print("— Treść:", p)

    # === LOGIKA BLOKOWANIA ===
    for p in prompts:
        if BLOCK_KEYWORD.lower() in p.lower():
            print(f"🚫 BLOKADA! Wykryto zakazane słowo: '{BLOCK_KEYWORD}'")

            flow.response = http.Response.make(
                403,
                json.dumps({
                    "error": {
                        "type": "policy_block",
                        "message": f"Prompt blocked by PVC (keyword: {BLOCK_KEYWORD})"
                    }
                }),
                {"Content-Type": "application/json"}
            )
            return

    print("✅ Prompt czysty — puszczam dalej")