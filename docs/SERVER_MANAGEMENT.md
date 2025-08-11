# Server Management

## Quick Commands

### Start Individually
```bash
# Backend (Terminal 1)
source venv/bin/activate && FLASK_APP=src/api.py python -m flask run --host=0.0.0.0 --port=5001

# Frontend (Terminal 2)
cd frontend && npm start
```

### Stop Servers
```bash
# Kill both
pkill -f "flask run" && pkill -f "react-scripts"

# Kill individually
pkill -f "flask run"      # Backend
pkill -f "react-scripts"  # Frontend
```

### Status Check
```bash
# Port status
lsof -i :5001  # Backend
lsof -i :3000  # Frontend

# Health check
curl http://localhost:5001/api/health  # Backend
curl http://localhost:3000              # Frontend
```

## Troubleshooting

### Port Conflicts
```bash
lsof -ti :5001 | xargs kill -9  # Backend
lsof -ti :3000 | xargs kill -9  # Frontend
```

### Force Kill All
```bash
pkill -9 -f "(flask|react|python.*api|node.*start)"
```