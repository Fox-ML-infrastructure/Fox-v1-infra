# Professional Domain Setup for Enterprise Licensing

## Current Status

The codebase has been updated to use a professional domain email address (`licensing@foxml.io`) instead of a personal Gmail address for enterprise licensing inquiries.

## Why This Matters

For enterprise sales to multi-billion dollar firms (Optiver, Citadel, etc.), using a professional domain:
- **Increases credibility**: Shows you're a vendor, not a hobbyist
- **Passes vendor onboarding**: Many firms auto-reject or flag personal email domains
- **Reduces "Key Person Risk"**: Professional domain suggests institutional support, not single-person dependency
- **Makes contracts look more valuable**: Professional infrastructure suggests higher-value agreements

## Action Required

### Option 1: Set Up Domain (Recommended)

1. **Purchase domain**: Buy `foxml.io` or similar (e.g., `fox-infra.com`, `foxml-infrastructure.com`)
   - Cost: ~$12-15/year
   - Recommended registrars: Namecheap, Google Domains, Cloudflare

2. **Set up email forwarding**: Configure `licensing@foxml.io` to forward to your Gmail
   - Most registrars offer free email forwarding
   - Or use a service like Google Workspace ($6/month) or Zoho Mail (free tier available)

3. **Update environment variable** (optional): If you want to keep the Gmail as fallback during setup:
   ```bash
   export FOXML_CONTACT_EMAIL="licensing@foxml.io"
   ```

### Option 2: Temporary Fallback

If you haven't set up the domain yet, the code will use `licensing@foxml.io` by default. You can temporarily override it:

```bash
export FOXML_CONTACT_EMAIL="jenn.lewis5789@gmail.com"
```

Or update the default in `TRAINING/common/license_banner.py` line 34.

## Files Updated

- `COMMERCIAL_LICENSE.md`: Copyright updated to "Fox ML Infrastructure LLC", email updated to `licensing@foxml.io`
- `TRAINING/common/license_banner.py`: Default email set to `licensing@foxml.io` (configurable via `FOXML_CONTACT_EMAIL` env var)
- All legal documents reference the professional domain

## Next Steps

1. **Immediate**: Set up domain and email forwarding (30 minutes)
2. **Test**: Send test email to `licensing@foxml.io` to verify forwarding works
3. **Update**: If using a different domain, update `TRAINING/common/license_banner.py` default
4. **Document**: Update this file once domain is live

---

**Note**: The 30-day evaluation period clause has already been added to `COMMERCIAL_LICENSE.md` Section 2, addressing the "immediate payment friction" issue.
