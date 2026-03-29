# PRIMAL Protocol + INVICTUS — Pushover Notifications

Automated Pushover push notifications for the PRIMAL Metabolic Cycle protocol and INVICTUS mantra reminders, scheduled via GitHub Actions.

## What This Does

Sends 6 Pushover notifications per day to your phone:

| # | Time (EDT) | Days | Content |
|---|---|---|---|
| 1 | 6:00 AM | Every day | PRIMAL daily briefing (day type, nutrition, training, eating block) |
| 2 | 6:30 AM | Mon–Fri | Full INVICTUS mantra |
| 3 | 10:30 AM | Mon–Fri | Full INVICTUS mantra |
| 4 | 11:00 PM | Mon–Fri | 4 Pillars only |
| 5 | 8:30 AM | Sat–Sun | Full INVICTUS mantra |
| 6 | 4:30 PM | Sat–Sun | Full INVICTUS mantra |

## Setup (One-Time, ~5 Minutes)

### Step 1 — Fork or Create This Repo on GitHub
- Go to github.com and create a **public** repository named `primal-notifications`
- Upload all files from this folder into the repo

### Step 2 — Add Secrets
- In your GitHub repo, go to **Settings → Secrets and variables → Actions**
- Click **New repository secret** and add:
  - Name: `PUSHOVER_TOKEN` | Value: your Pushover API token
  - Name: `PUSHOVER_USER` | Value: your Pushover user key

### Step 3 — Enable Actions
- Go to the **Actions** tab in your repo
- Click **"I understand my workflows, go ahead and enable them"**
- GitHub Actions will now run automatically on the schedule above

### Step 4 — Test It
- Go to **Actions → PRIMAL + INVICTUS Pushover Notifications → Run workflow**
- Select any notification type from the dropdown and click **Run workflow**
- Your phone should receive the notification within 30 seconds

## Notes
- GitHub Actions schedules run in UTC. All times above are converted correctly.
- GitHub may delay scheduled runs by up to ~15 minutes on the free tier.
- The PRIMAL briefing automatically calculates which day of the 14-day cycle it is based on the April 6, 2026 start date.
- Public repos have unlimited free GitHub Actions minutes.
