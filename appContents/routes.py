"""
This module defines routes for the web application, including sign-in, main page, server settings,
video management (uploading, removing), and call-forwarding functionality.
"""

from appContents import app
from flask import render_template, request, flash, redirect, url_for
from appContents.models import Settings
from flask import redirect, url_for, request
from appContents.websocket import called_position
from werkzeug.utils import secure_filename
from appContents.forms import SignInForm
from appContents import db;
from appContents.models import Settings
from appContents.models import ButtonRange
from flask import session
from datetime import timedelta
import os;
import re;
import subprocess
from appContents.config import Config 
from datetime import datetime
from flask import jsonify

            

# Set the session permanent and specify session timeout for 60 minutes
app.permanent_session_lifetime = timedelta(minutes=30)




@app.errorhandler(404)
def page_not_found(error):
    """
    Handles 404 errors by rendering a custom 404 page.
    """
    return render_template('404.html'), 404



@app.route('/last_update_time')
def last_update_time():
    """Returns the timestamp of the last video upload."""
    return jsonify({'last_update': Config.LAST_UPLOAD_TIME})



@app.route("/")
@app.route("/signin",  methods=['GET', 'POST'])
def signin():
    """
    Route for sign-in page.

    Renders the sign-in form. If the form is submitted with valid credentials, the user is
    redirected to the main page; otherwise, an error message is displayed.
    """
    form = SignInForm()
    if form.validate_on_submit():
        if form.username.data == Config.SIGNIN_USERNAME and form.password.data == Config.SIGNIN_PASSWORD:
          session['authenticated'] = True
          return redirect(url_for('main'))
        else :
          flash("Invalid username or password", "error")
    return render_template("signin.html" , form=form)




@app.route("/main")
def main():
    """
    Route for the main page.

    Renders the main page if the user is authenticated; otherwise, redirects to the sign-in page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    return render_template("main.html")




@app.route("/settings", methods=["POST", "GET"])
def edgelit_save():
    """
    Route for managing server settings (Edgeled's settings).

    GET method:
        Renders the server settings page, displaying existing settings.

    POST method:
        Processes form submission for updating server settings and redirects to the main page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    
    button_range_start = 1  # Default value
    button_range_end = 100  # Default value
    
    
    def show_edglit_settings(button_range_start, button_range_end):
        """ Get edgelit properties from db to show on setting page """
        edgeled_settings = {
            'flashspeededgelit': [],
            'numofflashes': [],
            'on_color': [],
            'off_color': [],
            'free_color': [],
            'busy_color': []
        }
        for i in range(button_range_start, button_range_end + 1):
            data_in_db = Settings.query.filter_by(id=i).first()
            if data_in_db:
                edgeled_settings['flashspeededgelit'].append(data_in_db.flashspeededgelit)
                edgeled_settings['numofflashes'].append(data_in_db.numofflashes)
                edgeled_settings['on_color'].append(data_in_db.on_color)
                edgeled_settings['off_color'].append(data_in_db.off_color)
                edgeled_settings['free_color'].append(data_in_db.free_color)
                edgeled_settings['busy_color'].append(data_in_db.busy_color)
        return edgeled_settings
    
    
    
    if request.method == "GET":
       # Query button range settings from the database
        button_range = ButtonRange.query.first()
        if button_range:
            button_range_start = button_range.start
            button_range_end = button_range.end

        edgeled_settings = show_edglit_settings(button_range_start, button_range_end)
        return render_template("serverSetting.html", edgeled_settings=edgeled_settings, button_range_start=button_range_start, button_range_end=button_range_end, flask_ip_address= Config.FLASK_IP_ADDRESS,  websocket_port= Config.WEBSOCKET_PORT)
    
    elif request.method == "POST":
        form_data = request.form
        button_range_start = request.form.get('button_range_start')
        button_range_end = request.form.get('button_range_end')
        position_range_min = request.form.get('position_range_min')
        position_range_max = request.form.get('position_range_max')
        
        # Check if all four range fields are provided
        if all((button_range_start, button_range_end, position_range_min, position_range_max)):
            # If all four range fields are provided, proceed with processing
            button_range_start = int(button_range_start)
            button_range_end = int(button_range_end)
            position_range_min = int(position_range_min)
            position_range_max = int(position_range_max)
            # Check if the provided range values are valid
            if button_range_start > button_range_end:
                button_range = ButtonRange.query.first()
                if button_range:
                    button_range_start = button_range.start
                    button_range_end = button_range.end
                edgeled_settings = show_edglit_settings(button_range_start, button_range_end)
                error_message = "Invalid range values. Please make sure the start value is less than or equal to the end value."
                return render_template("serverSetting.html", edgeled_settings=edgeled_settings, error_message=error_message, button_range_start=button_range_start, button_range_end=button_range_end, flask_ip_address= Config.FLASK_IP_ADDRESS, websocket_port= Config.WEBSOCKET_PORT)
        
            if button_range_start != position_range_min or button_range_end != position_range_max:
                button_range = ButtonRange.query.first()
                if button_range:
                    button_range_start = button_range.start
                    button_range_end = button_range.end
                edgeled_settings = show_edglit_settings(button_range_start, button_range_end)
                error_message = "Button Range Start must be equal to Position Range Min, and Button Range End must be equal to Position Range Max."
                return render_template("serverSetting.html", edgeled_settings=edgeled_settings, error_message=error_message, button_range_start=button_range_start, button_range_end=button_range_end, flask_ip_address= Config.FLASK_IP_ADDRESS,  websocket_port= Config.WEBSOCKET_PORT)
            
            # Process other form fields and update existing settings as needed
            button_range = ButtonRange.query.get(1)
            if button_range:
                # Update the existing record
                button_range.start = button_range_start
                button_range.end = button_range_end
            else:
                # Create a new ButtonRange object and add it to the session
                button_range = ButtonRange(start=button_range_start, end=button_range_end)
                db.session.add(button_range)
            
            # Process other form fields and update existing settings as needed
            for i in range(button_range_start, button_range_end + 1):
                existing_setting = Settings.query.filter_by(id=i).first()
                if existing_setting:
                    existing_setting.flashspeededgelit = form_data[f'flashspeededgelit{i}']
                    existing_setting.numofflashes = form_data[f'numofflashes{i}']
                    existing_setting.on_color = form_data[f'on_color{i}']
                    existing_setting.off_color = form_data[f'off_color{i}']
                    existing_setting.free_color = form_data[f'free_color{i}']
                    existing_setting.busy_color = form_data[f'busy_color{i}']
            db.session.commit()
            edgeled_settings = show_edglit_settings(button_range_start, button_range_end)
            success_message = "Update has done properly."
            return render_template("serverSetting.html", success_message=success_message, edgeled_settings=edgeled_settings, button_range_start=button_range_start, button_range_end=button_range_end, flask_ip_address= Config.FLASK_IP_ADDRESS,  websocket_port= Config.WEBSOCKET_PORT)
        
        # Check if all four range fields are empty
        elif not any((button_range_start, button_range_end, position_range_min, position_range_max)):
            # If all four range fields are empty, update existing settings from the form
            button_range = ButtonRange.query.first() 
            if button_range:
                button_range_start = button_range.start
                button_range_end = button_range.end
            else:
                button_range_start = 1
                button_range_end = 100
                
            for i in range(button_range_start, button_range_end + 1):
                existing_setting = Settings.query.filter_by(id=i).first()
                if existing_setting:
                    existing_setting.flashspeededgelit = form_data[f'flashspeededgelit{i}']
                    existing_setting.numofflashes = form_data[f'numofflashes{i}']
                    existing_setting.on_color = form_data[f'on_color{i}']
                    existing_setting.off_color = form_data[f'off_color{i}']
                    existing_setting.free_color = form_data[f'free_color{i}']
                    existing_setting.busy_color = form_data[f'busy_color{i}']
            db.session.commit()
            edgeled_settings = show_edglit_settings(button_range_start, button_range_end)
            success_message = "Update has done properly."    
            return render_template("serverSetting.html", edgeled_settings=edgeled_settings, success_message=success_message, button_range_start=button_range_start, button_range_end=button_range_end, flask_ip_address= Config.FLASK_IP_ADDRESS,  websocket_port= Config.WEBSOCKET_PORT)
        
        # If any of the range fields is empty, show an error message
        else:
            error_message = "Please fill all four input fields."
            button_range = ButtonRange.query.first()
            if button_range:
                button_range_start = button_range.start
                button_range_end = button_range.end
            edgeled_settings = show_edglit_settings(button_range_start, button_range_end)
            return render_template("serverSetting.html", edgeled_settings=edgeled_settings, error_message=error_message, button_range_start=button_range_start, button_range_end=button_range_end, flask_ip_address= Config.FLASK_IP_ADDRESS,  websocket_port= Config.WEBSOCKET_PORT)




@app.route('/callforward')
def call_forward():
    """
    Route for callforward page to display desired videos.

    Renders the callforward page, passing the dictionary of video filenames.
    """
    videos_folder = Config.VIDEOS_FOLDER
    # List all files in the videos folder
    video_files = os.listdir(videos_folder)
    # Create a dictionary to store video files
    video_files_dict = {}
    # Iterate through the list of filenames
    for filename in video_files:
        # Check if the filename is for the background video
        if filename.lower() == "background.mp4":
            background_filename = filename
            # Add the background filename to the dictionary
            video_files_dict["background"] = background_filename
        else:
            # Extract the numeric part of the filename using regular expression
            match = re.match(r'(\d+)\.mp4', filename)
            if match:
                key = match.group(1)
                video_files_dict[key] = filename
    # Get the FLASK_IP_ADDRESS from the environment
    FLASK_IP_ADDRESS = Config.FLASK_IP_ADDRESS
    # Whitelisted IP addresses that are allowed to access the callforward route
    ALLOWED_IP_ADDRESSES = [FLASK_IP_ADDRESS]
    # Get the remote IP address from the request
    remote_ip = request.remote_addr

    # Check if the remote IP address is in the whitelist
    if remote_ip not in ALLOWED_IP_ADDRESSES:
        # If the request is not from the local IP, return a 403 Forbidden response
        return render_template('404.html'), 404

    # Proceed with rendering the callforward page
    return render_template('callforward.html', video_files=video_files_dict, position=called_position, flask_ip_address=Config.FLASK_IP_ADDRESS, websocket_port=Config.WEBSOCKET_PORT)




# Validation for accepting only .mp4 file for uploading videos
ALLOWED_EXTENSIONS = ['mp4']

def allowed_file(filename):
    """Check if the filename has a valid .mp4 extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_filename(filename):
    """Normalize the filename by converting it to lowercase and removing spaces."""
    parts = filename.strip().split(".")
    return parts[0].lower().replace(' ', '').replace('_', '') + "." + parts[1]

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Route for uploading videos.

    GET method:
        Renders the upload videos page.

    POST method:
        Processes video upload, saves the files, and redirects back to the upload page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    
    if request.method == 'GET':
        return render_template("uploadVideos.html") 
    
    elif request.method == 'POST':
        uploaded_files = request.files.getlist('video')
        upload_folder = Config.VIDEOS_FOLDER
        
        # Check if no files were selected
        if not uploaded_files or all(video.filename == '' for video in uploaded_files):
            flash('No files selected for upload.', 'error')
            return redirect(url_for('upload'))
        
         # Process uploaded files
        for video in uploaded_files:
            if video.filename != '':
                if allowed_file(video.filename):
                    # Normalize the filename
                    filename = normalize_filename(secure_filename(video.filename))
                    # Condition for accepting video file names:
                    # The filename must be 'background.mp4' or a numeric value between 1.mp4 and 100.mp4    
                    if filename == 'background.mp4' or (filename.endswith('.mp4') and filename[:-4].isdigit() and 1 <= int(filename[:-4]) <= 100):
                        video.save(os.path.join(upload_folder, filename))
                        # Update the last upload time
                        Config.LAST_UPLOAD_TIME = datetime.utcnow().isoformat()
                    else:
                        flash('Invalid filename. Video names must be between 1.mp4 and 100.mp4, including background.mp4.', 'error')
                        return redirect(url_for('upload'))
                else:
                    flash('Invalid file format. Only .mp4 files are allowed.', 'error')
                    return redirect(url_for('upload'))
        
        # Check if all files were successfully uploaded
        if len(uploaded_files) == 1:
            flash('Video uploaded successfully', 'success')
        else:
            flash(f'All {len(uploaded_files)} videos uploaded successfully.', 'success')
        # Render the upload page and trigger the refresh of the callforward page
        return render_template('uploadVideos.html')
    
    return redirect(url_for('upload'))





def get_video_files():
    """
    Retrieve a list of video files from the static/videos directory.

    Returns:
        list: List of video file names.
    """
    upload_folder = Config.VIDEOS_FOLDER
    video_files = os.listdir(upload_folder)
    sorted_video_files = sorted(video_files, key=custom_sort_key)
    return sorted_video_files

def custom_sort_key(filename):
    """
    Custom sorting key function for sorting filenames based on numeric and textual content.

    This function separates filenames into numeric and non-numeric parts,
    converting the numeric part into an integer and keeping the non-numeric
    part as a string. The resulting tuple is used as the ing key.
    """
    parts = [], []
    for c in filename:
        parts[0 if c.isdigit() else 1].append(c)
    return (int(''.join(parts[0])), ''.join(parts[1]))

@app.route('/remove')
def show_remove_page():
    """
    Route for displaying videos on the remove page.

    Renders the removeVideos page, passing the list of current video files.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    
    current_video_files = get_video_files()
    return render_template('removeVideos.html', video_files=current_video_files)

@app.route('/remove_video/<filename>')
def remove_video(filename):
    """
    Route for removing a video file.

    Removes the specified video file and redirects to the remove page.
    """
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    upload_folder = Config.VIDEOS_FOLDER
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"The video '{filename}' has been successfully removed.", "success")
    else:
        flash(f"The video '{filename}' does not exist.", "error")
    return redirect(url_for('show_remove_page'))





@app.route("/logout")
def logout():
    """
    Route for logging out the user.

    Clears the session and redirects to the sign-in page.
    """
    session.clear()
    return redirect(url_for('signin'))





@app.route("/gate")
def handle_gate():
    """
    Route for adjusting  motorized turnstile gate
    
    Renders the gate page, adjusting gate directions

    """  
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('signin'))
    
    return render_template('motorized_turnstile_gate.html' , flask_ip_address= Config.FLASK_IP_ADDRESS,  websocket_port= Config.WEBSOCKET_PORT)