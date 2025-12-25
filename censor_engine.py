# censor_engine.py
import re
import os
import fnmatch
from config import *
from patterns import RAW_PATTERNS

# --- Kompilacja Regexów przy starcie ---
COMPILED_PATTERNS = []
for rule in RAW_PATTERNS:
    try:
        flags = rule.get("flags", 0)
        regex = re.compile(rule["pattern"], flags)
        COMPILED_PATTERNS.append({"id": rule["id"], "regex": regex})
    except re.error as e:
        print(f"⚠️ Błąd kompilacji regexa {rule['id']}: {e}")


def load_rules():
    """Wczytuje zasady plików/folderów z pliku."""
    restricted_files = []
    restricted_folders = []
    
    if not os.path.exists(RULES_FILE_PATH):
        return [], []

    try:
        current_section = None
        with open(RULES_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line or line.startswith("# --"): 
                if "Files" in line: current_section = "files"
                elif "Folders" in line: current_section = "folders"
                continue
            
            if line.startswith("#"): continue

            if current_section == "files":
                restricted_files.append(line)
            elif current_section == "folders":
                restricted_folders.append(line)
                
    except Exception as e:
        print(f"⚠️ Błąd odczytu zasad: {e}")

    return restricted_files, restricted_folders


def censor_text(text: str) -> tuple[str, bool]:
    """
    Główna funkcja cenzurująca. 
    Kolejność:
    1. Foldery (pvc.rules)
    2. Pliki (pvc.rules)
    3. Wrażliwe dane / Regex
    """
    files, folders = load_rules()
    is_censored = False

    # 1. Cenzura folderów
    for folder in folders:
        if folder.lower() in text.lower():
            pattern = re.compile(re.escape(folder), re.IGNORECASE)
            text = pattern.sub(CENSOR_FOLDER_TAG, text)
            is_censored = True

    # 2. Cenzura plików
    for file_rule in files:
        if '*' in file_rule:
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

    # 3. Cenzura danych wrażliwych (Regexy)
    for rule in COMPILED_PATTERNS:
        if rule["regex"].search(text):
            text = rule["regex"].sub(CENSOR_DATA_TAG, text)
            is_censored = True

    # Dodanie notatki systemowej
    if is_censored and "SYSTEM SECURITY NOTICE" not in text:
        text += SYSTEM_NOTE

    return text, is_censored