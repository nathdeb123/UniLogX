# UniLogX - Log Management Platform

A modern log collection and analysis platform for Windows and Linux systems with real-time log aggregation and a beautiful analytics dashboard.

## Features

✅ Real-time log collection from Windows Event Viewer and Linux system logs  
✅ Streamlit-based web dashboard with analytics and visualizations  
✅ Advanced filtering and search capabilities  
✅ Log indexing and fast search  
✅ Export functionality (CSV, JSON)  
✅ Multi-OS support (Windows/Linux)  

## Quick Start

```bash
# Install dependencies
pip install -r data/requirements.txt

# Run the application
python data/unilogx_main.py
```

Dashboard available at `http://localhost:8501`

## Installation

### Prerequisites
- Python 3.8+
- Windows 10+ or Linux (Ubuntu 18.04+)
- 500MB disk space, 1GB RAM minimum
- Administrator/sudo privileges recommended

### Windows
```bash
cd path\to\UniLogX
pip install -r data/requirements.txt
python data/unilogx_main.py
```

### Linux
```bash
cd /path/to/UniLogX
pip3 install -r data/requirements.txt
sudo python3 data/unilogx_main.py
```

## Architecture

```
UniLogX/
├── agent/                      # Log collection backend
│   ├── main_agent.py
│   ├── config.py              # Configuration settings
│   ├── windows_logs.py        # Windows log collection
│   ├── linux_logs.py          # Linux log collection
│   └── log_indexer.py
├── dashboard/                  # Web dashboard
│   └── dashboard_app.py       # Streamlit dashboard
├── data/
│   ├── unilogx_main.py        # Main entry point
│   └── requirements.txt
└── Log/                        # Log storage (created at runtime)
```

## Configuration

Edit `agent/config.py` to customize:

```python
COLLECTION_INTERVAL = 10        # Seconds between collections
LOG_INDEX_FILE = "Log/log_index.json"
DEBUG = False

WINDOWS_CATEGORIES = ['System', 'Security', 'Application', 'Network']
LINUX_CATEGORIES = ['syslog', 'auth', 'kernel']
```

## Usage

### Dashboard Navigation

**Filters** (Left Sidebar): Date range, OS type, log category, severity level, keyword search  
**Metrics** (Top): Total logs, critical errors, warnings, info messages  
**Visualizations** (Middle): Logs by category, level, time, OS, and host  
**Log Table** (Bottom): Sortable entries with detailed view, export to CSV/JSON  

### Search Examples
```
"special privileges"    # Exact phrase
error AND authentication # Boolean AND
critical OR error       # Boolean OR
NOT unauthorized        # Negation
securi*                 # Wildcards
```

## Log Format

Logs stored in JSONL format:
```json
{
  "timestamp": "2026-01-30T14:23:45.123456",
  "level": "ERROR",
  "category": "security",
  "os_type": "windows",
  "host": "DESKTOP-ABC",
  "message": "Special privileges assigned."
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No logs showing | Wait 10-15s, verify permissions, check `Log/` directory exists |
| Dashboard won't load | Run as Administrator (Windows) or sudo (Linux), verify port 8501 is free |
| Permission errors | Windows: Run CMD as admin, Linux: Use sudo or `sudo usermod -a -G systemd-journal $USER` |
| Memory issues | Reduce `COLLECTION_INTERVAL`, lower `LOG_RETENTION_DAYS` in config |
| Dependencies missing | Run `pip install -r data/requirements.txt --force-reinstall` |
| Debug mode | Set `DEBUG = True` in `agent/config.py` |

## Log Management

**Clear Old Logs**
```bash
# Windows
powershell -Command "Get-ChildItem Log -Recurse -File | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item"

# Linux
find Log -type f -mtime +30 -delete
```

**Backup Logs**
```bash
# Windows: robocopy Log backup_logs /MIR
# Linux: cp -r Log backup_logs/
```

**Archive Logs**
```bash
# Windows: Compress-Archive -Path Log -DestinationPath Log_backup.zip
# Linux: tar -czf Log_backup.tar.gz Log/
```

## System Requirements

- **Python**: 3.8+  
- **RAM**: 1GB minimum (4GB recommended)  
- **Disk**: 500MB minimum (10GB+ for 30-day retention)  
- **OS**: Windows 10+ or Linux 18.04+  
- **Privileges**: Administrator/sudo required for full access  
- **Network**: Not required (fully local operation)  

## Performance Metrics

- **Log Ingestion**: 1,000-10,000 logs per minute
- **Search Speed**: <500ms for index queries
- **Dashboard Refresh**: 5-10 seconds (configurable)
- **Memory Footprint**: 100-500MB (depending on log volume)

## Security

- All logs stored locally in the `Log/` directory
- No data sent to external services
- Store `Log/` on encrypted filesystem for sensitive environments
- Restrict permissions: `chmod 700 Log/` (Linux)
- Review logs for sensitive data (passwords, tokens, PII)
- Keep Python and dependencies updated

## Comparison with Other Solutions

| Feature | UniLogX | ELK Stack | Splunk |
|---------|---------|-----------|--------|
| Setup Time | 5 min | 30+ min | 1+ hour |
| Cost | Free | Free | $$$$ |
| Local Operation | ✅ | ✅ | ❌ |
| Built-in Collection | ✅ | ❌ | ❌ |
| Resource Usage | Low | High | High |
| Windows/Linux | ✅ Both | Limited/✅ | ✅ Both |

## Contributing

```bash
# Setup development environment
python -m venv dev_venv
source dev_venv/bin/activate      # Linux/Mac
dev_venv\Scripts\activate         # Windows

# Install dev dependencies
pip install -r data/requirements.txt pytest black pylint
```

To contribute:
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/new-feature`
5. Create Pull Request

## License

MIT License - Free for commercial and private use

## Changelog

### v2.0.1 (January 30, 2026)
- Enhanced dashboard with advanced search
- Linux journalctl integration
- CSV/JSON export, real-time streaming

### v2.0 (December 15, 2025)
- Streamlit redesign
- JSON-based log format
- Cross-platform support

### v1.0 (October 1, 2025)
- Initial release
- Basic log collection and dashboard

---

**Version**: 2.0.1 | **Status**: Production Ready ✅  
**Repository**: [GitHub](https://github.com/yourusername/unilogx)  
**Last Updated**: January 30, 2026
