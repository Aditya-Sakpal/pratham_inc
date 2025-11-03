"""
AWS Lambda handler for FastAPI application
Uses Mangum to adapt ASGI app to Lambda
"""
import logging
import traceback
import json
from mangum import Mangum

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    from main import app
    # Create Lambda handler with text_mime_types to handle JSON properly
    mangum_handler = Mangum(
        app, 
        lifespan="off",
        text_mime_types=["application/json", "text/plain", "text/event-stream"]
    )
    logger.info("Lambda handler initialized successfully")
    
    # CORS is handled by Lambda Function URL - no need to add headers here
    handler = mangum_handler
            
except Exception as e:
    logger.error(f"Failed to initialize Lambda handler: {str(e)}")
    logger.error(traceback.format_exc())
    # Create a minimal error handler
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Initialization failed: {str(e)}'})
        }

