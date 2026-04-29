import logging
from logging.handlers import TimedRotatingFileHandler
import os
import threading

logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

class MCPLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.mcp_client = None
        self._init_mcp_client()

    def _init_mcp_client(self):
        try:
            from app.utils.mcp_client import mcp_client
            self.mcp_client = mcp_client
        except Exception:
            pass

    def emit(self, record):
        if self.mcp_client is None:
            return
        try:
            msg = self.format(record)
            module = getattr(record, 'module', 'unknown')
            self.mcp_client.report_log(
                level=record.levelname,
                message=msg,
                module=module
            )
        except Exception:
            pass

logger = logging.getLogger('ai_recruitment')
logger.setLevel(logging.DEBUG)

file_handler = TimedRotatingFileHandler(
    os.path.join(logs_dir, 'app.log'),
    when='D',
    interval=1,
    backupCount=7
)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

mcp_handler = MCPLogHandler()
mcp_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
mcp_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.addHandler(mcp_handler)

if __name__ == '__main__':
    logger.debug('调试信息')
    logger.info('普通信息')
    logger.warning('警告信息')
    logger.error('错误信息')
    logger.critical('严重错误')