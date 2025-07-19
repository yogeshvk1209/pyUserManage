# User Management Web Application - CentOS 9

A modernized Flask web application for managing Linux system users with MongoDB logging support.

## Features

- **User Management**: Create, modify, and delete system users
- **MongoDB Integration**: All operations are logged to MongoDB with timestamps
- **Modern UI**: Bootstrap 5 interface with tabbed navigation
- **Operation Logs**: View historical user operations in a searchable table
- **Python 3.9**: Updated to use modern Python syntax and libraries
- **CentOS 9**: Compatible with CentOS Stream 9

## Technology Stack

- **Backend**: Python 3.9, Flask 2.3+, WTForms 3.0+
- **Database**: MongoDB 7.0
- **Frontend**: Bootstrap 5, HTML5, JavaScript ES6+
- **Container**: Docker with CentOS Stream 9

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to the project directory
2. Start the application with MongoDB:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost:8080`

### Manual Setup

1. Install dependencies:
   ```bash
   pip3 install -r src/requirements.txt
   ```

2. Start MongoDB (if not using Docker):
   ```bash
   mongod --dbpath /path/to/your/db
   ```

3. Configure environment variables in `src/.env`:
   ```env
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=user_management
   COLLECTION_NAME=user_operations
   ```

4. Run the application:
   ```bash
   python3 src/pytask.py -p 8080
   ```

## Configuration

### Environment Variables

- `MONGO_URI`: MongoDB connection string (default: `mongodb://localhost:27017/`)
- `DB_NAME`: Database name (default: `user_management`)
- `COLLECTION_NAME`: Collection name for logs (default: `user_operations`)
- `SECRET_KEY`: Flask secret key for sessions

### MongoDB Setup

The application automatically creates the necessary database and collections. The initialization script creates:
- `user_operations` collection with proper indexes
- Sample data for testing

## API Endpoints

- `GET /`: Main user management interface
- `POST /`: Process user management forms
- `GET /logs`: Retrieve operation logs (JSON API)

## User Operations

### Create User
- Username (4-12 characters, letters only)
- Shell (default: `/bin/bash`)
- Home folder (auto-filled based on username)
- Password
- Sudo privileges (Yes/No)

### Modify User
- Same fields as create, modifies existing user

### Delete User
- Only requires username
- Removes user and home directory

## MongoDB Logging

All operations are logged with:
- Timestamp
- User details (username, shell, home folder)
- Action performed
- Success/failure status
- Error messages (if any)
- Server information

## Security Considerations

⚠️ **Important Security Notes:**

1. This application executes system commands with sudo privileges
2. Passwords are not stored in logs but are processed in plaintext
3. Input validation is basic - consider additional sanitization for production
4. The application should run in a controlled environment
5. Consider implementing authentication and authorization

## Development

### File Structure
```
├── src/
│   ├── pytask.py          # Main Flask application
│   ├── templates/
│   │   └── webapp.html    # Web interface
│   ├── static/            # CSS files
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment configuration
├── mongo-init/
│   └── init.js           # MongoDB initialization
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
└── README.md
```

### Adding Features

1. **New User Fields**: Update the form class and HTML template
2. **Additional Logging**: Modify the `log_to_mongodb()` function
3. **New Operations**: Add new actions to the form and `usercreate()` function

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**: Check if MongoDB is running and accessible
2. **Permission Denied**: Ensure the container has sudo privileges
3. **User Creation Failed**: Check system user limits and permissions

### Logs

- Application logs: Check Docker container logs
- MongoDB logs: Check MongoDB container logs
- Operation logs: Available through the web interface `/logs` endpoint

## License

This project is provided as-is for educational and development purposes.