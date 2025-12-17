import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response(
            {'error': 'Internal server error'},
            status=500
        )
    
    # Add request ID to response
    response.data['request_id'] = context['request'].META.get('HTTP_X_REQUEST_ID', '')
    return response