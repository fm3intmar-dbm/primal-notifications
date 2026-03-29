"""
PRIMAL Protocol + INVICTUS Mantra — Pushover Notification System
Handles all scheduled notifications:
  - INVICTUS mantra alerts (5 per day, time-specific)
  - PRIMAL daily morning briefing (1 per day)

Called by GitHub Actions with a TYPE argument:
  python notify.py mantra_morning_full
  python notify.py mantra_midday_full
  python notify.py mantra_evening_pillars
  python notify.py mantra_weekend_morning_full
  python notify.py mantra_weekend_afternoon_full
  python notify.py primal_daily_briefing
"""

import sys
import os
import requests
from datetime import date, timedelta

# ── Credentials (injected as GitHub Actions secrets) ──────────────────────────
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN", "aimbbvi6n2d4k8a9hwe9f41oiuofq7")
PUSHOVER_USER  = os.environ.get("PUSHOVER_USER",  "uxf5tp9d5ksbsqizc2g85aw76p24q8")

# ── INVICTUS Mantra Text ───────────────────────────────────────────────────────
FULL_INVICTUS = """INVICTUS

1. Forge the Body
"I am forging a lean, resilient self through daily cardio, regular stretching, and weekly workouts."
INVICTUS

2. Improve My Health
"I am cycling between healthy eating, keto, and fasting to improve health, increase energy, and optimize metabolism."
INVICTUS

3. Fuel the Mind
"I am fueling my mind by learning new ideas, testing different strategies, and building on synergic systems that move me forward."
INVICTUS

4. Building a Brand
"I am building a sustainable brand by blending evergreen inspiration with event-driven passion for country, sport, and competition."
INVICTUS

I am the master of my fate. I am the captain of my soul.
I am unconquerable, resilient, and strong.
INVICTUS"""

PILLARS_ONLY = """1. Forge the Body
"I am forging a lean, resilient self through daily cardio, regular stretching, and weekly workouts."

2. Improve My Health
"I am cycling between healthy eating, keto, and fasting to improve health, increase energy, and optimize metabolism."

3. Fuel the Mind
"I am fueling my mind by learning new ideas, testing different strategies, and building on synergic systems that move me forward."

4. Building a Brand
"I am building a sustainable brand by blending evergreen inspiration with event-driven passion for country, sport, and competition.\""""

# ── PRIMAL Protocol — 14-Day Cycle Definition ─────────────────────────────────
# Cycle starts Monday April 6, 2026 (Day 1 = Monday of Week 1)
CYCLE_START = date(2026, 4, 6)

# Each entry: (day_label, day_type, nutrition_phase, eating_block, training, wake_time, notes)
CYCLE = [
    # Week 1
    {
        "label": "Week 1 — Monday",
        "day_type": "Off Day / Carb Load",
        "nutrition": "Carb Phase",
        "eating_block": "Short Block (4:30–8:30 PM)",
        "training": "Rest — no training today",
        "wake": "6:45 AM",
        "notes": "Fast until 4:30 PM. Glycogen loading for Tuesday's heavy session. MCT oil as needed."
    },
    {
        "label": "Week 1 — Tuesday",
        "day_type": "Heavy Session",
        "nutrition": "Carb Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 7:00–8:45 AM — fasted training",
        "wake": "6:00 AM",
        "notes": "Pre-workout stack 20–30 min before gym. Protein smoothie immediately post-workout. PRIMAL protocol 30–60 min after smoothie."
    },
    {
        "label": "Week 1 — Wednesday",
        "day_type": "Active Recovery",
        "nutrition": "Carb Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Active Recovery 7:00–8:00 AM — light cardio, stretching, calisthenics",
        "wake": "6:00 AM",
        "notes": "PRIMAL protocol at start of eating window (10:30 AM)."
    },
    {
        "label": "Week 1 — Thursday",
        "day_type": "Heavy Session",
        "nutrition": "Keto Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 7:00–8:45 AM — fasted training",
        "wake": "6:00 AM",
        "notes": "Pre-workout stack 20–30 min before gym. Protein smoothie post-workout. PRIMAL protocol 30–60 min after smoothie. Keto meals only after smoothie."
    },
    {
        "label": "Week 1 — Friday",
        "day_type": "Active Recovery",
        "nutrition": "Keto Phase",
        "eating_block": "Short Block (4:30–8:30 PM)",
        "training": "Active Recovery 7:00–8:00 AM — fasted",
        "wake": "6:00 AM",
        "notes": "Fast until 4:30 PM. MCT oil as needed. PRIMAL protocol at 4:30 PM when eating window opens."
    },
    {
        "label": "Week 1 — Saturday",
        "day_type": "Heavy Session",
        "nutrition": "Carb Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 1:00–2:45 PM — fed training",
        "wake": "6:45 AM",
        "notes": "Eating window opens 10:30 AM. PRIMAL protocol at 10:30 AM. Eat first meal 2–3 hrs before 1:00 PM workout."
    },
    {
        "label": "Week 1 — Sunday",
        "day_type": "Heavy Session",
        "nutrition": "Keto Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 1:00–2:45 PM — fed training",
        "wake": "6:45 AM",
        "notes": "Eating window opens 10:30 AM. PRIMAL protocol at 10:30 AM. Last meal closes eating window at 8:30 PM — extended fast begins."
    },
    # Week 2
    {
        "label": "Week 2 — Monday",
        "day_type": "FULL FAST DAY",
        "nutrition": "Fast Phase",
        "eating_block": "Fast Block — NO eating today",
        "training": "Rest — no training today",
        "wake": "6:45 AM",
        "notes": "Extended fast continues from Sunday evening. PRIMAL protocol in morning. MCT oil permitted. Water + electrolytes all day."
    },
    {
        "label": "Week 2 — Tuesday",
        "day_type": "Active Recovery / Fast Break",
        "nutrition": "Carb Phase",
        "eating_block": "Flexible (break fast 8:00 AM–noon)",
        "training": "Active Recovery 7:00–8:00 AM — still fasted",
        "wake": "6:00 AM",
        "notes": "~36 hrs into extended fast. Break fast between 8 AM–noon with protein-forward + carb meal. PRIMAL protocol when you break the fast."
    },
    {
        "label": "Week 2 — Wednesday",
        "day_type": "Heavy Session",
        "nutrition": "Carb Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 7:00–8:45 AM — fasted training",
        "wake": "6:00 AM",
        "notes": "Pre-workout stack 20–30 min before gym. Protein smoothie post-workout. PRIMAL protocol 30–60 min after smoothie."
    },
    {
        "label": "Week 2 — Thursday",
        "day_type": "Active Recovery",
        "nutrition": "Keto Phase",
        "eating_block": "Short Block (4:30–8:30 PM)",
        "training": "Active Recovery 7:00–8:00 AM — fasted",
        "wake": "6:00 AM",
        "notes": "Fast until 4:30 PM. MCT oil as needed. PRIMAL protocol at 4:30 PM when eating window opens."
    },
    {
        "label": "Week 2 — Friday",
        "day_type": "Heavy Session",
        "nutrition": "Carb Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 7:00–8:45 AM — fasted training",
        "wake": "6:00 AM",
        "notes": "Pre-workout stack 20–30 min before gym. Protein smoothie post-workout. PRIMAL protocol 30–60 min after smoothie."
    },
    {
        "label": "Week 2 — Saturday",
        "day_type": "Heavy Session",
        "nutrition": "Carb Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 1:00–2:45 PM — fed training",
        "wake": "6:45 AM",
        "notes": "Eating window opens 10:30 AM. PRIMAL protocol at 10:30 AM. Eat first meal 2–3 hrs before 1:00 PM workout."
    },
    {
        "label": "Week 2 — Sunday",
        "day_type": "Heavy Session",
        "nutrition": "Keto Phase",
        "eating_block": "Extended Block (10:30 AM–8:30 PM)",
        "training": "Gym 1:00–2:45 PM — fed training",
        "wake": "6:45 AM",
        "notes": "Eating window opens 10:30 AM. PRIMAL protocol at 10:30 AM. Last meal closes at 8:30 PM — cycle resets tomorrow."
    },
]

def get_today_protocol():
    """Calculate which day of the 14-day cycle today falls on."""
    today = date.today()
    delta = (today - CYCLE_START).days
    if delta < 0:
        # Protocol hasn't started yet
        days_until = abs(delta)
        return None, f"PRIMAL Protocol starts in {days_until} day(s) — on {CYCLE_START.strftime('%A, %B %d, %Y')}."
    cycle_day = delta % 14
    return CYCLE[cycle_day], None

def build_primal_message():
    """Build the daily PRIMAL morning briefing message."""
    today = date.today()
    day_data, pre_start_msg = get_today_protocol()

    if pre_start_msg:
        return "PRIMAL Protocol Briefing", pre_start_msg

    title = f"PRIMAL Briefing — {today.strftime('%A, %b %d')}"
    msg = (
        f"{day_data['label']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Day Type: {day_data['day_type']}\n"
        f"Nutrition: {day_data['nutrition']}\n"
        f"Eating Block: {day_data['eating_block']}\n"
        f"Training: {day_data['training']}\n"
        f"Wake: {day_data['wake']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{day_data['notes']}"
    )
    return title, msg

def send_pushover(title, message, priority=0, sound="pushover"):
    """Send a notification via Pushover API."""
    payload = {
        "token":   PUSHOVER_TOKEN,
        "user":    PUSHOVER_USER,
        "title":   title,
        "message": message,
        "priority": priority,
        "sound":   sound,
    }
    r = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=10)
    if r.status_code == 200:
        print(f"[OK] Sent: {title}")
    else:
        print(f"[ERROR] {r.status_code}: {r.text}")
        sys.exit(1)

# ── Dispatch ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python notify.py <notification_type>")
        sys.exit(1)

    ntype = sys.argv[1].lower()

    if ntype == "mantra_morning_full":
        send_pushover("INVICTUS — Morning", FULL_INVICTUS, priority=0, sound="bugle")

    elif ntype == "mantra_midday_full":
        send_pushover("INVICTUS — Midday", FULL_INVICTUS, priority=0, sound="bugle")

    elif ntype == "mantra_evening_pillars":
        send_pushover("INVICTUS — Evening Pillars", PILLARS_ONLY, priority=0, sound="bugle")

    elif ntype == "mantra_weekend_morning_full":
        send_pushover("INVICTUS — Weekend Morning", FULL_INVICTUS, priority=0, sound="bugle")

    elif ntype == "mantra_weekend_afternoon_full":
        send_pushover("INVICTUS — Weekend Afternoon", FULL_INVICTUS, priority=0, sound="bugle")

    elif ntype == "primal_daily_briefing":
        title, msg = build_primal_message()
        send_pushover(title, msg, priority=0, sound="magic")

    else:
        print(f"Unknown notification type: {ntype}")
        sys.exit(1)
