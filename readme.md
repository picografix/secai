# SecAI: Financial Data API

SecAI is a FastAPI-based application that provides financial data through a robust API. It includes caching mechanisms using Redis and PostgreSQL for efficient data retrieval and storage.

## Table of Contents
1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [API Usage](#api-usage)
8. [Caching](#caching)
9. [Google Apps Script Integration](#google-apps-script-integration)
10. [Contributing](#contributing)
11. [License](#license)

## Features

- FastAPI-based RESTful API
- Redis caching for quick data retrieval
- PostgreSQL database for persistent storage
- Google Apps Script integration for easy data access in Google Sheets

## Prerequisites

- Python 3.7+
- PostgreSQL
- Redis
- Git

## Installation

1. Clone the repository:
   ```
   git clone git@github.com:picografix/secai.git
   cd secai
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific configuration:
   ```
   PROJECT_NAME=getData API
   REDIS_URL=redis://localhost:6379/0
   DATABASE_URL=postgresql://username:password@localhost:5432/secai
   ```

## Database Setup

1. Create the PostgreSQL database:
   ```
   createdb secai
   ```

2. Run database migrations:
   ```
   alembic upgrade head
   ```

To clean the database:
```
alembic downgrade base
```

To create a new migration after model changes:
```
alembic revision --autogenerate -m "Description of changes"
```

## Running the Application

Start the FastAPI server:
```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Usage

### Get Data Endpoint

```http
POST /getData
Content-Type: application/json

{
  "header": "string",
  "year": "string",
  "sheetName": "string",
  "ticker": "string",
  "force_reload": false
}
```

## Caching

The application uses a two-level caching system:
1. Redis for fast, in-memory caching
2. PostgreSQL for persistent caching

Cache invalidation is handled through the `force_reload` parameter in API requests.

## Google Apps Script Integration

To use the API in Google Sheets:

1. Open your Google Sheet
2. Go to Tools > Script editor
3. Paste the following code:

```javascript
function getSecData(header, year, sheetName, ticker, forceReload = false) {
  var apiUrl = "https://your-api-endpoint.com/getData";
  
  var payload = {
    header: header,
    year: year,
    sheetName: sheetName,
    ticker: ticker,
    force_reload: forceReload
  };
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  };
  
  try {
    var response = UrlFetchApp.fetch(apiUrl, options);
    var jsonResponse = JSON.parse(response.getContentText());
    return jsonResponse.extracted_data;
  } catch (error) {
    console.error("API call failed: " + error);
    return "Error: " + error.toString();
  }
}
```

Replace `"https://your-api-endpoint.com/getData"` with your actual API endpoint.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)