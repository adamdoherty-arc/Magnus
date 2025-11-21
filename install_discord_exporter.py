"""
Install DiscordChatExporter
"""
import requests
import zipfile
import os
from pathlib import Path

def install_discord_exporter():
    # Get latest release
    print("Fetching latest DiscordChatExporter release...")
    api_url = "https://api.github.com/repos/Tyrrrz/DiscordChatExporter/releases/latest"
    response = requests.get(api_url)
    release_data = response.json()

    # Find CLI zip download URL for Windows x64
    download_url = None
    for asset in release_data.get('assets', []):
        if 'Cli.win-x64.zip' in asset['name']:
            download_url = asset['browser_download_url']
            print(f"Found: {asset['name']}")
            break

    if not download_url:
        print("ERROR: Could not find DiscordChatExporter.Cli.zip in latest release")
        return False

    # Create directory
    install_dir = Path(r"C:\Tools\DiscordChatExporter")
    install_dir.mkdir(parents=True, exist_ok=True)

    # Download
    print(f"Downloading from {download_url}...")
    zip_path = install_dir / "DiscordChatExporter.zip"

    response = requests.get(download_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(zip_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"Progress: {percent:.1f}%", end='\r')

    print(f"\nDownload complete: {zip_path}")

    # Extract
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(install_dir)

    # Clean up zip
    zip_path.unlink()

    # Find the exe
    exe_path = install_dir / "DiscordChatExporter.Cli.exe"
    if not exe_path.exists():
        print(f"ERROR: Could not find DiscordChatExporter.Cli.exe in {install_dir}")
        return False

    print(f"✅ DiscordChatExporter installed successfully!")
    print(f"Location: {exe_path}")

    # Update .env
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"\nUpdating {env_path}...")
        content = env_path.read_text()

        # Update the path
        new_path = f"DISCORD_EXPORTER_PATH={exe_path}"
        if "DISCORD_EXPORTER_PATH=" in content:
            import re
            content = re.sub(
                r'DISCORD_EXPORTER_PATH=.*',
                new_path,
                content
            )
        else:
            content += f"\n{new_path}\n"

        env_path.write_text(content)
        print("✅ .env updated")

    return True


if __name__ == "__main__":
    success = install_discord_exporter()
    if success:
        print("\n" + "="*60)
        print("Installation complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Get Discord channel IDs (right-click channel > Copy ID)")
        print("2. Run: python src/discord_message_sync.py CHANNEL_ID 7")
        print("3. View messages: streamlit run discord_messages_page.py")
    else:
        print("\n❌ Installation failed")
