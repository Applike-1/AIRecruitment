from functools import wraps
from flask import request, jsonify
from app.utils.mcp_client import mcp_client

def require_api_key(module: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'Unauthorized: API Key is required'}), 401

            result = mcp_client.verify_permission(api_key, module)
            if not result.get('success'):
                return jsonify({'error': 'Unauthorized: Invalid API Key'}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator

if __name__ == '__main__':
    print('测试MCP权限验证...')
    print(mcp_client.verify_permission('test_key_123', 'recruit_qa'))