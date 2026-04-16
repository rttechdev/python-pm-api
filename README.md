# Python PM API

A FastAPI-based project management API with PostgreSQL database and Google Cloud BigQuery integration for sales analytics.

## Features

- User authentication and management
- Organization management
- **Sales Analytics via Google Cloud BigQuery**
  - Fetch sales data with filtering
  - Revenue analysis per product
  - Category-wise sales analytics
  - Top selling products

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Cloud Platform account with BigQuery enabled
- Service account key file for GCP

### Installation

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Database Setup**: Update the `.env` file with your PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/your_database
   ```

2. **Google Cloud BigQuery Setup**:
   - Create a service account in Google Cloud Console
   - Download the service account key JSON file
   - Update the `.env` file with your GCP configuration:
   ```
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   BIGQUERY_DATASET=your-dataset-name
   BIGQUERY_TABLE=your-table-name
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
   ```

3. **BigQuery Table Schema**: Ensure your BigQuery table has the following columns:
   - `order_id` (STRING)
   - `product` (STRING)
   - `category` (STRING)
   - `price` (FLOAT)
   - `quantity` (INTEGER)
   - `order_date` (TIMESTAMP or DATE)

### Running the Application

#### With Docker (Recommended for full setup)

```bash
docker-compose up --build
```

#### Without Docker (for development)

1. Start PostgreSQL database
2. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /users` - Create new user
- `POST /auth/login` - User login

### Organization Management
- `GET /organizations` - List organizations
- `POST /organizations` - Create organization

### BigQuery Sales Analytics

All BigQuery endpoints are prefixed with `/api/v1`:

#### Fetch Sales Data
```
GET /api/v1/sales-data
```
**Query Parameters:**
- `limit` (int, default: 100) - Maximum records to return
- `offset` (int, default: 0) - Records to skip
- `product` (str, optional) - Filter by product name
- `category` (str, optional) - Filter by category
- `start_date` (str, optional) - Start date (YYYY-MM-DD)
- `end_date` (str, optional) - End date (YYYY-MM-DD)

#### Revenue per Product
```
GET /api/v1/analytics/revenue-per-product
```
**Query Parameters:**
- `limit` (int, default: 50) - Maximum products to return
- `category` (str, optional) - Filter by category

#### Category-wise Sales
```
GET /api/v1/analytics/category-sales
```
Returns sales aggregated by category.

#### Top Selling Products
```
GET /api/v1/analytics/top-selling-products
```
**Query Parameters:**
- `limit` (int, default: 10) - Maximum products to return
- `category` (str, optional) - Filter by category

## API Documentation

Once the application is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Development

### Project Structure
```
app/
├── api/           # API route handlers
│   ├── auth.py
│   ├── user.py
│   ├── organization.py
│   └── bigquery.py    # BigQuery analytics endpoints
├── core/          # Core functionality
│   ├── config.py  # Configuration settings
│   └── security.py
├── db/            # Database setup
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
│   └── bigquery.py    # BigQuery data schemas
└── main.py        # FastAPI application entry point
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Yes (for BigQuery) |
| `BIGQUERY_DATASET` | BigQuery dataset name | Yes (for BigQuery) |
| `BIGQUERY_TABLE` | BigQuery table name | Yes (for BigQuery) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key | Yes (for BigQuery) |

## Error Handling

The BigQuery endpoints include comprehensive error handling:
- Returns 500 error if BigQuery client is not initialized
- Handles GCP API errors gracefully
- Validates input parameters

## Security Notes

- Service account credentials are loaded from the file system
- Ensure the service account has appropriate BigQuery permissions:
  - `bigquery.jobs.create`
  - `bigquery.tables.getData`
- Store the service account key file securely and never commit it to version control
