# config.py

TARGET_HOSTS = [
    "chatgpt.com",
    "chat.openai.com",
    "api.openai.com",
]

RULES_FILE_PATH = r"C:\ProgramData\PVC\rules\pvc.rules"

# Tagi używane do cenzury
CENSOR_FILE_TAG = "[CENZORED_FILE]"
CENSOR_FOLDER_TAG = "[CENZORED_FOLDER]"
CENSOR_DATA_TAG = "[CENZORED_DATA]"

# Notatka systemowa doklejana na końcu promptu
SYSTEM_NOTE = (
    "\n\n[SYSTEM SECURITY NOTICE: Sensitive data, file paths, or API keys in the prompt above "
    "were automatically redacted as [CENZORED_DATA], [CENZORED_FILE], or [CENZORED_FOLDER] "
    "due to security policy. Do not attempt to recover them.]"
)