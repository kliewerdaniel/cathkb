# Code Signing Setup

The release workflow supports optional code signing for all platforms. Without signing, binaries work but show "unidentified developer" warnings (macOS) or SmartScreen prompts (Windows).

## Required GitHub Secrets

### macOS (Apple Developer — $99/year)

| Secret | Description |
|---|---|
| `APPLE_CERTIFICATE` | Base64-encoded `.p12` certificate (Developer ID Application) |
| `APPLE_CERTIFICATE_PASSWORD` | Password for the `.p12` file |
| `APPLE_ID` | Your Apple ID email |
| `APPLE_APP_PASSWORD` | App-specific password (generate at appleid.apple.com) |
| `APPLE_TEAM_ID` | Your 10-character Team ID |

**To export your certificate as base64:**
```bash
# Export .p12 from Keychain Access, then:
base64 -i certificate.p12 | pbcopy
# Paste as APPLE_CERTIFICATE secret
```

### Windows (Azure Trusted Signing or local cert)

**Option A: Azure Trusted Signing (recommended)**
| Secret | Description |
|---|---|
| `AZURE_CLIENT_ID` | Azure AD app client ID |
| `AZURE_CLIENT_SECRET` | Azure AD app client secret |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_CODE_SIGNING_ACCOUNT` | Trusted Signing account name |
| `AZURE_CERT_PROFILE_NAME` | Certificate profile name |

**Option B: Local code signing certificate**
| Secret | Description |
|---|---|
| `WINDOWS_CERTIFICATE` | Base64-encoded `.pfx` certificate |
| `WINDOWS_CERTIFICATE_PASSWORD` | Password for the `.pfx` file |

### Linux (GPG — free)

| Secret | Description |
|---|---|
| `GPG_PRIVATE_KEY` | ASCII-armored GPG private key (`gpg --armor --export-secret-key YOUR_KEY_ID`) |
| `GPG_PASSPHRASE` | Passphrase for the GPG key |

## How It Works

- The workflow checks if secrets are configured
- If secrets are missing, builds proceed **unsigned** (still functional)
- If secrets are present, binaries are signed and (on macOS) notarized
- No code changes needed — just add secrets when ready

## Quick Start (Without Signing)

```bash
# Just push a tag — unsigned builds work fine
git tag v0.1.0
git push origin v0.1.0
```

Users can bypass macOS Gatekeeper with:
```bash
xattr -d com.apple.quarantine ./cathkb
```
