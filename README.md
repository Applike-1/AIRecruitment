# AI招聘系统

企业级AI招聘系统的核心AI能力模块，包含招聘咨询、简历筛选和模拟面试功能。

## 项目结构

- `app/` - 主应用目录
  - `api/` - 路由接口
  - `agents/` - AI Agent逻辑
  - `knowledge_base/` - RAG知识库
  - `utils/` - 工具函数
  - `tests/` - 测试文件
  - `config/` - 配置文件
  - `logs/` - 日志文件
- `requirements.txt` - 依赖包
- `README.md` - 项目说明
- `.env` - 环境变量
- `app.py` - 主应用入口

## 功能模块

1. **AI招聘咨询**：智能解答招聘相关问题
2. **AI简历筛选**：自动分析简历，进行技能和岗位匹配
3. **AI模拟面试**：模拟面试提问并智能评估回答

## 技术栈

- 后端：Python、Flask
- AI技术：LangChain、RAG、DeepSeek API
- 平台：MCP平台
- 版本控制：GitHub