# Journald Logging Setup

All ranking scripts now support systemd journal logging, allowing you to monitor progress over SSH using `journalctl`.

## Installation

Install the systemd journal Python module:

```bash
conda activate trader_env
pip install systemd
```

Or if that doesn't work:

```bash
pip install cysystemd
```

## Usage

### View logs in real-time

```bash
# Watch all ranking script logs
journalctl -f -u user-1000.service | grep -E "(rank_target|rank_features|multi_model)"

# Watch specific script
journalctl -f SYSLOG_IDENTIFIER=rank_target_predictability

# Watch with timestamps
journalctl -f --since "10 minutes ago" SYSLOG_IDENTIFIER=rank_target_predictability
```

### View recent logs

```bash
# Last 100 lines
journalctl -n 100 SYSLOG_IDENTIFIER=rank_target_predictability

# Last hour
journalctl --since "1 hour ago" SYSLOG_IDENTIFIER=rank_target_predictability

# Today's logs
journalctl --since today SYSLOG_IDENTIFIER=rank_target_predictable
```

### Filter by log level

```bash
# Only warnings and errors
journalctl -p warning SYSLOG_IDENTIFIER=rank_target_predictability

# Only errors
journalctl -p err SYSLOG_IDENTIFIER=rank_target_predictability
```

### Search logs

```bash
# Search for specific target
journalctl SYSLOG_IDENTIFIER=rank_target_predictability | grep "peak_60m"

# Search for errors
journalctl SYSLOG_IDENTIFIER=rank_target_predictability | grep -i error

# Search for leakage warnings
journalctl SYSLOG_IDENTIFIER=rank_target_predictability | grep -i leakage
```

## Script Identifiers

Each script has its own identifier:

- `rank_target_predictability` - Target ranking script
- `rank_features_by_ic_and_predictive` - Feature ranking by IC and predictive power
- `rank_features_comprehensive` - Comprehensive feature ranking
- `multi_model_feature_selection` - Multi-model feature selection

## Example: Monitor Target Ranking

```bash
# Terminal 1: Start the script
python scripts/rank_target_predictability.py --discover-all --symbols AAPL,MSFT,GOOGL,TSLA,JPM

# Terminal 2 (SSH): Watch progress
journalctl -f SYSLOG_IDENTIFIER=rank_target_predictability
```

## Example: Check for Errors

```bash
# Check for any errors in the last hour
journalctl --since "1 hour ago" -p err SYSLOG_IDENTIFIER=rank_target_predictability

# Check for leakage warnings
journalctl --since "1 hour ago" SYSLOG_IDENTIFIER=rank_target_predictability | grep -i "leakage"
```

## Example: Monitor Multiple Scripts

```bash
# Watch all ranking scripts
journalctl -f | grep -E "SYSLOG_IDENTIFIER=(rank_target|rank_features|multi_model)"
```

## Fallback

If journald is not available, scripts will automatically fall back to console logging only. You'll see a debug message indicating journald is not available, but the script will continue normally.

## Benefits

1. **Remote monitoring**: Watch progress over SSH without needing to tail log files
2. **Persistent logs**: Systemd journal persists logs across reboots (configurable)
3. **Powerful filtering**: Use journalctl's filtering capabilities
4. **Centralized**: All logs in one place, easy to search
5. **Non-intrusive**: Falls back gracefully if journald isn't available

