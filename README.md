# Antisubscription - Monitoring System Against Paid Subscriptions and Recurring Payments

## Overview

Antisubscription is a Flask-based email monitoring system that analyses IMAP
mailboxes for subscription and recurring payment notifications. Messages that
match configurable keywords are persisted in PostgreSQL where they can be
queried through a REST API. The project is intentionally lightweight so that it
can be deployed locally with Docker Compose or embedded in existing monitoring
solutions.

The latest release modernises the codebase, introduces richer API endpoints and
provides documentation assets such as an OpenAPI contract and a C4 architecture
model.

---

## Features

- **Email Ingestion via IMAP** – Connects to any IMAP compatible provider and
  scans messages for subscription-related keywords.
- **Keyword Matching** – Uses configurable keyword lists to determine whether a
  message is a potential subscription notification.
- **PostgreSQL Storage** – Persists subscription hints for further analysis.
- **Flask REST API** – Provides endpoints for listing, aggregating and analysing
  subscriptions as well as a backwards compatible `/senders` endpoint.
- **Recurring Sender Detection** – Highlights senders that contact a recipient on
  a regular schedule.
- **Docker Support** – Easily deployable with Docker and Docker Compose.
- **Documentation Assets** – Includes an OpenAPI specification and a C4 model to
  help newcomers understand the system.

---

## Project Structure

```
├── assets/
│   └── anti_table.sql            # SQL script for database setup
├── docs/
│   ├── architecture/
│   │   └── c4-model.md           # C4 context + container diagrams
│   └── openapi.yaml              # HTTP API contract
├── libs/
│   ├── __init__.py               # Package initialisation
│   ├── imaplib.py                # Vendored IMAP library (used by app_yandex)
│   ├── key_values_scan.py        # Legacy keyword helpers
│   └── subscription.py           # Subscription detection logic
├── static_html/
│   ├── js/                       # JavaScript files
│   └── index.html                # Main HTML file
├── .env.example                  # Example environment variables
├── app.py                        # Flask application entry point
├── app_yandex.py                 # IMAP ingestion helpers
├── connect_db.py                 # PostgreSQL helpers
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image configuration
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## Installation

### 1. Local Installation (Without Docker)

#### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- `pip`

#### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/antisubscription.git
   cd antisubscription
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Copy `.env.example` to `.env` and provide the required values or export the
   variables manually. At minimum the database credentials and IMAP settings
   must be configured.

5. **Run the application**
   ```bash
   flask --app app run --debug
   ```
   The API will be available at `http://localhost:5000`.

### 2. Running with Docker

#### Prerequisites

- Docker
- Docker Compose

#### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/antisubscription.git
   cd antisubscription
   ```

2. **Provide configuration**
   Copy `.env.example` to `.env` and adjust credentials if required.

3. **Build and start the containers**
   ```bash
   docker-compose up --build -d
   ```

4. **Check running containers**
   ```bash
   docker ps
   ```

5. **Access the Flask API**
   Open `http://localhost:5000` in a browser or use your favourite HTTP client.

---

## Configuration

### Environment Variables

| Variable        | Description                                 | Default             |
|-----------------|---------------------------------------------|---------------------|
| `mail_service`  | IMAP server address                         | –                   |
| `login`         | IMAP login                                  | –                   |
| `password`      | IMAP password or app-specific token         | –                   |
| `mail_service_gmail` | Optional Gmail IMAP server             | –                   |
| `login_gmail`   | Optional Gmail login                        | –                   |
| `password_gmail`| Optional Gmail password                     | –                   |
| `user_login`    | PostgreSQL username                         | –                   |
| `user_pass`     | PostgreSQL password                         | –                   |
| `pg_host`       | PostgreSQL host                             | `db`                |
| `pg_port`       | PostgreSQL port                             | `5432`              |
| `pg_database`   | PostgreSQL database name                    | `antipodpiska`      |

The `.env.example` file contains the variables with sample values. Populate it
and rename to `.env` for local development.

---

## API Endpoints

The API is documented through `docs/openapi.yaml`. The most commonly used
endpoints are summarised below:

### Health Check
- **Endpoint:** `GET /health`
- **Description:** Returns a simple status object that can be used by monitoring
  systems.

### Trigger Mailbox Synchronisation
- **Endpoint:** `POST /account`
- **Body:**
  ```json
  {
    "mail_service": "imap.example.com",
    "login": "your_email@example.com",
    "password": "your_password",
    "keywords": ["subscription", "invoice", "payment"],
    "lookback_days": 365,
    "max_messages": 200
  }
  ```
- **Description:** Fetches messages from the specified mailbox and stores
  subscription matches in the database.

### List Stored Subscriptions
- **Endpoint:** `GET /subscriptions`
- **Query Parameters:** `recipient`, `sender`, `start`, `end`, `limit`
- **Description:** Returns stored subscription events filtered by the provided
  criteria.

### Summarise Subscriptions
- **Endpoint:** `GET /subscriptions/summary`
- **Description:** Aggregates stored events by sender including the number of
  occurrences and the last time a message was seen.

### Detect Periodic Senders
- **Endpoint:** `GET /subscriptions/periodic`
- **Query Parameters:** `recipient`, `min_gap_days`, `min_events`
- **Description:** Identifies senders that contact a recipient regularly.

### Legacy Endpoint
- **Endpoint:** `GET /senders`
- **Description:** Maintains the historical API contract while returning the new
  data model.

A complete specification including schemas and status codes can be found in
`docs/openapi.yaml`.

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

## Dependencies

Core dependencies are listed in `requirements.txt` and include:

- Flask 2.3.x
- dateparser 1.2.x
- psycopg2-binary 2.9.x
- python-dotenv 1.0.x

Install them with:

```bash
pip install -r requirements.txt
```

---

## Documentation Assets

- **OpenAPI specification:** [`docs/openapi.yaml`](docs/openapi.yaml)
- **C4 Architecture Model:** [`docs/architecture/c4-model.md`](docs/architecture/c4-model.md)

---

## Contribution

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License.

---

## Author

Developed by **Alex Shaman**.
