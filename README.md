# 🚀 OpenCodeHub

<div align="center">
  <h3>A modern, collaborative project management and file sharing platform</h3>
  <p>Manage, share, and collaborate on projects with ease</p>
</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Prerequisites](#-prerequisites)
- [Setup & Installation](#️-setup--installation)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Team Members](#-team-members)
- [Deployment](#-deployment)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

**OpenCodeHub** is a web-based platform designed to help users manage, share, and collaborate on projects of any type. It provides an intuitive interface for creating projects, uploading files, tracking changes, and organizing work with a clean, modern dashboard.

### 🎯 Purpose
Whether you're working on documents, designs, research, or any collaborative work, OpenCodeHub makes project management simple and efficient. The platform allows you to:
- **Organize** your work into structured projects
- **Upload** and manage files seamlessly
- **Share** projects with unique, shareable links
- **Collaborate** with team members through comments
- **Track** project activities and updates in real-time

## ✨ Features

### Core Features
- 🔐 **User Authentication**
  - Secure user registration and login
  - Password reset functionality
  - Session management
  - Protected routes and views

- 📁 **Project Management**
  - Create unlimited projects
  - Edit project details
  - Delete projects
  - Organize projects in a centralized dashboard

- 📤 **File Upload & Management**
  - Upload multiple files per project
  - Support for various file types
  - File size tracking
  - File type categorization

- 🌐 **Project Visibility Control**
  - **Public Projects** - Visible to all users
  - **Private Projects** - Visible only to the owner
  - Toggle visibility settings

- 🔗 **Shareable Project Links**
  - Generate unique URLs for project sharing
  - Access projects via secure, shareable links
  - Link management and control
  - Error handling with user notifications

- 💬 **Commenting System**
  - Add comments to projects
  - Real-time comment updates
  - Collaborate with team members
  - Discussion threads

- 📊 **Modern Dashboard**
  - Clean, responsive interface
  - Project overview at a glance
  - Quick action buttons
  - Statistics display (Projects, Files, Comments)

- ⏱️ **Activity Timeline**
  - Track recent project updates
  - View modification history
  - Real-time activity feed
  - Timestamp tracking

- 🔍 **Project Discovery**
  - Browse public projects
  - Search functionality
  - Filter by type (Public/Private)
  - Explore community projects

---

## 🛠️ Tech Stack

### **Backend Framework**
- **Django 5.1.2** - High-level Python web framework
- **Python** - Core programming language

### **Database**
- **Supabae**
  - PostgreSQL database

### **Frontend Technologies**
- **HTML**
- **CSS**
- **JavaScript**

### **Version Control**
- **Git** - Distributed version control system
- **GitHub** - Code hosting and collaboration platform
---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8 or higher**
  - Download from [python.org](https://www.python.org/downloads/)
  - Verify installation: `python --version` or `python3 --version`

- **pip (Python Package Manager)**
  - Usually comes with Python
  - Verify installation: `pip --version`

- **Git**
  - Download from [git-scm.com](https://git-scm.com/downloads)
  - Verify installation: `git --version`

- **IDE**
  - VS Code

---

## ⚙️ Setup & Installation

### 📌 **Option 1: Contributing to the Project (Fork & Clone)**

If you want to contribute to the codebase, follow these steps:

#### **Step 1: Fork the Repository**
1. Go to the [OpenCodeHub repository](https://github.com/yourusername/opencodehub)
2. Click the **"Fork"** button in the top-right corner
3. This creates a copy of the repository under your GitHub account

#### **Step 2: Clone Your Forked Repository**
```bash
# Clone your fork (replace 'yourusername' with your GitHub username)
git clone https://github.com/yourusername/opencodehub.git

# Navigate to the project directory
cd opencodehub
```

---

### 📌 **Option 2: Just Using the Project (Direct Clone)**

If you just want to use the application without contributing:

```bash
# Clone the repository directly
git clone https://github.com/yourusername/opencodehub.git

# Navigate to the project directory
cd opencodehub
```

---

### 🔧 **Common Setup Steps (After Cloning)**

#### **Step 1: Create a Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

**Verify Activation:**
```bash
# Check if virtual environment is active
where python

# Should point to the venv directory
```

---

#### **Step 2: Create Environment Variables File**

Create a `.env` file in the project root directory (same level as `manage.py`):

Add the following configuration to `.env`:

```env
# Supabase Database URL (PostgreSQL)
DATABASE_URL=postgresql://postgres.xxxxx:your-password@aws-x-xx-xxxxx-x.pooler.supabase.com:5432/postgres?sslmode=require
```

**⚠️ Important Security Notes:**
- Never commit `.env` to version control
- Keep your database password confidential
- Each team member should have their own .env file with their own credentials
  
---

#### **Step 3: Install Project Dependencies**

```bash
# Make sure your virtual environment is activated (you should see (venv) in the prompt)

# Install all required packages from requirements.txt
pip install -r requirements.txt

# Wait for all packages to install (this may take a few minutes)
```

**Verify Installation:**
```bash
# Check installed packages
pip list

# You should see Django, and other dependencies
```
---

#### **Step 4: Run the Development Server**

```bash
# Start the Django development server
python manage.py runserver

# Server will start on http://127.0.0.1:8000/
```
---

#### **Step 8: Access the Application**

Open your web browser and navigate to:

**Main Application:**
```
http://127.0.0.1:8000/
```

**Admin Panel:**
```
http://127.0.0.1:8000/admin/
```
**Available Pages:**
- Home: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Register: `http://127.0.0.1:8000/register/`
- Dashboard: `http://127.0.0.1:8000/dashboard/` (requires login)

---

## 👥 Team Members

**Project Managers**
| Name | Role | CIT-U Email |
|------|------|-------------|
| **Dexter Dela Riarte** | Product Owner | dexter.delariarte@cit.edu |
| **Erica Y. Dabalos** | Business Analyst | erica.dabalos@cit.edu |
| **Nico John G. Colo** | Scrum Master | nicojohn.colo@cit.edu |
| **Theo Cedric P. Chan** | Scrum Master | theocedric.chan@cit.edu |

**Developers**
| Name | Role | CIT-U Email |
|------|------|-------------|
| **Ashley Igonia** | Lead Full Stack Developer | ashley.igonia@cit.edu |
| **Louis Drey F. Castañeto** | Backend Developer | louisdrey.castañeto@cit.edu |
| **Nikolai R. Javier** | Frontend Developer | nikolai.javier@cit.edu |

**Academic Instructors**
| Name | Role |
|------|------|
| **Frederick Revilleza** | CSIT327 Instructor |
| **Joemarie Amparo** | IT317 Instructor |
---

## 🌐 Deployment
https://csit327-g8-opencodehub-mciy.onrender.com/



<div align="center">
  <p>Made with ❤️ by the OpenCodeHub Team</p>
  <p>© 2025 OpenCodeHub. All rights reserved.</p>
  <br>
  <a href="#-opencodehub">Back to Top ⬆️</a>
</div>
