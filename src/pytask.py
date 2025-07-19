#!/usr/bin/env python3

from flask import Flask, render_template, flash, request, jsonify
from wtforms import Form, StringField, validators, SubmitField
import sys
import argparse
import time
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
# Add secret for session management (Required for Debug)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '7d441f27d441f27567d441f2b6176a')

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'user_management')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'user_operations')

# Initialize MongoDB client
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("MongoDB connection established successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    mongo_client = None
    db = None
    collection = None

class ReusableForm(Form):
    name = StringField('Name:', validators=[validators.DataRequired(), validators.Length(min=4, max=12)])
    usershell = StringField('usershell:', validators=[validators.DataRequired(), validators.Length(min=7, max=15)])
    folder = StringField('folder:', validators=[validators.DataRequired(), validators.Length(min=6, max=18)])
    password = StringField('Password:', validators=[validators.DataRequired(), validators.Length(min=3, max=12)])
    sudop = StringField('Sudop:', validators=[validators.DataRequired(), validators.Length(min=2, max=3)])
    action = StringField('action:', validators=[validators.DataRequired(), validators.Length(min=5, max=10)])

def log_to_mongodb(name, folder, usershell, password, sudop, action, status, error_msg=None):
    """Log user operation to MongoDB"""
    if collection is None:
        print("MongoDB not available, skipping log")
        return
    
    try:
        log_entry = {
            'timestamp': datetime.utcnow(),
            'username': name,
            'home_folder': folder,
            'shell': usershell,
            'sudo_privileges': sudop,
            'action': action,
            'status': status,
            'error_message': error_msg,
            'server_info': {
                'hostname': os.uname().nodename,
                'system': os.uname().sysname
            }
        }
        
        # Don't store actual passwords in logs for security
        if password:
            log_entry['password_set'] = True
        
        result = collection.insert_one(log_entry)
        print(f"Operation logged to MongoDB with ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"Failed to log to MongoDB: {e}")

@app.route("/", methods=['GET', 'POST'])
def webapp():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        folder = request.form['folder']
        usershell = request.form['usershell']
        password = request.form['password']
        sudop = request.form['sudop']
        action = request.form['action']
        print(action, " ", name, " ", usershell, " ", folder, " ", password, " ", sudop)
        
        # Exclude delete action from form validation
        if action != "Delete":
            if form.validate():
                success, error_msg = usercreate(name, folder, usershell, password, sudop, action)
                if success:
                    log_to_mongodb(name, folder, usershell, password, sudop, action, "success")
                    flash(f'Action {action} performed successfully on User {name}')
                else:
                    log_to_mongodb(name, folder, usershell, password, sudop, action, "failed", error_msg)
                    flash(f'Error performing {action} on User {name}: {error_msg}')
            else:
                flash(f'Error: All the form fields are required for action {action}')
        else:
            success, error_msg = usercreate(name, folder, usershell, password, sudop, action)
            if success:
                log_to_mongodb(name, folder, usershell, password, sudop, action, "success")
                flash(f'Action {action} performed successfully on User {name}')
            else:
                log_to_mongodb(name, folder, usershell, password, sudop, action, "failed", error_msg)
                flash(f'Error performing {action} on User {name}: {error_msg}')
    
    return render_template('webapp.html', form=form)

@app.route("/logs", methods=['GET'])
def get_logs():
    """API endpoint to retrieve operation logs from MongoDB"""
    if collection is None:
        return jsonify({"error": "MongoDB not available"}), 500
    
    try:
        # Get recent logs (last 100 operations)
        logs = list(collection.find().sort("timestamp", -1).limit(100))
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            log['_id'] = str(log['_id'])
            log['timestamp'] = log['timestamp'].isoformat()
        
        return jsonify({"logs": logs})
    
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve logs: {str(e)}"}), 500

# Def a function for user create
def usercreate(name, folder, usershell, password, sudop, action):
    """
    Create, modify, or delete system users
    Returns: (success: bool, error_message: str)
    """
    try:
        # Command for useradd/mod/del
        if action == "Delete":
            cmd = f"sudo /usr/sbin/userdel -f {name}"
            result = os.system(cmd)
            if result != 0:
                return False, f"Failed to delete user {name}"
            return True, None
        elif action == "Modify":
            cmd = f"sudo /usr/sbin/usermod -m -d {folder} -s {usershell} {name}"
        else:  # Create
            cmd = f"sudo /usr/sbin/useradd -m -d {folder} -s {usershell} {name}"
        
        result = os.system(cmd)
        if result != 0:
            return False, f"Failed to {action.lower()} user {name}"
        
        # Command for password setting (only for create/modify)
        if action != "Delete":
            upass = f"sudo echo {name}:{password} | sudo chpasswd"
            result = os.system(upass)
            if result != 0:
                return False, f"User {action.lower()}d but failed to set password"
            
            # Command for sudo addition
            if sudop == "Yes":
                sudocmd = f"sudo echo '{name} ALL=(ALL:ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo"
                print(f"Sudo Command: {sudocmd}")
                result = os.system(sudocmd)
                if result != 0:
                    return False, f"User {action.lower()}d but failed to grant sudo privileges"
        
        return True, None
        
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User Management Web Application")
    parser.add_argument('-p', '--port', type=int, required=True, help='The port to listen on.')
    args = parser.parse_args()
    
    print(f"Starting application on port {args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=True)