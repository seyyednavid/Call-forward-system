"""
Main entry point for the Flask application. Initializes the app context, sets up the database, and starts the Flask and WebSocket servers.
"""

from appContents import app, db, open_browser
from appContents.setup_default_edgelit_settings import add_settings
from appContents.websocket import WebSocketServerThread

if __name__ == "__main__":
    with app.app_context():
        db.create_all()    # Create all database tables based on SQLAlchemy models
        add_settings()    # Populate the database with default settings if it's empty

    # Start a thread to manage WebSocket connections
    websocket_thread = WebSocketServerThread()
    websocket_thread.start()

    # Open the system default web browser to the Flask application's home page
    open_browser()
    # Run the Flask application
    app.run(host=app.config['FLASK_IP_ADDRESS'], port=app.config['FLASK_PORT'], debug=True, use_reloader=False)

    # Wait for the WebSocket thread to finish before closing
    websocket_thread.join()
