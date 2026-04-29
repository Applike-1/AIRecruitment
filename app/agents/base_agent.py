import os
import time
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from app.utils.logger import logger
from app.utils.mcp_client import mcp_client

load_dotenv()

class BaseAgent:
    def __init__(
        self,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.llm = self._create_llm()

    def _create_llm(self) -> ChatOpenAI:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')

        if not api_key:
            logger.warning('DEEPSEEK_API_KEY not found in environment')

        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=api_key,
            base_url=base_url,
            timeout=30
        )

    def _call_llm(self, prompt: str, system_message: Optional[str] = None) -> str:
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = self.llm.invoke(messages)
                elapsed_time = time.time() - start_time

                if hasattr(response, 'usage') and response.usage:
                    token_count = response.usage.total_tokens
                    logger.info(f'LLM调用成功，耗时{elapsed_time:.2f}秒，消耗Token: {token_count}')
                else:
                    logger.info(f'LLM调用成功，耗时{elapsed_time:.2f}秒')

                return response.content

            except Exception as e:
                logger.error(f'LLM调用失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}')
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1 * (attempt + 1))

    def chat(self, user_message: str, system_message: Optional[str] = None) -> str:
        return self._call_llm(user_message, system_message)

    def get_config(self, module: str) -> Dict[str, Any]:
        return mcp_client.fetch_config(module)

if __name__ == '__main__':
    agent = BaseAgent()
    print('测试BaseAgent...')
    print('模型配置:', agent.model)
    print('温度:', agent.temperature)
    print('最大Token:', agent.max_tokens)