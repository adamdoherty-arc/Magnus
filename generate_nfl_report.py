"""
Generate NFL Betting Report - Email and/or Printable HTML/PDF

Usage:
    python generate_nfl_report.py --email       # Send via email
    python generate_nfl_report.py --html        # Generate HTML file
    python generate_nfl_report.py --pdf         # Generate HTML and open for printing
    python generate_nfl_report.py --all         # Do everything
"""

import argparse
import os
import webbrowser
from datetime import datetime
from src.email_game_reports import EmailGameReportService

def generate_html_file(include_all_games: bool = False) -> str:
    """Generate HTML report file"""
    print("Generating NFL betting report...")

    service = EmailGameReportService()
    html_content = service.generate_game_report(include_all_games=include_all_games)

    # Add print-friendly CSS
    html_content = html_content.replace(
        '</style>',
        """
        @media print {
            body { background-color: white !important; }
            .container { box-shadow: none !important; padding: 20px !important; }
            .game-card { page-break-inside: avoid; }
            .no-print { display: none !important; }
        }
        </style>
        """
    )

    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'nfl_betting_report_{timestamp}.html'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    filepath = os.path.abspath(filename)
    print(f"\n✅ Report saved: {filepath}")
    return filepath


def send_email_report(include_all_games: bool = False):
    """Send email report"""
    print("Sending email report...")

    service = EmailGameReportService()
    success = service.send_email_report(include_all_games=include_all_games)

    if success:
        print("\n✅ Email sent successfully!")
    else:
        print("\n❌ Failed to send email. Check .env configuration.")
        print("\nRequired .env variables:")
        print("  SMTP_USERNAME=your@email.com")
        print("  SMTP_PASSWORD=your_app_password")
        print("  EMAIL_TO=recipient@email.com")


def main():
    parser = argparse.ArgumentParser(description='Generate NFL betting reports')
    parser.add_argument('--email', action='store_true', help='Send via email')
    parser.add_argument('--html', action='store_true', help='Generate HTML file')
    parser.add_argument('--pdf', action='store_true', help='Generate HTML and open for printing to PDF')
    parser.add_argument('--all', action='store_true', help='Email + HTML + Open for printing')
    parser.add_argument('--include-all', action='store_true', help='Include all games (not just high-confidence)')

    args = parser.parse_args()

    # If no args, default to --all
    if not any([args.email, args.html, args.pdf, args.all]):
        args.all = True

    print("="*80)
    print("NFL BETTING REPORT GENERATOR")
    print("="*80)
    print()

    filepath = None

    # Generate HTML file
    if args.html or args.pdf or args.all:
        filepath = generate_html_file(include_all_games=args.include_all)

    # Send email
    if args.email or args.all:
        send_email_report(include_all_games=args.include_all)

    # Open for printing
    if (args.pdf or args.all) and filepath:
        print(f"\n📄 Opening report in browser for printing...")
        print("\nTo save as PDF:")
        print("  1. Browser will open")
        print("  2. Press Ctrl+P (or Cmd+P on Mac)")
        print("  3. Select 'Save as PDF' as printer")
        print("  4. Click 'Save'")

        webbrowser.open('file://' + filepath)

    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
