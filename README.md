# TIS Enterprise: Safe-Log AI Governance Proxy

## Executive Summary
Safe-Log is a middleware security gateway designed to intercept, sanitize, and audit outbound Large Language Model (LLM) prompts in corporate environments. It prevents the unauthorized exfiltration of proprietary business data, classified assets, and Personally Identifiable Information (PII) to third-party AI services.



## Technical Architecture
The proxy operates as a localized firewall between internal employees and external AI APIs, executing a three-layer verification process on all outbound traffic:
* **Dynamic Database Inspection:** The system connects to a live MySQL database to actively query restricted corporate keywords (e.g., unreleased project codenames). Matches are instantly redacted.
* **Pattern-Based PII Filtering:** The engine utilizes Regular Expressions (Regex) to identify and sanitize sensitive data formats, such as Social Security Numbers, ensuring regulatory compliance.
* **Immutable Audit Logging:** Intercepted policy violations trigger an automated logging protocol. The system writes the employee identifier, original input, and a timestamp to a secure SQL table for CISO review.

---

## Prerequisites
* Python 3.8+
* MySQL Server (or MariaDB)
* Database management tool (e.g., DBeaver)

