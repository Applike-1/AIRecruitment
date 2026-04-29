from flask import request, jsonify
from app.utils.logger import logger
from app.utils.auth import require_api_key
from api.schemas import QAAskRequest, QAAskResponse
from app.agents.recruit_qa_agent import RecruitQAAgent
from pydantic import ValidationError
from . import recruit_qa_bp

# 初始化招聘问答Agent
logger.info('正在初始化RecruitQAAgent...')
try:
    qa_agent = RecruitQAAgent()
    logger.info('RecruitQAAgent初始化成功')
except Exception as e:
    logger.error(f'RecruitQAAgent初始化失败: {str(e)}')
    qa_agent = None

@recruit_qa_bp.route('/ask', methods=['POST'])
@require_api_key('recruit_qa')
def ask_question():
    try:
        logger.info('收到招聘问答请求')
        data = request.json
        logger.info(f'请求数据: {data}')
        
        req = QAAskRequest(**data)
        logger.info(f'Received question: {req.question}')

        # 调用RecruitQAAgent生成回答
        if qa_agent:
            logger.info('调用RecruitQAAgent生成回答...')
            result = qa_agent.answer(req.question)
            logger.info(f'Agent返回结果: {result}')
        else:
            logger.error('RecruitQAAgent未初始化')
            return jsonify({'error': 'RecruitQAAgent not initialized'}), 500
        
        # 构建响应
        response = QAAskResponse(
            answer=result['answer'],
            sources=result['sources'],
            confidence=0.85  # 假设固定置信度
        )
        
        logger.info(f'Generated answer: {result["answer"]}')
        return jsonify(response.model_dump()), 200
        
    except ValidationError as e:
        logger.warning(f'Validation error: {str(e)}')
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 422
    except Exception as e:
        logger.error(f'Error processing question: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500