## 🎯 About

**Nagios Web Manager** is a modern, user-friendly web interface for managing Nagios Core host configurations. Built with Python Flask and Bootstrap 5, it simplifies host management through an intuitive dashboard while maintaining compatibility with existing Nagios installations.

### The Problem

Managing Nagios hosts through manual `.cfg` file editing is:

- ⏰ Time-consuming
- ❌ Error-prone
- 📉 Not scalable
- 🔒 Difficult to manage for non-technical users

### The Solution

A lightweight Flask web application that provides:

- 🌐 Intuitive web-based dashboard
- ✅ Real-time configuration validation
- 🔄 Automatic Nagios config reload
- 🔐 Secure authentication
- 📡 Complete REST API
- 📱 Mobile-responsive design

---

## ✨ Features

### Core Features

- **Modern Dashboard** - Clean, responsive interface built with Bootstrap 5
- **Host Management** - Add, edit, delete hosts with ease
- **Real-time Validation** - Automatic syntax validation before applying changes
- **Configuration Backup** - Automatic backups before modifications
- **Multi-Directory Support** - Organize hosts across multiple directories
- **Search & Filter** - Quickly find hosts in large deployments

### Security

- **Secure Authentication** - Integration with Nagios htpasswd files
- **Session Management** - Secure session-based access control
- **Audit Logging** - Track all configuration changes

### API & Automation

- **REST API** - Complete RESTful API for automation
- **API Documentation** - Built-in API documentation
- **Bulk Operations** - Manage multiple hosts at once

### Integration

- **Nagios Core Compatible** - Works with existing Nagios installations
- **No Core Modifications** - Doesn't modify Nagios Core files
- **Multi-Version Support** - Tested with Nagios 4.x

---

## 📸 Screenshots

### Dashboard
<img width="1913" height="902" alt="apercu" src="https://github.com/user-attachments/assets/d56eb883-5f14-4c96-a0e1-8f390b10ab60" />

### Host Management
<img width="1880" height="862" alt="hotes" src="https://github.com/user-attachments/assets/61166941-4878-485a-a80e-599d3450afac" />

### Add/Edit Host
<img width="1841" height="886" alt="edithost" src="https://github.com/user-attachments/assets/ed5d785e-04ce-4f69-b1b5-88c8191bf3a9" />

---

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Nagios Core 4.x (or compatible version)
- Permissions to read/write Nagios configuration files

### Quick Install

```bash
# Clone the repository
git clone https://github.com/nagios-web-manager/nagios-web-manager.git
cd nagios-web-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate 

# Install dependencies
pip install -r requirements.txt

# Configure (see Configuration section)
cp config.example.py config.py
nano config.py

# Run the application
./run.sh
```

The application will be available at `http://localhost:5000`

---

## ⚙️ Configuration

### Basic Configuration

Edit `config.py`:

```python
# Nagios paths
NAGIOS_BASE_PATH = '/usr/local/nagios/etc'
NAGIOS_BIN = '/usr/local/nagios/bin/nagios'

# Authentication
HTPASSWD_FILE = '/usr/local/nagios/etc/htpasswd.users'
REQUIRE_AUTH = True

# Flask settings
SECRET_KEY = 'your-secret-key-here'
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False
```

### Authentication Setup

The application uses Nagios htpasswd files for authentication:

```bash
# Create a user
sudo htpasswd /usr/local/nagios/etc/htpasswd.users admin

# Or use existing Nagios users
```

### Permissions

Ensure the application user has proper permissions:

```bash
# Add user to nagios group
sudo usermod -aG nagios your-username

# Set permissions
sudo chown -R nagios:nagios /usr/local/nagios/etc/
sudo chmod -R 775 /usr/local/nagios/etc/
```

---

## 🎬 Quick Start

### 1. Start the Application

```bash
./run.sh
```

### 2. Access the Web Interface

Open your browser and navigate to:

```
http://localhost:5000
```

### 3. Login

Use your Nagios htpasswd credentials:

- Username: `admin` (or your Nagios user)
- Password: (your Nagios password)

### 4. Add Your First Host

1. Click "Add Host" button
2. Fill in the host details:
  - Host name
  - Alias
  - IP address
  - Directory (e.g., `linux`, `windows`)
  - Template (e.g., `linux-server`)
3. Click "Save"
4. Configuration is automatically validated and applied!

---

## 📚 API Documentation

### Authentication

All API endpoints require authentication. Use session-based authentication by logging in first.

### Endpoints

#### Get All Hosts

```bash
GET /api/hosts

Response:
{
  "success": true,
  "hosts": [
    {
      "host_name": "server01",
      "alias": "Production Server 1",
      "address": "192.168.1.10",
      "directory": "/usr/local/nagios/etc/linux",
      ...
    }
  ]
}
```

#### Get Single Host

```bash
GET /api/hosts/<host_name>

Response:
{
  "success": true,
  "host": {
    "host_name": "server01",
    "alias": "Production Server 1",
    ...
  }
}
```

#### Create Host

```bash
POST /api/hosts
Content-Type: application/json

{
  "host": {
    "host_name": "server01",
    "alias": "Production Server 1",
    "address": "192.168.1.10",
    "use": "linux-server"
  },
  "directory": "linux"
}

Response:
{
  "success": true,
  "message": "Host created successfully"
}
```

#### Update Host

```bash
PUT /api/hosts/<host_name>
Content-Type: application/json

{
  "host": {
    "alias": "Updated Alias",
    "address": "192.168.1.20"
  }
}

Response:
{
  "success": true,
  "message": "Host updated successfully"
}
```

#### Delete Host

```bash
DELETE /api/hosts/<host_name>

Response:
{
  "success": true,
  "message": "Host deleted successfully"
}
```

For complete API documentation, visit `/api/docs` when running the application.

---

## 📖 Usage

### Managing Hosts

#### Adding a Host

1. Navigate to "Hosts" page
2. Click "Add Host" button
3. Fill in the form:
  - **Host Name**: Unique identifier (e.g., `web-server-01`)
  - **Alias**: Friendly name (e.g., `Web Server 1`)
  - **Address**: IP address or hostname
  - **Directory**: Where to store the config file
  - **Template**: Nagios template to use (e.g., `linux-server`)
  - **Additional Settings**: Check intervals, contacts, etc.
4. Click "Save"

#### Editing a Host

1. Navigate to "Hosts" page
2. Find the host you want to edit
3. Click "Edit" button
4. Modify the fields
5. Click "Save"

#### Deleting a Host

1. Navigate to "Hosts" page
2. Find the host you want to delete
3. Click "Delete" button
4. Confirm the action

### Using the API

#### Example: Automate Host Creation

```python
import requests

# Login
session = requests.Session()
login_data = {"username": "admin", "password": "your_password"}
session.post("http://localhost:5000/api/login", json=login_data)

# Create host
host_data = {
    "host": {
        "host_name": "auto-server-01",
        "alias": "Automated Server",
        "address": "192.168.1.100",
        "use": "linux-server"
    },
    "directory": "linux"
}

response = session.post("http://localhost:5000/api/hosts", json=host_data)
print(response.json())
```

---

## 🗺️ Roadmap

### v1.1.0 (Coming Soon)

- [ ] Service configuration management
- [ ] Advanced search and filtering
- [ ] English UI 

### v1.2.0

- [ ] Audit logging dashboard
- [ ] Custom alerting rules
- [ ] Email notifications

### v2.0.0

- [ ] Multi-language support (i18n)
- [ ] Advanced analytics dashboard

---

## 🤝 Contributing

Contributions are welcome and greatly appreciated! Here's how you can help:

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the repository
- 📢 Share with others

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 💖 Support the Project

If you find this project useful, please consider supporting its development:

- ⭐ **Star the repository** on GitHub
- ☕ **KO-FI** on [KO-FI](https://ko-fi.com/messefreeze)

Your support helps maintain and improve this project. Thank you! 🙏
