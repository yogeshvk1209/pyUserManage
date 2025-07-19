// MongoDB initialization script for user management system
db = db.getSiblingDB('user_management');

// Create collection for user operations
db.createCollection('user_operations');

// Create indexes for better performance
db.user_operations.createIndex({ "timestamp": -1 });
db.user_operations.createIndex({ "username": 1 });
db.user_operations.createIndex({ "action": 1 });
db.user_operations.createIndex({ "status": 1 });

// Insert a sample log entry
db.user_operations.insertOne({
    timestamp: new Date(),
    username: "sample_user",
    home_folder: "/home/sample_user",
    shell: "/bin/bash",
    sudo_privileges: "No",
    action: "Create",
    status: "success",
    error_message: null,
    password_set: true,
    server_info: {
        hostname: "docker-container",
        system: "Linux"
    }
});

print("MongoDB initialization completed successfully!");
print("Created user_operations collection with indexes");
print("Database: user_management is ready for use");