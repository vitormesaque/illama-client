import json
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = (5, 60)
_ALLOWED_RISK = {"low", "medium", "high"}

ILLAMA_INSTRUCTION = (
    "Extract issues from the user review in strict JSON format. "
    "At the top level, provide: severity (1–5), likelihood (1–5), risk_level (low|medium|high), "
    "and category (one of: Bug, User Experience, Performance, Security, Compatibility, Functionality, UI, "
    "Connectivity, Localization, Accessibility, Data Handling, Privacy, Notifications, Account Management, "
    "Payment, Content Quality, Support, Updates, Syncing, Customization). "
    'Also include an array "issues", where each issue has: title, category, severity (1–5), '
    "likelihood (1–5), and risk_level (low|medium|high)."
)

PROMPT_TEMPLATE = """Below is an instruction that describes a task, paired with an input that provides context.

### Instruction:
{instruction}

### Input:
{input}

### Response:
"""

def _extract_first_json_object(text: str) -> Optional[str]:
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "{":
            start = i
            depth = 0
            in_str = False
            esc = False
            i -= 1
            while i + 1 < n:
                i += 1
                ch = text[i]
                if in_str:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        in_str = False
                else:
                    if ch == '"':
                        in_str = True
                    elif ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            return text[start : i + 1]
            return None
        i += 1
    return None

def _safe_json_parse(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except Exception:
        block = _extract_first_json_object(raw)
        if block is not None:
            return json.loads(block)
        raise ValueError("Unable to parse JSON from model response")

def _clamp_int(v: Any, lo: int = 1, hi: int = 5) -> Optional[int]:
    try:
        iv = int(v)
        return max(lo, min(hi, iv))
    except Exception:
        return None

def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "severity" in payload:
        payload["severity"] = _clamp_int(payload["severity"])
    if "likelihood" in payload:
        payload["likelihood"] = _clamp_int(payload["likelihood"])
    if "risk_level" in payload and isinstance(payload["risk_level"], str):
        rl = payload["risk_level"].strip().lower()
        payload["risk_level"] = rl if rl in _ALLOWED_RISK else None
    issues = payload.get("issues")
    if isinstance(issues, list):
        for it in issues:
            if isinstance(it, dict):
                if "severity" in it:
                    it["severity"] = _clamp_int(it["severity"])
                if "likelihood" in it:
                    it["likelihood"] = _clamp_int(it["likelihood"])
                if "risk_level" in it and isinstance(it["risk_level"], str):
                    rl = it["risk_level"].strip().lower()
                    it["risk_level"] = rl if rl in _ALLOWED_RISK else None
    return payload

class IssueExtractor:
    def __init__(self, api_url: str, model: str, timeout=DEFAULT_TIMEOUT, max_retries: int = 5, pool_maxsize: int = 20):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["POST"]),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=pool_maxsize, pool_maxsize=pool_maxsize)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self._headers = {"Content-Type": "application/json"}

    def _build_payload(self, review: str) -> Dict[str, Any]:
        prompt = PROMPT_TEMPLATE.format(instruction=ILLAMA_INSTRUCTION, input=review)
        return {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}

    def extract_issues(self, review: str) -> Union[Dict[str, Any], str]:
        try:
            payload = self._build_payload(review)
            resp = self.session.post(self.api_url, headers=self._headers, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            try:
                body = resp.json()
            except Exception as e:
                return f"Error decoding the response as JSON: {e}"
            raw = body.get("response", body)
            if isinstance(raw, dict):
                parsed = raw
            elif isinstance(raw, str):
                parsed = _safe_json_parse(raw)
            else:
                return "Unexpected response format from API."
            parsed = _normalize_payload(parsed)
            if "review" not in parsed:
                parsed["review"] = review
            return parsed
        except requests.exceptions.RequestException as e:
            return f"Error during API request: {e}"
        except ValueError as e:
            return f"Error decoding JSON: {e}"
        except Exception as e:
            return f"An error occurred: {e}"

def extract_issues(review: str, api_url: str, model: str) -> Union[Dict[str, Any], str]:
    client = IssueExtractor(api_url, model)
    return client.extract_issues(review)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract issues from a user review.")
    parser.add_argument("review", type=str, help="The user review text.")
    parser.add_argument("api_url", type=str, help="The API URL.")
    parser.add_argument("model", type=str, help="The model name.")
    args = parser.parse_args()
    res = extract_issues(args.review, args.api_url, args.model)
    if isinstance(res, dict):
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(res)

if __name__ == "__main__":
    main()
