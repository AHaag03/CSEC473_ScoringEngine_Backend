# CCDC Scoring Backend (Port-based)

- Loads configuration from `.env`
- Expands IPs for each team (X → team number)
- Connects to the specified service ports to check if they’re open
- Logs results in SQLite (`scores.db`)
- Serves `/scores` as JSON for the frontend

## Running

1. `pip install -r requirements.txt`
2. Terminal 1: `python main.py` (scoring loop)
3. Terminal 2: `python api.py` (frontend endpoint)
