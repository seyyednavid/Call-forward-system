"""
Configuration settings for the Flask application.
"""


class Config:
    # Credentials for application sign-in
    SIGNIN_USERNAME="10SatorAdmin"
    SIGNIN_PASSWORD="@Ten10Sator!!YSN"
    
    # Network configuration for Flask application
    FLASK_IP_ADDRESS='127.0.0.1'
    FLASK_PORT=8888
    COMBINED_FLASK_IP_PORT=f"{FLASK_IP_ADDRESS}:{FLASK_PORT}"
    
    # Port configuration for WebSocket server
    WEBSOCKET_PORT=8764
    
    # Secret key for session management and security
    SECRET_KEY="382860d6ef9587472b5f3bbe"
    
    # Secret key for session management and security
    VIDEOS_FOLDER="./appContents/static/videos"


