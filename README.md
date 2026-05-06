# AI招聘系统

基于AI Agent智能体的简历筛选、AI面试官和简历问答系统。

## 功能特性

### 系统界面预览

![招聘问答与简历筛选](https://raw.githubusercontent.com/Applike-1/AIRecruitment/main/screenshots/screenshot1.png)

![模拟面试](https://raw.githubusercontent.com/Applike-1/AIRecruitment/main/screenshots/screenshot2.png)

### 🤖 AI招聘咨询
- 基于RAG（检索增强生成）的智能问答系统
- 支持招聘政策、常见问题、面试流程等知识库查询
- 自动检索相关文档并生成准确回答

### 📄 AI简历筛选
- 支持PDF、Word、TXT等多种简历格式上传
- 六边形能力图可视化展示（学历、工龄、技术、专业、项目经验、沟通能力）
- 基于规则和大模型的综合评分体系

### 🎯 AI模拟面试
- 10道完整面试题目流程
- 根据用户回答动态生成下一个问题
- 实时评分和反馈（60分及格，80分优秀）
- 面试结束后生成详细总结报告

## 技术栈

- **后端框架**: Flask 2.0+
- **AI技术**: LangChain、RAG、DeepSeek API
- **向量数据库**: Chroma
- **前端**: HTML5、CSS3、JavaScript、Chart.js
- **文件处理**: PyPDF2、python-docx
- **认证**: API Key验证

## 项目结构

```
AIzhaoping/
├── app.py                    # 主应用入口
├── index.html                # 前端界面
├── requirements.txt          # 依赖配置
├── .env.example              # 环境变量示例
├── api/                     # API定义
│   ├── resume_filter.py      # 简历筛选API
│   └── schemas.py           # 数据模型
├── app/                     # 核心模块
│   ├── agents/              # AI代理模块
│   │   ├── base_agent.py    # 基础代理类
│   │   ├── recruit_qa_agent.py   # 招聘问答代理
│   │   ├── resume_scorer.py      # 简历评分代理
│   │   └── interview_agent.py    # 面试代理
│   ├── ai_interview/        # 模拟面试API
│   ├── recruit_qa/          # 招聘问答API
│   ├── resume_filter/       # 简历筛选API
│   ├── knowledge_base/      # 知识库
│   │   ├── documents/       # 文档文件
│   │   └── build_vector_store.py # 向量存储构建
│   └── utils/               # 工具函数
│       ├── auth.py          # 认证工具
│       ├── logger.py        # 日志工具
│       └── mcp_client.py    # MCP客户端
├── resumes/                 # 简历示例文件
└── tests/                   # 测试目录
```

## 快速开始

### 环境要求

- Python 3.10+
- DeepSeek API Key（需自行申请）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的DeepSeek API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
FLASK_APP=app.py
FLASK_ENV=development
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 启动应用

```bash
python app.py
```

访问 http://localhost:5000 查看应用。

## API接口

### 招聘问答

**POST** `/qa/ask`

请求体：
```json
{
  "question": "如何投递简历？"
}
```

响应：
```json
{
  "answer": "回答内容...",
  "sources": ["文档1", "文档2"]
}
```

### 简历筛选

**POST** `/resume/upload`

支持文件上传（PDF/Word/TXT）

请求体：
```json
{
  "job_description": "岗位描述..."
}
```

响应：
```json
{
  "score": 85,
  "matched_skills": ["Python", "Flask"],
  "feedback": "评价内容...",
  "summary": "简历总结...",
  "ability_data": [...]
}
```

### 模拟面试

**POST** `/interview/start` - 开始面试

请求体：
```json
{
  "position": "Python开发工程师"
}
```

**POST** `/interview/evaluate` - 提交回答并获取下一题

**POST** `/interview/end` - 结束面试并获取总结

## 面试评分标准

| 分数 | 评级 | 说明 |
|------|------|------|
| 80-100 | 优秀 | 表现出色，建议录用 |
| 70-79 | 良好 | 表现良好，可以考虑 |
| 60-69 | 及格 | 基本达标，需进一步评估 |
| <60 | 不及格 | 未达到要求 |

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

**注意**: 本项目使用DeepSeek API进行AI推理，请确保已申请并配置有效的API Key。
