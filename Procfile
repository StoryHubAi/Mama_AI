web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
release: python -c "from app import app, db; app.app_context().push(); db.create_all()"
