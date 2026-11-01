"""
MODULE 4: Institutional Interactive HTML Dashboard Generator (`generate_dashboard.py` v6.0 Audited Zero-Defect Suite).
Reads:
- `data/latest_market_snapshot.json`
- `data/quant_portfolio_analytics.json`
- `05_Learning_And_Evolution/learning_telemetry.json`
- `data/mentor_dashboard_data.json`
- `06_Investor_Academy_And_Mentorship/user_journal/student_profile.json`
- `07_Daily_Investment_Specialist/daily_specialist_ledger.json`
- `data/gatekeeper_audit_report.json`
- `scripts/dashboard_template.html`
Outputs:
- `dashboard/index.html` (Full-featured institutional command center matching user specification v6.0).
"""

import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = BASE_DIR / "data" / "latest_market_snapshot.json"
QUANT_PATH = BASE_DIR / "data" / "quant_portfolio_analytics.json"
LEARNING_PATH = BASE_DIR / "05_Learning_And_Evolution" / "learning_telemetry.json"
MENTOR_DATA_PATH = BASE_DIR / "data" / "mentor_dashboard_data.json"
PROFILE_PATH = BASE_DIR / "06_Investor_Academy_And_Mentorship" / "user_journal" / "student_profile.json"
SPECIALIST_PATH = BASE_DIR / "07_Daily_Investment_Specialist" / "daily_specialist_ledger.json"
GATEKEEPER_PATH = BASE_DIR / "data" / "gatekeeper_audit_report.json"
TEMPLATE_PATH = BASE_DIR / "scripts" / "dashboard_template.html"

DASHBOARD_DIR = BASE_DIR / "dashboard"
DASHBOARD_OUT = DASHBOARD_DIR / "index.html"


def load_opt_json(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def main() -> None:
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    snapshot = load_opt_json(SNAPSHOT_PATH)
    quant = load_opt_json(QUANT_PATH)
    learning = load_opt_json(LEARNING_PATH)
    mentor_data = load_opt_json(MENTOR_DATA_PATH)
    profile = load_opt_json(PROFILE_PATH)
    specialist = load_opt_json(SPECIALIST_PATH)
    gatekeeper = load_opt_json(GATEKEEPER_PATH)

    embedded_data = {
        "snapshot": snapshot,
        "quant": quant,
        "learning": learning,
        "mentor": mentor_data,
        "profile": profile,
        "specialist": specialist,
        "gatekeeper": gatekeeper,
    }
    json_str = json.dumps(embedded_data, ensure_ascii=False)

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.replace("<!-- DATA_JSON_PAYLOAD -->", json_str)

    DASHBOARD_OUT.write_text(html, encoding="utf-8")
    print(f"Done! Institutional Command Center v6.0 Audited saved to: {DASHBOARD_OUT} (Size: {len(html):,} bytes)")


if __name__ == "__main__":
    main()
