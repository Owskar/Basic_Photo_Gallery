# Image Sharing Web Application

A simple Flask-based web application that allows users to register, log in, upload images, create posts, and manage their accounts.

## Features

- **User Authentication**

  - Registration system
  - Login/logout functionality
  - Session management

- **User Profile Management**

  - View profile information (username, email)
  - Change password functionality

- **File Upload Feature**

  - Upload images to a dedicated directory
  - Personal gallery to view uploaded images

- **Post Creation**
  - Create text posts
  - View posts on dashboard

## Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/image-sharing-app.git
cd image-sharing-app
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the virtual environment

   - Windows:

   ```bash
   venv\Scripts\activate
   ```

   - macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

4. Install the required packages

```bash
pip install -r requirements.txt
```

5. Create required directories

```bash
mkdir -p static/uploads
```

## Running the Application

1. Run the Flask application

```bash
python app.py
```

2. Access the application at: http://127.0.0.1:5000/

## Usage Flow

1. Register a new account
2. Log in with your credentials
3. Upload images to your gallery
4. Create posts that appear on your dashboard
5. View and manage your profile information
6. Change your password if needed

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS

## Project Structure

```
image-sharing-app/
├── app.py                # Main application file
├── database.db           # SQLite database (generated on first run)
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── static/               # Static files
│   └── uploads/          # Uploaded images directory
└── templates/            # HTML templates
    ├── layout.html       # Base template
    ├── home.html         # Home page
    ├── register.html     # Registration page
    ├── login.html        # Login page
    ├── dashboard.html    # User dashboard
    ├── profile.html      # User profile
    ├── change_password.html  # Change password page
    ├── upload.html       # File upload page
    ├── gallery.html      # Image gallery page
    └── create_post.html  # Post creation page
```

## Note

This application is intentionally vulnerable to common security flaws for educational purposes. Do not use in a production environment.
