# main.py
from mitmproxy import http
import json
from config import TARGET_HOSTS
from censor_engine import censor_text

def process_content_structure(data):
    """Przechodzi rekurencyjnie przez JSON i cenzuruje pola tekstowe."""
    censored_any = False

    # === RESPONSES API / CODEX ===
    if isinstance(data.get("input"), list):
        for item in data["input"]:
            if isinstance(item, dict) and isinstance(item.get("content"), list):
                for c in item["content"]:
                    if isinstance(c, dict) and isinstance(c.get("text"), str):
                        new_text, changed = censor_text(c["text"])
                        if changed:
                            c["text"] = new_text
                            censored_any = True
                            print(f"✏️ [CODEX] Ocenzurowano dane.")

    # === STARE CHAT API ===
    if isinstance(data.get("messages"), list) and data["messages"]:
        last_msg = data["messages"][-1]
        content = last_msg.get("content")
        
        if isinstance(content, str):
            new_text, changed = censor_text(content)
            if changed:
                last_msg["content"] = new_text
                censored_any = True
                print(f"✏️ [CHAT API] Ocenzurowano dane.")
        
        elif isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    new_text, changed = censor_text(c["text"])
                    if changed:
                        c["text"] = new_text
                        censored_any = True
                        print(f"✏️ [CHAT API MULTIMODAL] Ocenzurowano dane.")

    # === CHATGPT UI (PRZEGLĄDARKA) ===
    if isinstance(data.get("messages"), list):
        for msg in data["messages"]:
            content = msg.get("content")
            if isinstance(content, dict) and isinstance(content.get("parts"), list):
                new_parts = []
                for p in content["parts"]:
                    if isinstance(p, str):
                        new_text, changed = censor_text(p)
                        if changed:
                            censored_any = True
                            print(f"✏️ [UI] Ocenzurowano dane.")
                        new_parts.append(new_text)
                    else:
                        new_parts.append(p)
                content["parts"] = new_parts

    return censored_any

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

    print(f"\n🔍 Sprawdzam żądanie do: {host}")
    
    was_censored = process_content_structure(data)

    if was_censored:
        new_payload = json.dumps(data)
        flow.request.set_text(new_payload)
        print("🛡️  PROMPT ZMODYFIKOWANY (Usunięto pliki/foldery lub wykryto sekrety)")
    else:
        print("✅  Prompt czysty.")