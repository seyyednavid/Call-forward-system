# Call Forward System (CFS)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [HTML Pages](#html-pages)
  - [Main Page](#main-page)
  - [Settings Page](#settings-page)
  - [Upload Page](#upload-page)
  - [Remove Page](#remove-page)
  - [Gate Control Page](#gate-control-page)
- [Project Structure](#project-structure)
- [Access the Application](#Access-the-Application)
- [Navigate to Different Pages](#Navigate-to-Different-Pages)
- [WebSocket Communication](#websocket-communication)
- [License](#license)



## Introduction
This project handles requests from edgelit buttons via WebSocket, retrieves the relevant edgelit button specifications from the database, and responds with the appropriate features. Additionally, it displays desired videos based on edgelit button requests to navigate customers or passengers to the correct destination.



## Features
- **User Authentication:** Secure access control.
- **Real-Time WebSocket Communication:** Instant data exchange.
- **Database Management with SQLAlchemy:** Robust data handling.
- **Flask-Based Routing:** Efficient request handling.
- **Configurable Settings:** Easily adjustable parameters.
- **Responsive UI:** Mobile-friendly design.



## Getting Started

  ### Prerequisites
  Before you begin, ensure you have the following installed:
  - Python 3.12.1
  - Virtualenv (recommended)

  ### Installation
  for installing all packages
  - pip install -r requirements.txt  



## Configuration
Make sure the configuration settings are correctly set in `config.py`.



## Running the Application
Execute the following command in your terminal to start the application:

    ```bash on windows
    python run.py
    ```
    
    ```bash on mac
    python3 run.py
    ```



## HTML Pages

  ### Sign-In Page
  - **Purpose:**  Authenticates users to access the application.
  - **Features:**
    - Sign-in form for entering username and password.
    - Validation to ensure credentials are correct before granting access.

  ### Main Page
  - **Purpose:** Serves as the navigation hub to access other pages of the application.
  - **Features:** Provides links or buttons to navigate to the settings, upload, remove, and gate control pages.

  ### Settings Page
  - **Purpose:** Allows users to adjust the settings of the edgelit buttons.
  - **Features:** 
    - Form inputs to configure button range start and end.
    - Fields to set Wi-Fi name and password.
    - Options to modify button flash speed, number of flashes, and color settings.

  ### Upload Page
  - **Purpose:** Enables users to upload video files to the project.
  - **Features:** 
    - File upload functionality to add new videos.
    - Display of uploaded videos.

  ### Remove Page
  - **Purpose:** Allows users to remove existing video files from the project.
  - **Features:** 
    - List of videos with options to remove them.
    - Confirmation prompts to prevent accidental deletions.

  ### Gate Control Page
  - **Purpose:** Manages the direction of the motorized gate.
  - **Features:** 
    - Controls to set the direction of the gate.



## Project Structure
  ## Project Structure
- `run.py`: This script starts the Flask application, initializing the application context, setting up the database, starting the Flask server, and opening the default web browser to the application's home page.

- `requirements.txt`: Contains all the necessary package dependencies for the application. Install them using the command `pip install -r requirements.txt`.

- `instance/`: Directory for instance-specific files like the SQLite database file (`site.db`). This directory is not under version control, making it suitable for data that should not be shared across different deployments.

- `appContents/`: Main package containing all core components of the application.
  - `__init__.py`: Initializes the Flask application, configures settings, and sets up the database and routes.
  - `config.py`: Holds configuration settings such as database URIs and secret keys.
  - `models.py`: Defines the database models using SQLAlchemy.
  - `routes.py`: Defines the application's routes.
  - `websocket.py`: Manages WebSocket connections for real-time communication.
  - `forms.py`: A form used for user authentication
  - `setup_default_edgelit_settings.py`: Default configurations if no settings exist
  - `templates/`: Contains HTML templates for the application.
    - `base.html`: Base template with common HTML structure.
    - `signin.html`: Template for the sign-in page.
    - `serverSetting.html`: Template for adjusting edgelit button settings.
    - `upload.html`: Template for uploading videos.
    - `remove.html`: Template for removing videos.
    - `gate.html`: Template for gate control operations.
  - `static/`: Contains static files like CSS, JavaScript, and media.
    - `css/`: CSS files for styling.
    - `js/`: JavaScript files for functionality.
    - `videos/`: Storage for video files.



## Access the Application
 Open your web browser and go to `http://127.0.0.1:8888` to access the application.



## Navigate to Different Pages
- **Sign in:** `127.0.0.1:8888//signin` or `127.0.0.1:8888`
- **Main Page:** `127.0.0.1:8888/main` 
- **Settings Page:** `127.0.0.1:8888/settings` 
- **Upload Page:** `127.0.0.1:8888/upload`
- **Remove Page:** `127.0.0.1:8888/remove` 
- **Gate Control Page:** `127.0.0.1:8888/gate` 




## WebSocket Communication
The Call Forward System utilizes WebSocket technology to enable real-time, bidirectional communication between the server and client devices. This allows the system to promptly respond to interactions from edgelit buttons and manage the flow of data efficiently.

  ### WebSocket Server Setup
  The WebSocket server is implemented using Python's `websockets` library and is integrated within the Flask application environment. It runs on a separate thread to handle incoming WebSocket connections without blocking the main application thread. The server listens for connections on a designated port as specified in the application's configuration.

  ### Connection Management
  Once a WebSocket connection is established, the server adds it to a set of connected clients, enabling messages to be sent to all or specific clients based on the application logic. The connection remains open to continuously receive and process messages sent by the client.

  ### Message Handling
  The server handles different types of messages identified by a `device_type` field in the JSON message structure. Depending on the `device_type`, the server performs various actions:
  - **Edgelit-button**: Retrieves settings from the database and sends back configuration details such as flash speed, color settings, and other parameters necessary for the button's operation.
  - **MG-button**: Broadcasts motorized gate's message to other clients as needed.
  - **WiFi_CRED**: Handles Wi-Fi credentials updates or requests.

  ### Error Handling and Logging
  The server logs significant events such as new connections, disconnections, and errors in message handling. In case of a JSON parsing error or an unexpected message format, it logs the error details. This assists in monitoring the system's health and troubleshooting issues.

  ### Closing Connections
  Connections can be terminated gracefully by the server in response to specific commands or if the client disconnects. The server ensures that all resources are cleaned up properly, which includes removing the client from the connected set and closing the WebSocket.



  ## License
  This project is licensed under the Tensator Proprietary License - see the [LICENSE](LICENSE) file for details.
