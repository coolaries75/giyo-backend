# 🧪 Dev Notes — Giyo Backend

## [2025-04-29] ⚙️ DB Schema Setup Moved

### ✅ Summary:
- Removed `Base.metadata.create_all(bind=engine)` from `main.py`
- Created a dedicated script `setup_db.py` for manual DB schema initialization
- This improves server restart performance on Railway by preventing cold-start delays

### 📂 File Changes:
- `main.py`: Removed DB auto-creation line
- `setup_db.py`: Added for manual one-time table setup

### ▶️ Usage:
Run the script manually after initial deployment or if the database is reset:
```bash
python setup_db.py
