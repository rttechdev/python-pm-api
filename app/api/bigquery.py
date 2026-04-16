"""
BigQuery API endpoints for sales data analytics.

This module defines API routes for fetching sales data from Google Cloud BigQuery
and performing various analytics operations like revenue calculations and top products.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import os

from app.schemas.bigquery import (
    SalesDataResponse,
    RevenuePerProduct,
    CategorySales,
    TopSellingProduct,
    AnalyticsResponse
)
from app.core.config import (
    GOOGLE_CLOUD_PROJECT,
    BIGQUERY_DATASET,
    BIGQUERY_TABLE,
    GOOGLE_APPLICATION_CREDENTIALS
)

# Create router for BigQuery analytics endpoints
router = APIRouter(tags=["BigQuery Analytics"])

# Create separate router for BigQuery ML endpoints
ml_router = APIRouter(tags=["BigQuery ML"])

# Initialize BigQuery client
bq_client = None
bigquery = None
GoogleAPIError = None

try:
    from google.cloud import bigquery
    from google.api_core.exceptions import GoogleAPIError

    # Set up Google Cloud credentials if a service account file path is provided
    if GOOGLE_APPLICATION_CREDENTIALS:
        if os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
        else:
            print(f"Warning: GOOGLE_APPLICATION_CREDENTIALS file not found: {GOOGLE_APPLICATION_CREDENTIALS}. Trying default credentials.")

    # Initialize BigQuery client. On Cloud Run, this will use default credentials if available.
    try:
        bq_client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    except Exception as e:
        print(f"Warning: Failed to initialize BigQuery client: {e}")

except ImportError:
    print("Warning: Google Cloud BigQuery dependencies not installed")


def get_table_ref() -> str:
    """Get the full BigQuery table reference."""
    return f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"


@router.get("/sales-data", response_model=SalesDataResponse)
async def get_sales_data(
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    product: Optional[str] = Query(None, description="Filter by product name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Fetch sales data from BigQuery with optional filtering.

    Returns paginated sales records with optional filters for product, category, and date range.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")

    try:
        # Build the base query
        query = f"""
        SELECT
            order_id,
            product,
            category,
            price,
            quantity,
            order_date
        FROM `{get_table_ref()}`
        WHERE 1=1
        """

        # Build query parameters list
        query_params = []

        # Add filters
        if product:
            query += " AND LOWER(product) LIKE LOWER(@product)"
            query_params.append(bigquery.ScalarQueryParameter("product", "STRING", f"%{product}%"))

        if category:
            query += " AND LOWER(category) = LOWER(@category)"
            query_params.append(bigquery.ScalarQueryParameter("category", "STRING", category))

        if start_date:
            query += " AND DATE(order_date) >= @start_date"
            query_params.append(bigquery.ScalarQueryParameter("start_date", "DATE", start_date))

        if end_date:
            query += " AND DATE(order_date) <= @end_date"
            query_params.append(bigquery.ScalarQueryParameter("end_date", "DATE", end_date))

        # Add pagination
        query += " ORDER BY order_date DESC LIMIT @limit OFFSET @offset"
        query_params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))
        query_params.append(bigquery.ScalarQueryParameter("offset", "INT64", offset))

        # Execute query
        query_job = bq_client.query(query, job_config=bigquery.QueryJobConfig(
            query_parameters=query_params
        ))

        results = query_job.result()

        # Convert to list of dicts
        data = []
        for row in results:
            data.append({
                "order_id": str(row.order_id),  # Convert to string for consistency
                "product": row.product,
                "category": row.category,
                "price": float(row.price),
                "quantity": int(row.quantity),
                "order_date": row.order_date
            })

        # Get total count for pagination info
        count_query = f"""
        SELECT COUNT(*) as total
        FROM `{get_table_ref()}`
        WHERE 1=1
        """
        count_params = []

        if product:
            count_query += " AND LOWER(product) LIKE LOWER(@product)"
            count_params.append(bigquery.ScalarQueryParameter("product", "STRING", f"%{product}%"))
        if category:
            count_query += " AND LOWER(category) = LOWER(@category)"
            count_params.append(bigquery.ScalarQueryParameter("category", "STRING", category))
        if start_date:
            count_query += " AND DATE(order_date) >= @start_date"
            count_params.append(bigquery.ScalarQueryParameter("start_date", "DATE", start_date))
        if end_date:
            count_query += " AND DATE(order_date) <= @end_date"
            count_params.append(bigquery.ScalarQueryParameter("end_date", "DATE", end_date))

        count_job = bq_client.query(count_query, job_config=bigquery.QueryJobConfig(
            query_parameters=count_params
        ))
        count_result = count_job.result()
        total_records = next(count_result).total

        return SalesDataResponse(data=data, total_records=total_records)

    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sales data: {str(e)}")


@router.get("/analytics/revenue-per-product", response_model=List[RevenuePerProduct])
async def get_revenue_per_product(
    limit: int = Query(50, description="Maximum number of products to return"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get total revenue per product.

    Returns products sorted by total revenue in descending order.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")

    try:
        query = f"""
        SELECT
            product,
            SUM(price * quantity) as total_revenue,
            SUM(quantity) as total_quantity
        FROM `{get_table_ref()}`
        """

        query_params = []
        
        if category:
            query += " WHERE LOWER(category) = LOWER(@category)"
            query_params.append(bigquery.ScalarQueryParameter("category", "STRING", category))

        query += """
        GROUP BY product
        ORDER BY total_revenue DESC
        LIMIT @limit
        """

        query_params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))

        query_job = bq_client.query(query, job_config=bigquery.QueryJobConfig(
            query_parameters=query_params
        ))

        results = query_job.result()

        data = []
        for row in results:
            data.append({
                "product": row.product,
                "total_revenue": float(row.total_revenue),
                "total_quantity": int(row.total_quantity)
            })

        return data

    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching revenue data: {str(e)}")


@router.get("/analytics/category-sales", response_model=List[CategorySales])
async def get_category_sales():
    """
    Get category-wise sales analytics.

    Returns sales data aggregated by category including total revenue, quantity, and product count.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")

    try:
        query = f"""
        SELECT
            category,
            SUM(price * quantity) as total_revenue,
            SUM(quantity) as total_quantity,
            COUNT(DISTINCT product) as product_count
        FROM `{get_table_ref()}`
        GROUP BY category
        ORDER BY total_revenue DESC
        """

        query_job = bq_client.query(query)
        results = query_job.result()

        data = []
        for row in results:
            data.append({
                "category": row.category,
                "total_revenue": float(row.total_revenue),
                "total_quantity": int(row.total_quantity),
                "product_count": int(row.product_count)
            })

        return data

    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching category sales: {str(e)}")


@router.get("/analytics/top-selling-products", response_model=List[TopSellingProduct])
async def get_top_selling_products(
    limit: int = Query(10, description="Maximum number of products to return"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get top selling products by quantity.

    Returns products sorted by total quantity sold in descending order.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")

    try:
        query = f"""
        SELECT
            product,
            category,
            SUM(quantity) as total_quantity,
            SUM(price * quantity) as total_revenue
        FROM `{get_table_ref()}`
        """

        query_params = []
        
        if category:
            query += " WHERE LOWER(category) = LOWER(@category)"
            query_params.append(bigquery.ScalarQueryParameter("category", "STRING", category))

        query += """
        GROUP BY product, category
        ORDER BY total_quantity DESC
        LIMIT @limit
        """

        query_params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))

        query_job = bq_client.query(query, job_config=bigquery.QueryJobConfig(
            query_parameters=query_params
        ))

        results = query_job.result()

        data = []
        for row in results:
            data.append({
                "product": row.product,
                "category": row.category,
                "total_quantity": int(row.total_quantity),
                "total_revenue": float(row.total_revenue)
            })

        return data

    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top products: {str(e)}")


# ==================== BigQuery ML Endpoints ====================

@ml_router.post("/ml/train-sales-forecast")
async def train_sales_forecast_model():
    """
    Train a time series forecasting model using BigQuery ML.
    
    Creates a linear regression model to predict future sales trends.
    This is a one-time or periodic operation that trains the model on historical data.
    
    Returns:
        Model training status and information.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")
    
    try:
        model_name = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.sales_forecast_model"
        
        # SQL to create/train the model
        create_model_query = f"""
        CREATE OR REPLACE MODEL `{model_name}`
        OPTIONS(
            model_type='linear_reg',
            input_label_cols=['total_revenue']
        ) AS
        SELECT
            EXTRACT(YEAR FROM order_date) as year,
            EXTRACT(MONTH FROM order_date) as month,
            EXTRACT(DAY FROM order_date) as day,
            SUM(price * quantity) as total_revenue
        FROM `{get_table_ref()}`
        GROUP BY year, month, day
        HAVING total_revenue IS NOT NULL
        ORDER BY year, month, day;
        """
        
        query_job = bq_client.query(create_model_query)
        query_job.result()  # Wait for job to complete
        
        return {
            "status": "success",
            "message": "Sales forecast model trained successfully",
            "model_name": model_name,
            "model_type": "linear_reg",
            "description": "Predicts total daily revenue based on historical sales data"
        }
    
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery ML error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@ml_router.get("/ml/forecast-revenue", tags=["BigQuery ML"])
async def forecast_revenue(
    days_ahead: int = Query(7, description="Number of days to forecast (1-30)", ge=1, le=30),
    category: Optional[str] = Query(None, description="Filter forecast by category")
):
    """
    Forecast future revenue using the trained BigQuery ML model.
    
    Uses the trained linear regression model to predict revenue for upcoming days.
    
    Args:
        days_ahead: Number of days to forecast (1-30)
        category: Optional category filter for the forecast
    
    Returns:
        List of forecasted revenue values with dates and confidence intervals.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")
    
    try:
        model_name = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.sales_forecast_model"
        
        # Get latest date from data
        latest_date_query = f"SELECT MAX(order_date) as max_date FROM `{get_table_ref()}`"
        latest_result = bq_client.query(latest_date_query).result()
        max_date = next(latest_result).max_date
        
        # Generate future dates
        forecast_query = f"""
        WITH future_dates AS (
            SELECT
                EXTRACT(YEAR FROM future_date) as year,
                EXTRACT(MONTH FROM future_date) as month,
                EXTRACT(DAY FROM future_date) as day,
                future_date
            FROM (
                SELECT
                    DATE_ADD('{max_date}', INTERVAL n DAY) as future_date
                FROM UNNEST(GENERATE_ARRAY(1, {days_ahead})) as n
            )
        )
        SELECT
            future_date,
            ROUND(predicted_total_revenue, 2) as predicted_revenue,
            ROUND(predicted_total_revenue * 0.85, 2) as lower_bound,
            ROUND(predicted_total_revenue * 1.15, 2) as upper_bound
        FROM ML.PREDICT(MODEL `{model_name}`, TABLE future_dates)
        ORDER BY future_date;
        """
        
        results = bq_client.query(forecast_query).result()
        
        forecast_data = []
        for row in results:
            forecast_data.append({
                "date": str(row.future_date),
                "predicted_revenue": float(row.predicted_revenue),
                "lower_bound": float(row.lower_bound),
                "upper_bound": float(row.upper_bound)
            })
        
        return {
            "status": "success",
            "forecast_days": days_ahead,
            "data": forecast_data,
            "description": "Revenue forecast with 15% confidence interval"
        }
    
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery ML error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@ml_router.post("/ml/train-demand-predictor")
async def train_demand_predictor():
    """
    Train a demand prediction model using BigQuery ML.
    
    Creates a linear regression model to predict product quantity demand
    based on product, category, and price.
    
    Returns:
        Model training status and information.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")
    
    try:
        model_name = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.demand_predictor"
        
        create_model_query = f"""
        CREATE OR REPLACE MODEL `{model_name}`
        OPTIONS(
            model_type='linear_reg',
            input_label_cols=['quantity']
        ) AS
        SELECT
            product,
            category,
            CAST(price AS FLOAT64) as price,
            month,
            quarter,
            quantity
        FROM (
            SELECT
                product,
                category,
                CAST(price AS FLOAT64) as price,
                EXTRACT(MONTH FROM order_date) as month,
                EXTRACT(QUARTER FROM order_date) as quarter,
                quantity,
                ROW_NUMBER() OVER (PARTITION BY product ORDER BY order_date DESC) AS row_num
            FROM `{get_table_ref()}`
            WHERE quantity IS NOT NULL
        )
        WHERE row_num <= 100;
        """
        
        query_job = bq_client.query(create_model_query)
        query_job.result()
        
        return {
            "status": "success",
            "message": "Demand predictor model trained successfully",
            "model_name": model_name,
            "model_type": "linear_reg",
            "description": "Predicts product quantity demand based on category, price, and temporal features"
        }
    
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery ML error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training demand model: {str(e)}")


@ml_router.get("/ml/predict-demand")
async def predict_demand(
    product: str = Query(..., description="Product name"),
    category: str = Query(..., description="Product category"),
    price: float = Query(..., description="Product price")
):
    """
    Predict product demand using the trained BigQuery ML model.
    
    Predicts the quantity demand for a product based on its characteristics.
    
    Args:
        product: Product name
        category: Product category
        price: Product price
    
    Returns:
        Predicted quantity and confidence metrics.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")
    
    try:
        model_name = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.demand_predictor"
        
        predict_query = f"""
        SELECT
            ROUND(m.predicted_quantity, 0) as predicted_quantity,
            ROUND(m.predicted_quantity * 0.8, 0) as min_demand,
            ROUND(m.predicted_quantity * 1.2, 0) as max_demand
        FROM ML.PREDICT(MODEL `{model_name}`, (
            SELECT
                '{product}' as product,
                '{category}' as category,
                CAST({price} AS FLOAT64) as price,
                EXTRACT(MONTH FROM CURRENT_DATE()) as month,
                EXTRACT(QUARTER FROM CURRENT_DATE()) as quarter
        )) m;
        """
        
        results = bq_client.query(predict_query).result()
        row = next(results)
        
        return {
            "status": "success",
            "product": product,
            "category": category,
            "price": price,
            "prediction": {
                "predicted_quantity": int(row.predicted_quantity),
                "min_demand": int(row.min_demand),
                "max_demand": int(row.max_demand)
            },
            "description": "Predicted demand with 20% confidence interval"
        }
    
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery ML error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting demand: {str(e)}")


@ml_router.get("/ml/model-evaluation")
async def get_model_evaluation(
    model_name: str = Query("sales_forecast_model", description="Model to evaluate")
):
    """
    Get evaluation metrics for a trained BigQuery ML model.
    
    Returns model performance metrics including R-squared, RMSE, etc.
    
    Args:
        model_name: Name of the model to evaluate
    
    Returns:
        Model evaluation metrics and performance indicators.
    """
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized")
    
    try:
        full_model_name = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.{model_name}"
        
        eval_query = f"""
        SELECT
            mean_absolute_error,
            mean_squared_error,
            SQRT(mean_squared_error) AS rmse,
            r2_score,
            explained_variance
        FROM ML.EVALUATE(MODEL `{full_model_name}`);
        """
        
        results = bq_client.query(eval_query).result()
        row = next(results)
        
        return {
            "status": "success",
            "model_name": model_name,
            "evaluation_metrics": {
                "mean_absolute_error": float(row.mean_absolute_error) if row.mean_absolute_error else None,
                "mean_squared_error": float(row.mean_squared_error) if row.mean_squared_error else None,
                "rmse": float(row.rmse) if row.rmse else None,
                "r2_score": float(row.r2_score) if row.r2_score else None,
                "explained_variance": float(row.explained_variance) if row.explained_variance else None
            },
            "description": "Model performance metrics - higher R2 and lower RMSE indicate better fit"
        }
    
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery ML error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating model: {str(e)}")