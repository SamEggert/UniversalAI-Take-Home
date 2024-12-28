import azure.functions as func
from app.utils.cleanup_utility import cleanup_storage_and_db
from app.utils.cors import cors_headers
import logging

def clear_data(req: func.HttpRequest) -> func.HttpResponse:
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        result = cleanup_storage_and_db()
        return func.HttpResponse(
            "Data cleared successfully",
            status_code=200,
            headers=cors_headers
        )
    except Exception as e:
        logging.error(f"Error clearing data: {str(e)}")
        return func.HttpResponse(
            f"Error clearing data: {str(e)}",
            status_code=500,
            headers=cors_headers
        )