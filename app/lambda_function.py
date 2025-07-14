import json
from services.validator import validate_level

def lambda_handler(event, context):
    """AWS Lambda handler for level validation"""
    try:
        # Handle different event sources (API Gateway, direct invocation, etc.)
        if isinstance(event.get('body'), str):
            # API Gateway sends body as string
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            # Direct invocation might have dict
            body = event['body']
        else:
            # Direct invocation with level data at root
            body = event
        
        # Validate level
        result = validate_level(body)
        
        # Determine status code
        if 'error' in result:
            if result['error']['code'] == 'INVALID_REQUEST':
                status_code = 400
            elif result['error']['code'] in ['VALIDATION_ERROR', 'INVALID_LEVEL_DATA']:
                status_code = 422
            else:
                status_code = 500
        else:
            status_code = 200
        
        # Return response in API Gateway format
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body is not valid JSON'
                }
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': f'An unexpected error occurred: {str(e)}'
                }
            })
        }