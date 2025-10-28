# Settings Feature - User Guide

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Connecting Your Robinhood Account](#connecting-your-robinhood-account)
4. [Managing Sessions](#managing-sessions)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Overview

The Settings feature provides secure management of your trading platform connections, focusing on Robinhood integration for the Wheel Strategy platform. This module handles authentication, session management, and secure credential storage while maintaining the highest security standards.

### Key Capabilities

- **Secure Authentication**: Connect to Robinhood with encrypted credential handling
- **Session Persistence**: Automatic session caching for seamless reconnection
- **Multi-Factor Authentication**: Full support for 2FA/MFA security
- **Auto-Connection**: Automatic login using environment variables
- **Real-time Status**: Visual connection status indicators

## Quick Start

### Prerequisites

1. **Robinhood Account**: Active trading account with API access enabled
2. **Environment Setup**: Python 3.8+ with required dependencies
3. **Security Setup**: Optional MFA configuration for enhanced security

### Initial Setup

1. **Navigate to the Positions Page**
   - Open the dashboard (`dashboard.py`)
   - Select "Positions" from the sidebar menu
   - The Settings panel will appear at the top

2. **Connection Status Check**
   - Green indicator: Connected and authenticated
   - Yellow indicator: Session cached but not active
   - Red indicator: Not connected

## Connecting Your Robinhood Account

### Method 1: Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# Robinhood Credentials
ROBINHOOD_USERNAME=your_email@example.com
ROBINHOOD_PASSWORD=your_secure_password
ROBINHOOD_MFA_CODE=your_mfa_secret_key  # Optional - for automated MFA
```

**Security Note**: Never commit `.env` files to version control. Add `.env` to your `.gitignore` file.

### Method 2: Manual Connection

1. **Open Settings Panel**
   - Click on "🔗 Robinhood Settings" expander
   - The panel shows connection status and input fields

2. **Enter Credentials**
   - **Username/Email**: Your Robinhood login email
   - **Password**: Your account password
   - **MFA Secret**: Optional - your 2FA secret key (not the 6-digit code)

3. **Connect**
   - Click "Connect to Robinhood" button
   - Wait for authentication to complete
   - Success message confirms connection

### Method 3: Auto-Connection

The system automatically attempts connection when:
- Environment variables are configured
- A valid cached session exists
- You navigate to the Positions page

## Managing Sessions

### Session Lifecycle

```
Initial Login → Session Creation → Token Storage → Auto-Renewal → Expiration
     ↓              ↓                    ↓             ↓              ↓
  Credentials    24hr Token      .pickle file    Refresh API    Re-login
```

### Session Storage

Sessions are stored locally at:
- **Windows**: `%USERPROFILE%\.robinhood_token.pickle`
- **macOS/Linux**: `~/.robinhood_token.pickle`

### Session Features

1. **Automatic Persistence**
   - Sessions last 24 hours (86400 seconds)
   - Cached for instant reconnection
   - Encrypted token storage

2. **Session Status Indicators**
   - 💾 Cached session found - no MFA needed
   - ⚠️ No cached session - MFA may be required
   - ✅ Connected and active
   - 🔄 Refresh available

3. **Manual Session Management**
   - **Refresh**: Click "🔄 Refresh Positions" to update data
   - **Disconnect**: Click "🚪 Disconnect" to logout
   - **Clear Cache**: Delete `.robinhood_token.pickle` file

## Security Best Practices

### 1. Credential Protection

**DO:**
- Use environment variables for credentials
- Enable 2FA on your Robinhood account
- Rotate passwords regularly
- Use strong, unique passwords

**DON'T:**
- Hard-code credentials in source code
- Share `.env` files or session tokens
- Use the same password across platforms
- Store credentials in plain text files

### 2. Environment Variable Security

```bash
# Set restrictive permissions on .env file
# Windows (PowerShell as Administrator)
icacls .env /inheritance:r /grant:r "%USERNAME%:F"

# macOS/Linux
chmod 600 .env
```

### 3. Session Security

- Sessions expire after 24 hours
- Tokens are stored with user-only permissions
- Invalid sessions trigger re-authentication
- No credentials stored in browser/UI state

### 4. Network Security

- All API calls use HTTPS encryption
- Certificate validation enabled
- No proxy bypass for authentication
- Rate limiting prevents brute force

## Troubleshooting

### Common Issues and Solutions

#### 1. "Failed to connect" Error

**Symptoms**: Connection fails despite correct credentials

**Solutions**:
- Verify username/email is correct
- Check password for typos
- Ensure account is not locked
- Try clearing cached session

```bash
# Clear cached session
rm ~/.robinhood_token.pickle  # macOS/Linux
del %USERPROFILE%\.robinhood_token.pickle  # Windows
```

#### 2. MFA Challenges

**Symptoms**: "MFA verification required" message

**Solutions**:
- Check phone/email for verification code
- Enter code when prompted
- For automation, add MFA secret to environment
- Ensure time sync for TOTP codes

#### 3. Session Expiration

**Symptoms**: Sudden disconnection after 24 hours

**Solutions**:
- Normal behavior - sessions expire daily
- Click "Connect" to re-authenticate
- Enable auto-connection via environment variables

#### 4. Auto-Connect Failures

**Symptoms**: Auto-connect not working despite setup

**Solutions**:
```bash
# Verify environment variables are loaded
python -c "import os; print(os.getenv('ROBINHOOD_USERNAME'))"

# Check .env file location (must be in project root)
ls -la .env  # Should show file exists

# Verify dotenv installation
pip install python-dotenv
```

### Error Messages Decoder

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| "Login error: Challenge Required" | MFA needed | Check phone/email for code |
| "Invalid credentials" | Wrong username/password | Verify login details |
| "Rate limit exceeded" | Too many login attempts | Wait 5 minutes before retry |
| "Session expired" | 24-hour limit reached | Re-authenticate |
| "Network error" | Connection issue | Check internet connection |

## FAQ

### Q: Is it safe to store my password in environment variables?

**A:** Environment variables are safer than hard-coding, but for maximum security:
- Use a password manager for the `.env` file
- Set restrictive file permissions
- Consider using system keyring integration
- Never commit `.env` to version control

### Q: Why does my session expire after 24 hours?

**A:** This is a Robinhood security feature. All API sessions expire after 24 hours to prevent unauthorized access. The platform handles re-authentication gracefully.

### Q: Can I connect multiple accounts?

**A:** Currently, the platform supports one Robinhood account at a time. Multi-account support is planned for future releases (see WISHLIST.md).

### Q: What happens to my credentials when I disconnect?

**A:**
- UI fields are cleared immediately
- Session tokens are invalidated
- Cached session file remains (for convenience)
- Environment variables are never modified

### Q: How do I enable MFA automation?

**A:** Add your MFA secret key (not the 6-digit code) to the environment:
1. Get secret key from Robinhood 2FA setup
2. Add to `.env`: `ROBINHOOD_MFA_CODE=your_secret_key`
3. The system will auto-generate TOTP codes

### Q: Can I use this on a shared computer?

**A:** Not recommended. If you must:
1. Never save credentials
2. Always disconnect when done
3. Clear session cache after use
4. Use incognito/private browsing
5. Consider using a separate user account

### Q: What data is sent to Robinhood?

**A:** Only authentication credentials and API requests for:
- Account summary
- Position details
- Option contracts
- Order execution (when implemented)

No data is sent to third parties.

## Best Practices Summary

1. **Always use environment variables** for credential storage
2. **Enable 2FA** on your Robinhood account
3. **Disconnect** when not actively trading
4. **Monitor** session status indicators
5. **Update** credentials after any security incident
6. **Review** connected sessions regularly
7. **Clear** cache when switching accounts

## Support and Resources

- **Security Issues**: Report immediately via secure channels
- **Feature Requests**: See WISHLIST.md for roadmap
- **Architecture Details**: Refer to ARCHITECTURE.md
- **API Specifications**: Check SPEC.md for technical details

---

*Last Updated: January 2025*
*Security Version: 1.0*