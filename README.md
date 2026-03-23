---

# 🛡️ Prompt Version Control – Proxy

Prompt-Version-Control-Proxy is the core security layer of the PVC ecosystem.
It acts as a **local AI firewall and policy enforcement engine**, controlling what data can be sent from your machine to external AI systems like Codex or ChatGPT.

It reads project configuration from the `.pvc` directory, connects to your workspace, and enforces rules defined by your organization.

---

## 💡 Overview

The PVC Proxy runs locally and intercepts all communication between your AI tools and external models.

It ensures that **sensitive data never leaves your machine**, based on rules defined in your PVC workspace (e.g. by a team lead or manager).

---

## 🔗 Workspace Integration

The proxy:

* Reads the local `.pvc` folder
* Connects to your PVC workspace (linked via CLI)
* Fetches rules defined in the web/mobile application

These rules can be centrally managed and automatically applied to all connected machines.

---

## 🔐 Policy Enforcement

Managers or organizations can define what is allowed or blocked, including:

* Specific files or folders
* File types
* Code patterns
* API keys and secrets
* Sensitive keywords or data structures

The proxy enforces these rules **in real time**.

---

## 🚫 Data Leakage Prevention

Before any data is sent to an AI model, the proxy:

1. Intercepts the request
2. Scans the content
3. Compares it against workspace rules
4. Blocks or sanitizes the request if needed

Example:

> If a prompt contains an API key or references a restricted file, the proxy will prevent it from being sent to Codex.

---

## ⚙️ Works Across Multiple Interfaces

PVC Proxy is designed to work seamlessly across different AI entry points:

### 🧑‍💻 VS Code (Codex Extension)

* Intercepts prompts sent via the Codex extension
* Protects local development workflows

### 🌐 Web (ChatGPT / similar)

* Works with browser-based AI tools
* Ensures the same policies apply outside the IDE

---

## 🧠 Role in the PVC Ecosystem

PVC Proxy is the enforcement layer:

| Component          | Role                               |
| ------------------ | ---------------------------------- |
| PVC-CLI            | Links project and syncs data       |
| PVC Proxy          | Enforces security rules            |
| PVC Web/Mobile App | Defines policies and displays data |
| Telegram Bot       | Sends alerts                       |

---

## 🏢 Centralized Control

One of the key features of PVC Proxy is **central policy management**:

* A manager defines rules once
* Rules are synced to all connected environments
* Every developer machine enforces the same constraints

This makes PVC suitable for teams and organizations that need **consistent AI usage policies**.

---

## 🎯 Use Cases

* Preventing API key leaks during AI-assisted coding
* Blocking access to sensitive folders or files
* Enforcing company-wide AI usage policies
* Securing both IDE and browser-based AI workflows
* Controlling what context is shared with external models

---

## 🔐 Security Philosophy

PVC Proxy is built on a strict principle:

> If it shouldn’t leave your machine, it won’t.

Instead of trusting AI tools blindly, PVC introduces a **control point** that ensures only safe and approved data is transmitted.

---

## 🧩 Summary

Prompt-Version-Control-Proxy is the **execution layer of PVC security**:

* Reads local project configuration (`.pvc`)
* Syncs with workspace rules
* Intercepts all AI communication
* Blocks sensitive data in real time

It is what turns PVC from a monitoring system into an actual **enforcement system**.

---
