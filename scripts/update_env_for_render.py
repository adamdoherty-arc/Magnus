"""
Update .env file with Render PostgreSQL credentials
"""
import re
import os
from urllib.parse import urlparse

def parse_postgres_url(url):
    """Parse PostgreSQL connection URL"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:],  # Remove leading /
        'user': parsed.username,
        'password': parsed.password
    }

def update_env_file(render_url):
    """Update .env file with new Render credentials"""

    print("🔄 Parsing Render connection string...")
    creds = parse_postgres_url(render_url)

    print(f"✅ Parsed credentials:")
    print(f"   Host: {creds['host']}")
    print(f"   Port: {creds['port']}")
    print(f"   Database: {creds['database']}")
    print(f"   User: {creds['user']}")
    print(f"   Password: {'*' * len(creds['password'])}")
    print()

    # Read current .env
    env_path = '.env'
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Backup original .env
    backup_path = '.env.backup'
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    print(f"💾 Backed up original .env to {backup_path}")

    # Update lines
    updated_lines = []
    updated_keys = set()

    for line in lines:
        if line.startswith('DB_HOST='):
            updated_lines.append(f'DB_HOST={creds["host"]}\n')
            updated_keys.add('DB_HOST')
        elif line.startswith('DB_PORT='):
            updated_lines.append(f'DB_PORT={creds["port"]}\n')
            updated_keys.add('DB_PORT')
        elif line.startswith('DB_NAME='):
            updated_lines.append(f'DB_NAME={creds["database"]}\n')
            updated_keys.add('DB_NAME')
        elif line.startswith('DB_USER='):
            updated_lines.append(f'DB_USER={creds["user"]}\n')
            updated_keys.add('DB_USER')
        elif line.startswith('DB_PASSWORD='):
            updated_lines.append(f'DB_PASSWORD={creds["password"]}\n')
            updated_keys.add('DB_PASSWORD')
        elif line.startswith('DATABASE_URL='):
            updated_lines.append(f'DATABASE_URL={render_url}\n')
            updated_keys.add('DATABASE_URL')
        elif line.startswith('PGHOST='):
            updated_lines.append(f'PGHOST={creds["host"]}\n')
            updated_keys.add('PGHOST')
        elif line.startswith('PGPORT='):
            updated_lines.append(f'PGPORT={creds["port"]}\n')
            updated_keys.add('PGPORT')
        elif line.startswith('PGDATABASE='):
            updated_lines.append(f'PGDATABASE={creds["database"]}\n')
            updated_keys.add('PGDATABASE')
        elif line.startswith('PGUSER='):
            updated_lines.append(f'PGUSER={creds["user"]}\n')
            updated_keys.add('PGUSER')
        elif line.startswith('PGPASSWORD='):
            updated_lines.append(f'PGPASSWORD={creds["password"]}\n')
            updated_keys.add('PGPASSWORD')
        else:
            updated_lines.append(line)

    # Write updated .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    print(f"✅ Updated {len(updated_keys)} variables in .env:")
    for key in sorted(updated_keys):
        print(f"   ✓ {key}")

    print()
    print("🎉 .env file updated successfully!")
    print()
    print("🚀 Next step: Test connection with test_render_connection.bat")

if __name__ == '__main__':
    print("=" * 60)
    print("AVA - Update .env for Render")
    print("=" * 60)
    print()

    render_url = input("Paste your Render connection string: ").strip()

    if not render_url:
        print("❌ No connection string provided")
        exit(1)

    if not render_url.startswith('postgresql://'):
        print("❌ Invalid connection string. Must start with postgresql://")
        exit(1)

    print()
    confirm = input("Update .env file? (yes/no): ").lower()

    if confirm == 'yes':
        update_env_file(render_url)
    else:
        print("❌ Cancelled")
