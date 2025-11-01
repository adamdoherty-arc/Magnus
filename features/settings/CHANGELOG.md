# Changelog

All notable changes to the Settings feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-account Robinhood support
- System keyring integration for credential storage
- OAuth 2.0 authentication flow
- Session expiration warnings with auto-refresh
- API usage statistics and rate limit tracking
- Advanced security settings (2FA enforcement)
- Connection health monitoring dashboard
- Automated credential rotation

## [1.0.0] - 2025-10-28

### Added
- **Secure Robinhood Authentication**
  - Username/email and password input
  - Multi-factor authentication (MFA) support
  - TOTP code generation for automation
  - Session token caching for persistence
  - Encrypted credential handling
  - HTTPS-only API communications
- **Session Management System**
  - 24-hour session duration (86400 seconds)
  - Automatic session token storage
  - `.robinhood_token.pickle` file caching
  - Session status indicators
  - Automatic session refresh
  - Graceful session expiration handling
  - Manual disconnect capability
- **Auto-Connection Features**
  - Environment variable credential support
  - Automatic login on page navigation
  - Cached session detection
  - Silent authentication for seamless UX
  - No repeated login prompts
- **Connection Status Display**
  - Real-time connection indicators
  - Visual status colors (green/yellow/red)
  - Session cache notifications
  - MFA requirement warnings
  - Connected/active confirmations
  - Refresh availability indicators
- **Environment Variable Integration**
  - `ROBINHOOD_USERNAME` support
  - `ROBINHOOD_PASSWORD` support
  - `ROBINHOOD_MFA_CODE` support (optional)
  - Secure `.env` file loading
  - python-dotenv integration
  - Zero hardcoded credentials
- **Security Best Practices**
  - Credentials never stored in UI state
  - Tokens encrypted at rest
  - User-only file permissions on cache
  - Certificate validation enabled
  - Rate limiting protection
  - No proxy bypass for auth
- **Settings Panel UI**
  - Expandable settings section
  - Connection status at top of Positions page
  - Username/password input fields
  - MFA secret optional field
  - Connect/disconnect buttons
  - Refresh positions button
  - Clear visual feedback for actions
- **Session Lifecycle Management**
  ```
  Initial Login → Session Creation → Token Storage →
  Auto-Renewal → Expiration → Re-login
  ```
- **Cross-Platform Session Storage**
  - Windows: `%USERPROFILE%\.robinhood_token.pickle`
  - macOS/Linux: `~/.robinhood_token.pickle`
  - Automatic path resolution
  - Consistent behavior across OS
- **Error Handling**
  - Invalid credentials detection
  - MFA challenge handling
  - Network error recovery
  - Session expiration notifications
  - Rate limit warnings
  - Connection timeout handling
- **Security Features**
  - No credentials in browser/UI state
  - Environment variable protection
  - Session token encryption
  - Automatic logout after 24 hours
  - Invalid session triggers re-auth
  - Secure credential storage guidelines

### Technical Implementation
- **Authentication Flow**
  1. Credentials validation
  2. MFA TOTP generation (if configured)
  3. Session creation with Robinhood API
  4. Encrypted token storage to pickle file
  5. Session expiry timestamp tracking
- **Session Persistence**
  - Pickle serialization for token storage
  - File-based caching for 24-hour validity
  - Automatic refresh before expiry
  - Graceful degradation on expiry
- **Integration Points**
  - Positions page for login/logout
  - Robinhood API for all trading operations
  - Dashboard for connection status checks
  - Database features require active session
- **Configuration**
  - `.env` file in project root (recommended)
  - Environment variables via OS
  - Manual input via UI (less secure)
  - MFA secret for automation (optional)

### Security Measures
- **Credential Protection**
  - Environment variables (not hardcoded)
  - 2FA/MFA enabled support
  - Regular password rotation recommended
  - Strong password enforcement
  - Unique passwords across platforms
- **File Permissions**
  - Windows: User-only access via icacls
  - macOS/Linux: chmod 600 on .env
  - Restrictive pickle file permissions
  - No group/other read access
- **Network Security**
  - HTTPS encryption for all API calls
  - Certificate validation mandatory
  - No proxy bypass allowed
  - Rate limiting to prevent brute force
- **Session Security**
  - 24-hour automatic expiration
  - User-only token access
  - Invalid sessions trigger re-auth
  - No credential storage in browser

### User Experience
- **Workflow Support**
  - First-time setup with environment variables
  - Manual connection for testing
  - Auto-connection for daily use
  - Session status monitoring
  - Quick disconnect for security
- **Status Indicators**
  - 💾 Cached session found
  - ⚠️ No cached session - MFA may be needed
  - ✅ Connected and active
  - 🔄 Refresh available
  - 🚪 Disconnect option
- **Error Messages**
  - "Login error: Challenge Required" → Check MFA
  - "Invalid credentials" → Verify login details
  - "Rate limit exceeded" → Wait 5 minutes
  - "Session expired" → Re-authenticate
  - "Network error" → Check internet

### Best Practices Documentation
1. Always use environment variables
2. Enable 2FA on Robinhood account
3. Disconnect when not actively trading
4. Monitor session status indicators
5. Update credentials after security incidents
6. Review connected sessions regularly
7. Clear cache when switching accounts

### FAQ Coverage
- Credential storage safety
- 24-hour session expiration rationale
- Multi-account support (future)
- Credential handling on disconnect
- MFA automation setup
- Shared computer usage warnings
- Data transmission transparency

[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/settings-v1.0.0
