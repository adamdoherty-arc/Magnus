# Email Game Reports Setup Guide

**Status:** ✅ Ready to configure
**Created:** November 14, 2025

---

## Overview

I've created an automated email reporting system that sends comprehensive game analysis reports directly to your inbox. The report includes:

✅ **Daily game summaries** with AI predictions
✅ **High-confidence betting opportunities** (⚡ highlighted)
✅ **Win probabilities and expected values**
✅ **Clear reasoning** for each recommendation
✅ **Beautiful HTML formatting** (looks great on mobile and desktop)
✅ **Customizable filters** (all games or only high-value opportunities)

---

## Quick Setup (5 Minutes)

### Step 1: Get an App Password for Gmail

If you're using Gmail, you need to create an "App Password" (this is different from your regular Gmail password):

1. Go to your **Google Account** → https://myaccount.google.com
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google," click **2-Step Verification**
4. If not enabled, **enable 2-Step Verification** first
5. Scroll down and click **App passwords**
6. Select app: **Mail**
7. Select device: **Other (Custom name)**
8. Type: **Magnus Betting Reports**
9. Click **Generate**
10. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

**Important:** This password will only be shown once, so copy it immediately!

### Step 2: Update .env File

Open your `.env` file and update these lines:

```ini
# ============================================
# EMAIL REPORTING CONFIGURATION
# ============================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # <- Paste the 16-character app password (no spaces)
EMAIL_FROM=your.email@gmail.com
EMAIL_TO=your.email@gmail.com   # <- Can be different if you want to send to another email
```

**Example:**
```ini
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=h.adam.doherty@gmail.com
SMTP_PASSWORD=xyzw abcd efgh ijkl  # Your actual app password
EMAIL_FROM=h.adam.doherty@gmail.com
EMAIL_TO=h.adam.doherty@gmail.com
```

### Step 3: Test It!

Run the batch file to send a test report:

```bash
send_game_report.bat
```

You should receive an email within 30 seconds with today's game analysis!

---

## Using Other Email Providers

### Microsoft Outlook / Hotmail

```ini
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your.email@outlook.com
SMTP_PASSWORD=your_password_here
EMAIL_FROM=your.email@outlook.com
EMAIL_TO=your.email@outlook.com
```

### Yahoo Mail

```ini
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your.email@yahoo.com
SMTP_PASSWORD=your_app_password  # Yahoo also requires app password
EMAIL_FROM=your.email@yahoo.com
EMAIL_TO=your.email@yahoo.com
```

**Yahoo App Password Setup:**
1. Go to Account Security → https://login.yahoo.com/account/security
2. Scroll to "Generate app password"
3. Select "Other App"
4. Type: "Magnus Reports"
5. Copy the password

---

## What the Email Report Includes

### Email Format

The report is beautifully formatted HTML that looks great on:
- Desktop email clients (Outlook, Apple Mail, Thunderbird)
- Web email (Gmail, Yahoo, Outlook.com)
- Mobile devices (iPhone Mail, Android Gmail)

### Report Sections

**1. Header**
```
🏈 Daily Sports Betting Report
Generated: November 14, 2025 at 2:30 PM
```

**2. Summary Dashboard**
```
Total Games: 74
NFL Games: 15
NCAA Games: 59
High-Confidence Bets: 8
```

**3. Game Cards (Top 20 by Confidence)**

Each game card shows:

**High Confidence (⚡)** - Green border
```
⚡ HIGH CONFIDENCE

Buffalo Bills @ Kansas City Chiefs
24 - 17
Live - 4th Quarter 5:23

🔼 Predicted Winner: Buffalo Bills

Win Probability: 72%
Confidence: 85%
Expected Value: +18.5%

Recommendation: STRONG_BUY

Why:
• ⚡ HIGH CONFIDENCE: 85% confidence with +18.5% expected value
• Late in game (4th Quarter) - high certainty
• Large score differential (7 points)
• Kelly suggests 12.5% of bankroll
• Strong away team advantage: 72% win probability
```

**Medium Confidence** - Blue border
```
GOOD OPPORTUNITY

Minnesota Vikings @ Green Bay Packers
14 - 10
Live - 3rd Quarter 8:45

🔼 Predicted Winner: Minnesota Vikings

Win Probability: 65%
Confidence: 68%
Expected Value: +12.3%

Recommendation: BUY

Why:
• Good opportunity: 68% confidence, +12.3% EV
• Moderate away team edge: 65% to win
• Kelly suggests 8.5% of bankroll
```

**Low Confidence** - Gray border
```
MARGINAL

Detroit Lions @ Chicago Bears
7 - 7
Live - 2nd Quarter 3:12

🔼 Predicted Winner: Detroit Lions

Win Probability: 55%
Confidence: 52%
Expected Value: +3.2%

Recommendation: HOLD

Why:
• Marginal value: +3.2% EV, consider waiting
• Small Kelly bet: 2.5% of bankroll
```

**4. Footer**
```
This report was generated automatically by the Advanced AI Betting System.
All predictions are based on Kelly Criterion and multi-factor analysis.

Disclaimer: This is for informational purposes only. Bet responsibly.
```

---

## Customization Options

### Send Only High-Value Opportunities

By default, the report only includes games with confidence ≥ 70%. To include ALL games:

Edit `send_game_report.bat`:
```batch
python -c "from src.email_game_reports import send_full_report; success = send_full_report(); print('Report sent!' if success else 'Failed to send report')"
```

### Custom Email Subject

Create a Python script `send_custom_report.py`:
```python
from src.email_game_reports import EmailGameReportService

service = EmailGameReportService()
service.send_email_report(
    subject="🏈 Tonight's Game Analysis - Don't Miss These Bets!",
    include_all_games=False
)
```

### Schedule Daily Reports

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Daily Betting Report"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
6. Program: `C:\Code\Legion\repos\ava\send_game_report.bat`
7. Done!

**Linux Cron:**
```bash
0 9 * * * cd /path/to/ava && ./send_game_report.bat
```

---

## Programmatic Usage

### Send Report from Python

```python
from src.email_game_reports import EmailGameReportService

# Create service
service = EmailGameReportService()

# Send high-value opportunities only
service.send_email_report(include_all_games=False)

# Send all games
service.send_email_report(include_all_games=True)

# Custom subject
service.send_email_report(
    subject="🎯 Weekly Betting Analysis - Nov 14-20",
    include_all_games=True
)
```

### Generate HTML Without Sending

```python
from src.email_game_reports import EmailGameReportService

service = EmailGameReportService()
html = service.generate_game_report(include_all_games=False)

# Save to file
with open('report.html', 'w') as f:
    f.write(html)

# Open in browser for preview
import webbrowser
webbrowser.open('file://' + os.path.abspath('report.html'))
```

### Integrate with Real-Time Sync

Add to `src/realtime_betting_sync.py` to send reports after each sync:

```python
from src.email_game_reports import send_daily_report

# At end of sync_all_data()
if results['price_drops_detected'] > 0 or results['alerts_sent'] > 0:
    logger.info("Sending email report...")
    send_daily_report()
```

---

## Troubleshooting

### Error: "SMTP Authentication Failed"

**Solution:**
- Make sure you're using an **App Password**, not your regular password
- Enable 2-Step Verification in Google Account
- Check SMTP_USERNAME is your full email address

### Error: "Connection Refused"

**Solution:**
- Check SMTP_SERVER is correct: `smtp.gmail.com`
- Check SMTP_PORT is: `587`
- Make sure firewall isn't blocking port 587

### Error: "No Email Recipient Configured"

**Solution:**
- Set EMAIL_TO in .env file
- Make sure it's a valid email address

### Email Not Arriving

**Check:**
1. **Spam folder** - First time emails often go to spam
2. **Sent folder** - Verify it actually sent
3. **Email address** - Double-check EMAIL_TO is correct
4. **Quotas** - Gmail has a daily limit of ~500 emails

### Report Shows "AI analysis temporarily unavailable"

**Solution:**
- The advanced AI agent had an error
- Check game_cards_visual_page.py logs
- This is a fallback - report will still generate

---

## Email Report Features

### Mobile-Friendly Design

The HTML report is fully responsive:
- Large, readable fonts on mobile
- Cards stack vertically on small screens
- Touch-friendly links and buttons
- Optimized for iPhone/Android email apps

### Dark Mode Support

Automatically adapts to:
- Gmail dark mode
- iOS dark mode
- Android dark mode

### Accessibility

- Screen reader friendly
- High contrast colors
- Semantic HTML structure
- Alt text for all visual elements

---

## Security Best Practices

✅ **Do:**
- Use App Passwords (not your main password)
- Keep .env file private (it's in .gitignore)
- Use 2-Step Verification
- Review who has access to reports

❌ **Don't:**
- Share your App Password
- Commit .env to git
- Use your main email password
- Send to untrusted email addresses

---

## Advanced Features

### Multiple Recipients

Send to multiple emails:
```python
service = EmailGameReportService()
service.to_email = "email1@gmail.com,email2@yahoo.com,email3@outlook.com"
service.send_email_report()
```

### BCC for Privacy

```python
# In src/email_game_reports.py, add BCC:
msg['Bcc'] = 'private_list@example.com'
```

### Attach Raw Data

```python
# Add CSV attachment
import csv
from email.mime.base import MIMEBase
from email import encoders

# ... generate report ...

# Create CSV
csv_data = "game,predicted_winner,confidence,ev\n"
for game in analyzed_games:
    csv_data += f"{game['away_team']} @ {game['home_team']},"
    csv_data += f"{game['ai_prediction']['predicted_winner']},"
    csv_data += f"{game['ai_prediction']['confidence_score']},"
    csv_data += f"{game['ai_prediction']['expected_value']}\n"

# Attach to email
attachment = MIMEBase('text', 'csv')
attachment.set_payload(csv_data)
encoders.encode_base64(attachment)
attachment.add_header('Content-Disposition', 'attachment', filename='betting_data.csv')
msg.attach(attachment)
```

---

## Example Use Cases

### Morning Briefing

Schedule for 9:00 AM daily:
```
Subject: ☕ Morning Betting Briefing
Content: Top opportunities for today's games
```

### Pre-Game Analysis

Schedule for 1 hour before game time:
```
Subject: 🏈 Kickoff in 1 Hour - Last Minute Picks
Content: Live analysis with latest odds
```

### Weekly Summary

Send every Monday:
```
Subject: 📊 Weekly Betting Performance + This Week's Picks
Content: Last week's results + upcoming opportunities
```

---

## Summary

✅ **Email reporting system created**
✅ **Beautiful HTML formatting**
✅ **AI predictions with reasoning**
✅ **Easy Gmail/Outlook/Yahoo setup**
✅ **Scheduled delivery ready**
✅ **Mobile-friendly design**
✅ **Secure app password authentication**

**Setup Time:** 5 minutes
**Cost:** Free (uses existing email account)
**Frequency:** On-demand or scheduled

---

**Next Steps:**

1. Create Gmail App Password
2. Update .env file
3. Run `send_game_report.bat`
4. Check your inbox!
5. (Optional) Schedule daily reports

**Questions?** Check the troubleshooting section or the inline code comments in `src/email_game_reports.py`.

---

Last Updated: November 14, 2025
