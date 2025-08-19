# SecurityAwarenessApp

SecurityAwarenessApp is a Kotlin-based Android application that supports the Iron Dillo mission of providing veteran-owned cybersecurity for East Texas small businesses, individuals, and rural operations. The app promotes security awareness through mobile-friendly guidance.

## Build Steps
1. Install Android Studio or the Android command line tools.
2. Open the project in `mobile-app/`.
3. Use the Gradle wrapper to build:
   ```bash
   ./gradlew build
   ```
4. Run on an emulator or connected device running Android 8.0 (API 26) or newer.

## OWASP Mobile Top 10 Mapping

| Module | Vulnerability | OWASP Category |
| --- | --- | --- |
| `vulns.storage.InsecurePrefsActivity` | Plain-text SharedPreferences | M2: Insecure Data Storage |
| `vulns.storage.SecurePrefsActivity` | Hashed preference storage | M2: Insecure Data Storage |
| `vulns.auth.WeakPasswordActivity` | Weak password validation | M4: Insecure Authentication |
| `vulns.auth.SecurePasswordActivity` | Strong password requirements | M4: Insecure Authentication |
| `vulns.network.InsecureHttpActivity` | Clear-text HTTP communication | M3: Insecure Communication |
| `vulns.network.SecureHttpActivity` | HTTPS with certificate validation | M3: Insecure Communication |

## Legal Notice
This software is provided "as is" without warranty of any kind. Use at your own risk and ensure compliance with local laws and regulations.
