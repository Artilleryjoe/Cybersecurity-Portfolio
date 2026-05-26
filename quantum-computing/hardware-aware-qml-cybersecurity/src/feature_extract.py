import math
from collections import Counter
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = {"login", "verify", "secure", "update", "account", "bank"}

TLD_RISK = {
    "ru": 0.90,
    "tk": 0.95,
    "top": 0.85,
    "xyz": 0.80,
    "com": 0.20,
    "org": 0.20,
    "edu": 0.10,
}


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    probs = [count / len(text) for count in counts.values()]
    return -sum(p * math.log2(p) for p in probs)


def url_features(url: str) -> list[float]:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    combined = f"{host}{path}".strip()

    url_len = len(url)
    depth = path.count("/")
    entropy = shannon_entropy(combined)

    special_count = sum(1 for ch in combined if not ch.isalnum())
    special_ratio = special_count / max(1, len(combined))

    digits = sum(ch.isdigit() for ch in combined)
    letters = sum(ch.isalpha() for ch in combined)
    digit_letter_ratio = digits / max(1, letters)

    keyword_flag = int(any(keyword in combined for keyword in SUSPICIOUS_KEYWORDS))
    tld = host.split(".")[-1] if "." in host else ""
    tld_risk = TLD_RISK.get(tld, 0.50)

    return [url_len, depth, entropy, special_ratio, digit_letter_ratio, keyword_flag, tld_risk]


def email_header_features(record: dict) -> list[float]:
    return [
        int(record.get("spf_pass", 0)),
        int(record.get("dkim_pass", 0)),
        int(record.get("dmarc_pass", 0)),
        float(record.get("received_hops", 0.0)),
        int(record.get("domain_mismatch", 0)),
        float(record.get("interhop_delay_mean", 0.0)),
        float(record.get("ip_rep", 0.5)),
        float(record.get("domain_rep", 0.5)),
    ]
