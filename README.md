# Antisubscription - Monitoring System Against Paid Subscriptions and Recurring Payments

## Overview

Antisubscription is a Flask-based email monitoring system that detects the appearance of paid subscriptions and recurring payments based on email notifications. The system connects to an email account via IMAP, extracts relevant emails, identifies subscription-related messages, and stores the information in a PostgreSQL database for further analysis.

The application is designed to help users track new paid subscriptions and analyze recurring payments.

---

## Features

- **Email Fetching via IMAP**: Connects to various email services to retrieve messages.
- **Subscription Detection**: Identifies emails related to paid subscriptions using keyword analysis.
- **PostgreSQL Storage**: Stores extracted data for further analysis.
- **Flask API**: Provides RESTful endpoints for querying stored email data.
- **Docker Support**: Easily deployable using Docker and Docker Compose.
- **Keyword Matching**: Uses predefined keywords to detect subscription-related emails.

---

## Project Structure

```
├── assets/
│   ├── anti_table.sql            # SQL script for database setup
├── libs/
│   ├── __init__.py               # Package initialization
│   ├── imaplib.py                # IMAP handling logic
│   ├── key_values_scan.py        # Keyword analysis for subscriptions
│   ├── subscription.py           # Subscription detection logic
├── static_html/
│   ├── js/                       # JavaScript files
│   ├── index.html                # Main HTML file
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore file
├── app_old_get.py                # Legacy API endpoint (for reference)
├── app_yandex.py                 # Email fetching logic (Yandex Mail)
├── app.py                        # Main Flask application
├── application.yml               # Configuration file (database settings)
├── config.py                     # Application configuration (environment variables)
├── connect_db.py                 # Database connection logic
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image configuration
├── models.py                     # Database models
├── one_mail_ya.py                # Script for fetching a single email (for testing)
├── README.md                     # Project documentation
└── requirements.txt               # Project dependencies
```

---

## Installation

### 1. Local Installation (Without Docker)

#### Prerequisites:
- Python 3.8+
- PostgreSQL
- `pip` (Python package manager)

#### Steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/antisubscription.git
   cd antisubscription
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (or use a `.env` file)
   ```bash
   export mail_service="imap.example.com"
   export login="your_email@example.com"
   export password="your_password"
   export user_login="db_user"
   export user_pass="db_password"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

---

### 2. Running with Docker

#### Prerequisites:
- Docker
- Docker Compose

#### Steps:

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/antisubscription.git
   cd antisubscription
   ```

2. **Build and start the containers**
   ```bash
   docker-compose up --build -d
   ```

3. **Check running containers**
   ```bash
   docker ps
   ```

4. **Access the Flask API**
   ```
   http://localhost:5000
   ```

---

## API Endpoints

### 1. Fetch Subscription Data
**Endpoint:** `GET /senders`

**Query Parameters:**
- `login` - Email address of the recipient

**Example Request:**
```bash
curl -X GET "http://localhost:5000/senders?login=your_email@example.com"
```

---

### 2. Submit Account Credentials
**Endpoint:** `POST /account`

**Request Body:**
```json
{
  "mail_service": "imap.example.com",
  "login": "your_email@example.com",
  "password": "your_password",
  "keyWords": "subscribe payment invoice"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/account" -H "Content-Type: application/json" -d '{
  "mail_service": "imap.example.com",
  "login": "your_email@example.com",
  "password": "your_password",
  "keyWords": "subscribe payment invoice"
}'
```

---

## Configuration

### Environment Variables:
| Variable        | Description                  |
|----------------|------------------------------|
| `mail_service` | IMAP server address          |
| `login`        | Email login                  |
| `password`     | Email password               |
| `user_login`   | PostgreSQL username          |
| `user_pass`    | PostgreSQL password          |

---

## Dependencies

The project relies on the following Python libraries:

| Library            | Version |
|--------------------|---------|
| Flask             | 2.0.1   |
| Flask-SQLAlchemy  | 2.5.1   |
| Flask-Cors        | 3.0.10  |
| psycopg2-binary   | 2.9.1   |
| SQLAlchemy        | 1.4.20  |
| dateparser        | 1.0.0   |
| python-dotenv     | 0.18.0  |

To install them manually, run:
```bash
pip install -r requirements.txt
```

---

## Database Schema (PostgreSQL)

The project uses a PostgreSQL database with the following schema:

```sql
CREATE TABLE public.anti (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(255),
    email VARCHAR(255),
    send_date TIMESTAMP,
    recipient VARCHAR(255),
    subscription INT
);
```

---

## Contribution

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Added a new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License.

---

## Author

Developed by **Alex Shaman**.

