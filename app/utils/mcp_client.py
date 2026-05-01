import os
import requests
import time
from typing import Optional, Dict, Any
from app.utils.logger import logger

MCP_PLATFORM_URL = 'https://mcp.platform.internal'
MCP_APP_ID = 'ai_recruitment_system'
MCP_APP_SECRET = os.getenv('MCP_APP_SECRET', 'your_app_secret_here')

class MCPClient:
    def __init__(self, platform_url: str = None, app_id: str = None, app_secret: str = None):
        self.platform_url = platform_url or MCP_PLATFORM_URL
        self.app_id = app_id or MCP_APP_ID
        self.app_secret = app_secret or MCP_APP_SECRET
        self.token = None
        self.token_expires_at = 0

    def _get_token(self) -> str:
        if not self.token or time.time() > self.token_expires_at:
            self.token = f'mock_token_{int(time.time())}'
            self.token_expires_at = time.time() + 3600
        return self.token

    def verify_permission(self, api_key: str, module: str) -> Dict[str, Any]:
        logger.info(f'验证权限: API Key={api_key}, 模块={module}')
        if api_key == 'test_key_123' or api_key == 'dev_key_456':
            return {
                'success': True,
                'permissions': ['qa:ask', 'resume:analyze', 'interview:start', 'interview:evaluate', 'interview:end']
            }
        return {'success': False, 'error': 'Invalid API Key'}

    def report_log(self, level: str, message: str, module: str, extra: Dict = None) -> bool:
        log_entry = {
            'level': level,
            'message': message,
            'module': module,
            'app_id': self.app_id,
            'timestamp': int(time.time()),
            'extra': extra or {}
        }
        try:
            response = requests.post(
                f'{self.platform_url}/api/logs',
                json=log_entry,
                headers={'Authorization': f'Bearer {self._get_token()}'},
                timeout=3
            )
            logger.debug(f'日志上报结果: {response.status_code}')
            return True
        except requests.exceptions.RequestException:
            logger.debug(f'MCP平台日志上报失败（模拟）: {log_entry}')
            return False

    def fetch_config(self, module: str) -> Dict[str, Any]:
        logger.info(f'获取配置: 模块={module}')
        mock_configs = {
            'recruit_qa': {
                'enabled': True,
                'model': 'deepseek-chat',
                'temperature': 0.7,
                'max_tokens': 2000,
                'retrieval_top_k': 5
            },
            'resume_filter': {
                'enabled': True,
                'model': 'deepseek-chat',
                'temperature': 0.5,
                'max_tokens': 1000,
                'score_threshold': 60
            },
            'ai_interview': {
                'enabled': True,
                'model': 'deepseek-chat',
                'temperature': 0.8,
                'max_tokens': 500,
                'question_count': 5,
                'passing_score': 70
            }
        }
        return mock_configs.get(module, {})

mcp_client = MCPClient()

if __name__ == '__main__':
    print('测试MCP客户端...')
    print('权限验证:', mcp_client.verify_permission('test_key_123', 'recruit_qa'))
    print('日志上报:', mcp_client.report_log('INFO', '测试日志', 'test_module'))
    print('配置拉取:', mcp_client.fetch_config('recruit_qa'))