# Settings Feature Agent

## Agent Identity

- **Feature Name**: Settings
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Settings Agent is responsible for **secure credential management and platform configuration**, with primary focus on Robinhood authentication and session management. It provides the foundation for all broker-integrated features by handling secure login, session persistence, and connection status monitoring.

### Primary Responsibilities
1. Manage Robinhood authentication (login/logout)
2. Handle session persistence with 24-hour token caching
3. Support Multi-Factor Authentication (MFA/2FA)
4. Provide real-time connection status indicators
5. Enable auto-connection using environment variables
6. Protect credentials with secure storage practices
7. Manage session lifecycle and automatic renewal
8. Display connection health and troubleshooting info

### Security Philosophy
- **Zero Hardcoded Credentials**: All credentials via environment variables
- **Encrypted Storage**: Session tokens stored with encryption
- **No UI Persistence**: Credentials never stored in browser state
- **Automatic Expiration**: 24-hour session limits for security
- **MFA Support**: Full 2FA/TOTP integration

## Feature Capabilities

### What This Agent CAN Do
- ✅ Authenticate with Robinhood using username/password
- ✅ Handle MFA challenges (SMS, email, TOTP)
- ✅ Cache sessions for 24-hour persistence
- ✅ Auto-connect using environment variables
- ✅ Display connection status (connected/disconnected/cached)
- ✅ Refresh positions without re-authentication
- ✅ Disconnect and clear sessions on demand
- ✅ Store session tokens securely (.pickle file)
- ✅ Provide visual status indicators (colored badges)
- ✅ Support manual and automatic connection modes

### What This Agent CANNOT Do
- ❌ Change Robinhood account password (use Robinhood website)
- ❌ Execute trades (only authentication management)
- ❌ Support multiple accounts simultaneously
- ❌ Bypass MFA requirements
- ❌ Store credentials in browser/UI
- ❌ Auto-reconnect beyond 24 hours (security limit)

## Dependencies

### Required Features
- **robin_stocks library**: For Robinhood API integration
- **python-dotenv**: For environment variable loading
- **pickle**: For session token storage

### Optional Features
- **Positions Agent**: Primary consumer of Robinhood connection
- **Dashboard Agent**: Uses connection for portfolio data

### External APIs
- **Robinhood API**: Authentication and session management

## Key Files & Code

### Main Implementation
- `dashboard.py`: Settings UI panel (typically in Positions page)
- `src/robinhood_integration.py`: Robinhood client wrapper
- `.env`: Environment variables for credentials (NOT committed)
- `~/.robinhood_token.pickle`: Session cache file

### Critical Functions
```python
# Authentication
def connect_to_robinhood(username, password, mfa_code=None):
    """
    Login to Robinhood with MFA support
    - Attempts login with credentials
    - Handles MFA challenges
    - Stores session for 24 hours
    - Returns connection status
    """

# Session Management
def check_cached_session():
    """
    Check for valid cached session
    - Looks for .robinhood_token.pickle
    - Validates token expiration
    - Returns session status
    """

# Auto-Connection
def auto_connect_if_configured():
    """
    Automatic connection using environment variables
    - Loads credentials from .env
    - Attempts connection if configured
    - Falls back to manual if needed
    """
```

### Environment Variables (.env)
```bash
# Required for auto-connection
ROBINHOOD_USERNAME=your_email@example.com
ROBINHOOD_PASSWORD=your_secure_password

# Optional - for automated MFA
ROBINHOOD_MFA_CODE=your_mfa_secret_key
```

## Session Lifecycle

```
Initial Login
     ↓
Credentials Entered/Loaded
     ↓
Robinhood API Authentication
     ↓
MFA Challenge (if required)
     ↓
Session Token Generated
     ↓
Token Cached (.pickle file)
     ↓
24-Hour Active Session
     ↓
Auto-Renewal Attempts
     ↓
Session Expires
     ↓
Re-Authentication Required
```

## Session Storage

- **Location**: `~/.robinhood_token.pickle` (user home directory)
- **Lifetime**: 24 hours (86,400 seconds)
- **Security**: User-only file permissions
- **Format**: Encrypted pickle object

## Status Indicators

- 💾 **Cached Session Found** - No MFA needed for reconnection
- ⚠️ **No Cached Session** - MFA may be required
- ✅ **Connected and Active** - Ready for trading operations
- 🔄 **Refresh Available** - Click to update data
- ❌ **Disconnected** - Connection required
- 🚪 **Disconnect** - Logout option available

## Security Best Practices

### DO
- ✅ Use environment variables for credentials
- ✅ Enable 2FA on Robinhood account
- ✅ Rotate passwords regularly
- ✅ Set restrictive permissions on .env file
- ✅ Disconnect when not actively trading
- ✅ Monitor session status regularly
- ✅ Clear cache when switching accounts

### DON'T
- ❌ Hard-code credentials in source code
- ❌ Commit .env files to version control
- ❌ Share session tokens with others
- ❌ Use the same password across platforms
- ❌ Store credentials in browser/UI state
- ❌ Use auto-connection on shared computers

## Error Handling

### Common Issues

1. **"Failed to connect" Error**
   - Verify username/email is correct
   - Check password for typos
   - Ensure account is not locked
   - Clear cached session and retry

2. **"MFA verification required"**
   - Check phone/email for verification code
   - Enter code when prompted
   - For automation, add MFA secret to .env
   - Ensure time sync for TOTP codes

3. **"Session expired"**
   - Normal behavior - sessions expire after 24 hours
   - Click "Connect" to re-authenticate
   - Enable auto-connection via environment variables

4. **"Rate limit exceeded"**
   - Too many login attempts
   - Wait 5 minutes before retry
   - Check for repeated failed attempts

## Performance Metrics

| Operation | Target | Current |
|-----------|--------|---------|
| Login (no MFA) | < 2s | ~1.5s |
| Login (with MFA) | < 5s | ~3s |
| Cached session check | < 100ms | ~50ms |
| Auto-connect | < 3s | ~2s |
| Disconnect | < 500ms | ~200ms |

## Questions This Agent CAN Answer

1. "Am I connected to Robinhood?"
2. "How do I connect my Robinhood account?"
3. "Where are my credentials stored?"
4. "How long does my session last?"
5. "Can I use environment variables for auto-login?"
6. "How do I enable MFA automation?"
7. "What happens when I disconnect?"
8. "Where is the session token stored?"

## Questions This Agent CANNOT Answer

1. "What are my current positions?" → Positions Agent
2. "Execute this trade for me" → Not a trading agent
3. "Change my Robinhood password" → Use Robinhood website
4. "Support multiple accounts" → Single account only (currently)
5. "Why is my account locked?" → Contact Robinhood support
6. "Bypass two-factor authentication" → Security requirement

---

**For detailed information, see:**
- [README.md](./README.md)
- Security best practices documentation

**Security Note**: This agent handles sensitive credentials. Always follow security best practices and never share your credentials or session tokens.
