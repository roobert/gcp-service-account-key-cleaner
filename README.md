# GCP Service Account Key Cleaner

GCP Function that can be used to delete service account keys after a set period of time.

This can be useful when using Vault to issue service account keys since there is a limit to 10 keys per service account.

## Example
```
SERVICE_ACCOUNT_EMAIL="<service account email>" TIME_TO_LIVE_MINUTES="20" ./src/main.py
```
