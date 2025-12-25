from mitmproxy import http
import json
import os
import re
import fnmatch

# === KONFIGURACJA ===
TARGET_HOSTS = [
    "chatgpt.com",
    "chat.openai.com",
    "api.openai.com",
]

RULES_FILE_PATH = r"C:\ProgramData\PVC\rules\pvc.rules"
CENSOR_FILE_TAG = "[CENZORED_FILE]"
CENSOR_FOLDER_TAG = "[CENZORED_FOLDER]"

# Komunikat dla AI, doklejany na końcu, jeśli coś ocenzurowano
SYSTEM_NOTE = (
    "\n\n[SYSTEM SECURITY NOTICE: Some file and folder names above were automatically "
    "redacted as [CENZORED_FILE] or [CENZORED_FOLDER] due to security policy. "
    "Do not look for them, simply assume they exist but are restricted.]"
)

def load_rules():
    """
    Wczytuje zasady z pliku przy każdym wywołaniu.
    Zwraca dwie listy: (files, folders).
    """
    restricted_files = []
    restricted_folders = []
    
    if not os.path.exists(RULES_FILE_PATH):
        print(f"⚠️ Nie znaleziono pliku zasad: {RULES_FILE_PATH}")
        return [], []

    try:
        current_section = None
        with open(RULES_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line or line.startswith("# --"): 
                # Wykrywanie sekcji
                if "Files" in line:
                    current_section = "files"
                elif "Folders" in line:
                    current_section = "folders"
                continue
            
            if line.startswith("#"): # Zwykłe komentarze
                continue

            if current_section == "files":
                restricted_files.append(line)
            elif current_section == "folders":
                restricted_folders.append(line)
                
    except Exception as e:
        print(f"⚠️ Błąd odczytu zasad: {e}")

    return restricted_files, restricted_folders

def censor_text(text: str) -> tuple[str, bool]:
    """
    Cenzuruje tekst na podstawie aktualnych zasad.
    Zwraca: (nowy_tekst, czy_zmieniono)
    """
    files, folders = load_rules()
    is_censored = False
    original_text = text


    for folder in folders:

        if folder.lower() in text.lower():

            pattern = re.compile(re.escape(folder), re.IGNORECASE)
            text = pattern.sub(CENSOR_FOLDER_TAG, text)
            is_censored = True

    for file_rule in files:
        if '*' in file_rule:

            regex_glob = fnmatch.translate(file_rule) 
            ext = file_rule.replace("*", "") 

            pattern_str = r'\b[\w\-\.]+' + re.escape(ext)
            
            matches = re.findall(pattern_str, text, re.IGNORECASE)
            for m in matches:
                text = text.replace(m, CENSOR_FILE_TAG)
                is_censored = True
        else:
   
            if file_rule.lower() in text.lower():
                pattern = re.compile(re.escape(file_rule), re.IGNORECASE)
                text = pattern.sub(CENSOR_FILE_TAG, text)
                is_censored = True


    if is_censored and "SYSTEM SECURITY NOTICE" not in text:
        text += SYSTEM_NOTE

    return text, is_censored

def process_content_structure(data):
    """Przechodzi rekurencyjnie przez JSON i cenzuruje pola tekstowe."""
    censored_any = False


    if isinstance(data.get("input"), list):
        for item in data["input"]:
            if isinstance(item, dict) and isinstance(item.get("content"), list):
                for c in item["content"]:
                    if isinstance(c, dict) and isinstance(c.get("text"), str):
                        new_text, changed = censor_text(c["text"])
                        if changed:
                            c["text"] = new_text
                            censored_any = True
                            print(f"✏️ [CODEX] Ocenzurowano fragment.")


    if isinstance(data.get("messages"), list) and data["messages"]:
        last_msg = data["messages"][-1]
        content = last_msg.get("content")
        
        if isinstance(content, str):
            new_text, changed = censor_text(content)
            if changed:
                last_msg["content"] = new_text
                censored_any = True
                print(f"✏️ [CHAT API] Ocenzurowano wiadomość.")
        
        elif isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    new_text, changed = censor_text(c["text"])
                    if changed:
                        c["text"] = new_text
                        censored_any = True
                        print(f"✏️ [CHAT API MULTIMODAL] Ocenzurowano fragment.")

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
                            print(f"✏️ [UI] Ocenzurowano część wiadomości.")
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
        print("🛡️  PROMPT ZMODYFIKOWANY I WYSŁANY (Zasady wczytane z pvc.rules)")
    else:
        print("✅  Brak danych wrażliwych - prompt czysty.")