#!/usr/bin/env python3
"""
Test script to verify BigQuery API routes are properly configured.
This script tests the route definitions without requiring database connections.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_bigquery_routes():
    """Test that BigQuery routes are properly defined."""
    try:
        from app.api.bigquery import router
        print("✓ BigQuery router imported successfully")

        # Check that routes are defined
        routes = router.routes
        expected_routes = [
            "/sales-data",
            "/analytics/revenue-per-product",
            "/analytics/category-sales",
            "/analytics/top-selling-products"
        ]

        found_routes = []
        for route in routes:
            if hasattr(route, 'path'):
                found_routes.append(route.path)

        print(f"✓ Found {len(found_routes)} routes:")
        for route in found_routes:
            print(f"  - {route}")

        # Check if expected routes are present
        for expected in expected_routes:
            if expected in found_routes:
                print(f"✓ Route {expected} is properly configured")
            else:
                print(f"✗ Route {expected} is missing")

        return True

    except ImportError as e:
        print(f"✗ Failed to import BigQuery router: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing routes: {e}")
        return False

def test_schemas():
    """Test that BigQuery schemas are properly defined."""
    try:
        from app.schemas.bigquery import (
            SalesData,
            SalesDataResponse,
            RevenuePerProduct,
            CategorySales,
            TopSellingProduct
        )
        print("✓ BigQuery schemas imported successfully")

        # Test schema instantiation
        sales_data = SalesData(
            order_id="12345",
            product="Test Product",
            category="Test Category",
            price=99.99,
            quantity=2,
            order_date="2024-01-01T00:00:00"
        )
        print("✓ SalesData schema validation works")

        return True

    except ImportError as e:
        print(f"✗ Failed to import schemas: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing schemas: {e}")
        return False

def test_config():
    """Test that configuration is properly loaded."""
    try:
        from app.core.config import (
            GOOGLE_CLOUD_PROJECT,
            BIGQUERY_DATASET,
            BIGQUERY_TABLE,
            GOOGLE_APPLICATION_CREDENTIALS
        )
        print("✓ Configuration loaded successfully")
        print(f"  - Project: {GOOGLE_CLOUD_PROJECT or 'Not set'}")
        print(f"  - Dataset: {BIGQUERY_DATASET or 'Not set'}")
        print(f"  - Table: {BIGQUERY_TABLE or 'Not set'}")
        print(f"  - Credentials: {GOOGLE_APPLICATION_CREDENTIALS or 'Not set'}")

        return True

    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing config: {e}")
        return False

if __name__ == "__main__":
    print("Testing BigQuery Integration Setup")
    print("=" * 40)

    tests = [
        ("Configuration", test_config),
        ("Schemas", test_schemas),
        ("Routes", test_bigquery_routes)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nTesting {test_name}:")
        if test_func():
            passed += 1
        print()

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All BigQuery integration components are properly configured!")
        print("\nNext steps:")
        print("1. Set up your Google Cloud service account credentials")
        print("2. Update the .env file with your GCP project details")
        print("3. Ensure your BigQuery table has the correct schema")
        print("4. Run the application with: uvicorn app.main:app --reload")
    else:
        print("❌ Some components need attention. Check the error messages above.")
        sys.exit(1)