from app import app  
# Expose the underlying Flask server to Gunicorn
server = app.server
