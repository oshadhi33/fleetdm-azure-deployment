 
import os
import time
import requests
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin

# ---- Config ----
LAST_SENT_FILE = "/data/last_alert_hash"
RAW_FLEET_URL = os.getenv("FLEET_URL", "").strip()
FLEET_API_TOKEN = os.getenv("FLEET_API_TOKEN", "").strip()
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "").strip()

INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "300"))  # default: 5 minutes
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_HOSTS_LISTED = int(os.getenv("MAX_HOSTS_LISTED", "5"))
PER_PAGE = int(os.getenv("PER_PAGE", "100"))

POLICY_NAME_FILTER = os.getenv("POLICY_NAME_FILTER", "").strip().lower()

def normalize_fleet_base(url: str) -> str:
    """
    Normalizes FLEET_URL to a base like:
      https://mdm.example.com
    If user mistakenly provides .../api/fleet, we'll strip that.
    """
    url = url.rstrip("/")
    for suffix in ("/api/fleet", "/api"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            url = url.rstrip("/")
    return url

FLEET_BASE = normalize_fleet_base(RAW_FLEET_URL)

def must_have_env():
    missing = []
    if not FLEET_BASE:
        missing.append("FLEET_URL")
    if not FLEET_API_TOKEN:
        missing.append("FLEET_API_TOKEN")
    if not SLACK_WEBHOOK:
        missing.append("SLACK_WEBHOOK")
    if missing:
        raise SystemExit(f"Missing required env var(s): {', '.join(missing)}")

SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"Bearer {FLEET_API_TOKEN}",
    "Content-Type": "application/json",
})

def fleet_get(path: str, params: dict | None = None) -> dict:
    url = urljoin(FLEET_BASE + "/", path.lstrip("/"))
    r = SESSION.get(url, params=params, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()

def send_slack(message: str):
    r = requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

def get_policies() -> list[dict]:
    data = fleet_get("/api/v1/fleet/global/policies")
    return data.get("policies", []) or []


def get_failing_hosts(policy_id: int) -> list[dict]:
    data = fleet_get(
        "/api/v1/fleet/hosts",
        params={"policy_id": policy_id, "policy_response": "failing", "per_page": PER_PAGE},
    )
    return data.get("hosts", []) or []


def build_alert_message() -> str | None:
    rows = []


    policies = sorted(get_policies(), key=lambda p: (p.get("name") or "").lower())

    for policy in policies:
        policy_id = policy.get("id")
        if policy_id is None:
            continue

        policy_name = policy.get("name", "Unnamed policy")
        platform_raw = (policy.get("platform") or "").lower()

        if "darwin" in platform_raw or "macos" in platform_raw:
            platform = "macOS"
        elif "windows" in platform_raw:
            platform = "Windows"
        else:
            platform = "Other"

        failing_hosts = get_failing_hosts(int(policy_id))
        if not failing_hosts:
            continue

        rows.append((policy_name, platform, len(failing_hosts)))

    if not rows:
        return None


    rows.sort(key=lambda x: (-x[2], x[0].lower()))


    def trunc(s: str, n: int) -> str:
        return s if len(s) <= n else s[: n - 1] + "…"

    policy_col_width = min(44, max(len("Policy"), max(len(r[0]) for r in rows)))
    platform_col_width = max(len("Platform"), max(len(r[1]) for r in rows))
    failing_col_width = len("Failing")

    header = (
        f"{'Policy'.ljust(policy_col_width)} | "
        f"{'Platform'.ljust(platform_col_width)} | "
        f"{'Failing'.rjust(failing_col_width)}"
    )
    sep = "-" * len(header)

    table_lines = [header, sep]
    for policy_name, platform, fail_count in rows:
        p = trunc(policy_name, policy_col_width).ljust(policy_col_width)
        pl = platform.ljust(platform_col_width)
        fc = str(fail_count).rjust(failing_col_width)
        table_lines.append(f"{p} | {pl} | {fc}")

    now = datetime.now(timezone.utc).astimezone()

    return (
        f":rotating_light: Fleet Policy Alert "
        f"({now.strftime('%Y-%m-%d %H:%M:%S %Z')}):\n\n"
        "```" + "\n".join(table_lines) + "```"
    )

def main():
    must_have_env()
    while True:
        try:
            msg = build_alert_message()
            if msg:
                stable_msg = msg.split("):\n\n", 1)[-1]
           
                msg_hash = hashlib.sha256(msg.encode()).hexdigest()

                try:
                    with open(LAST_SENT_FILE, "r") as f:
                        last_hash = f.read().strip()
                        if last_hash == msg_hash:
                          
                            time.sleep(INTERVAL_SECONDS)
                            continue
                except FileNotFoundError:
          
                    pass

                send_slack(msg)

         
                with open(LAST_SENT_FILE, "w") as f:
                    f.write(msg_hash)

        except Exception as e:
       
            try:
                send_slack(f":warning: fleet-alerts error: `{type(e).__name__}` - {e}")
            except Exception:
        
                print(f"[fleet-alerts] ERROR: {type(e).__name__}: {e}", flush=True)

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
