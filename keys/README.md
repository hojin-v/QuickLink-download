# Update verification public key

`updates.pem` is the RSA **public key** used by QuickLink and the release workflow to verify signed update metadata. Publishing it is intentional. It cannot produce a valid release signature.

The matching private key is kept outside this repository in private local signing storage and GitHub Actions Secrets. Never commit a private key, upload keystore, service-account JSON or access token here.

The application pins the same public key; changing this repository's copy does not change the key already embedded in installed apps. Key rotation requires a deliberate application update.
