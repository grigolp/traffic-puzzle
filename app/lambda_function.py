import json
import time
from services.validator import validate_level

def lambda_handler(event, context):
    """AWS Lambda handler for level validation"""
    try:
        if event.get('httpMethod') == 'GET' and not event.get('body'):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Empty GET request processed successfully'})
            }

        # Handle different event sources (API Gateway, direct invocation, etc.)
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            body = event['body']
        else:
            body = event

        # Time the validation
        start_time = time.perf_counter()
        result = validate_level(body)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 3)  # milliseconds with precision

        # Include timing in response
        result['executionTimeMs'] = duration_ms

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
