import os
from typing import Dict, List, Optional, Any
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base_agent import BaseAgent
from app.knowledge_base.build_vector_store import SimpleEmbeddings
from app.utils.logger import logger

class RecruitQAAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.vector_store = None
        self.use_vector_store = False
        try:
            self.vector_store = self._load_vector_store()
            self.use_vector_store = True
            logger.info('RecruitQAAgent初始化成功，使用向量存储')
        except Exception as e:
            logger.warning(f'向量存储加载失败，使用降级模式: {str(e)}')
            self.use_vector_store = False

    def _load_vector_store(self):
        vector_store_dir = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base', 'vector_store')
        embeddings = SimpleEmbeddings()
        return Chroma(
            persist_directory=vector_store_dir,
            embedding_function=embeddings
        )

    def answer(self, question: str) -> Dict[str, Any]:
        try:
            if self.use_vector_store and self.vector_store:
                # 使用向量存储检索相关文档
                documents = self.vector_store.similarity_search(question, k=3)
                context = "\n".join([doc.page_content for doc in documents])
                sources = [doc.metadata.get('filename', '') for doc in documents]
            else:
                # 使用降级模式：简单关键词匹配
                context, sources = self._fallback_search(question)
            
            # 构建提示模板
            template = """
            你是一个招聘助手。根据以下上下文回答候选人的问题。如果不知道就说不知道。
            上下文：{context}
            问题：{question}
            回答：
            """
            
            # 生成回答
            prompt = template.format(context=context, question=question)
            answer = self.chat(prompt)
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            logger.error(f'回答问题失败: {str(e)}')
            return {
                "answer": "抱歉，我现在无法回答您的问题。请稍后再试。",
                "sources": []
            }
    
    def _fallback_search(self, question: str) -> tuple:
        """
        降级搜索：使用简单的关键词匹配
        """
        # 定义知识库内容
        knowledge_base = {
            'recruitment_policy.txt': '公司招聘政策：我们致力于吸引和培养优秀人才，提供有竞争力的薪酬福利和良好的职业发展空间。',
            'faq.txt': '常见问题：如何投递简历？请将简历发送至hr@company.com，邮件主题注明应聘职位。面试有几轮？通常有2-3轮面试，包括技术面试和HR面试。',
            'technical_requirements.txt': '技术岗位要求：后端开发工程师需要熟悉Python、Flask、Django等框架，具备良好的编程基础和问题解决能力。',
            'interview_process.txt': '面试流程：1. 简历筛选 2. 技术面试 3. 综合面试 4. HR面试 5. 发放offer',
            'benefits.txt': '薪资福利：我们提供具有竞争力的薪资、五险一金、带薪年假、节日福利、培训机会等。'
        }
        
        # 简单关键词匹配
        matched_docs = []
        matched_sources = []
        
        keywords = question.split()
        for filename, content in knowledge_base.items():
            for keyword in keywords:
                if keyword in content:
                    if filename not in matched_sources:
                        matched_docs.append(content)
                        matched_sources.append(filename)
                    break
        
        # 如果没有匹配到，返回默认内容
        if not matched_docs:
            matched_docs.append('抱歉，我没有找到相关的信息。您可以尝试其他问题或联系HR部门。')
            matched_sources.append('unknown')
        
        context = "\n".join(matched_docs)
        return context, matched_sources