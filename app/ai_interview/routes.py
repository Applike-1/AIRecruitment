from . import ai_interview_bp
from flask import request, jsonify
from app.utils.logger import logger
from app.utils.auth import require_api_key
from api.schemas import (
    InterviewStartRequest, InterviewStartResponse,
    InterviewEvaluateRequest, InterviewEvaluateResponse,
    InterviewEndRequest, InterviewEndResponse
)
from app.agents.interview_agent import InterviewAgent
from pydantic import ValidationError

# 初始化面试Agent
interview_agent = InterviewAgent()

# 存储面试会话
interview_sessions = {}

# 面试配置
MAX_QUESTIONS = 10  # 最大问题数

@ai_interview_bp.route('/start', methods=['POST'])
@require_api_key('ai_interview')
def start_interview():
    try:
        data = request.json
        req = InterviewStartRequest(**data)
        logger.info(f'Starting interview for position: {req.job_position}')

        # 调用InterviewAgent开始面试
        result = interview_agent.start_interview(req.job_position, req.user_id)
        
        # 存储面试会话
        interview_sessions[result['interview_id']] = {
            'position': req.job_position,
            'user_id': req.user_id,
            'questions': [],
            'answers': [],
            'scores': [],
            'current_question_index': 0,
            'start_time': None
        }

        # 构建响应
        response = InterviewStartResponse(
            interview_id=result['interview_id'],
            first_question=result['first_question'],
            estimated_duration=result['estimated_duration'],
            total_questions=MAX_QUESTIONS,
            current_question=1
        )
        return jsonify(response.model_dump()), 200
    except ValidationError as e:
        logger.warning(f'Validation error: {str(e)}')
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 422
    except Exception as e:
        logger.error(f'Error starting interview: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@ai_interview_bp.route('/evaluate', methods=['POST'])
@require_api_key('ai_interview')
def evaluate_answer():
    try:
        data = request.json
        req = InterviewEvaluateRequest(**data)
        logger.info(f'Evaluating answer for interview: {req.interview_id}')

        # 检查面试会话是否存在
        if req.interview_id not in interview_sessions:
            return jsonify({'error': 'Interview session not found'}), 404

        session = interview_sessions[req.interview_id]
        current_index = session['current_question_index']
        
        # 检查是否已经回答了所有问题
        if current_index >= MAX_QUESTIONS:
            return jsonify({'error': 'Interview has ended'}), 400

        # 调用InterviewAgent评估回答
        result = interview_agent.evaluate_answer(
            req.interview_id,
            req.question,
            req.answer,
            session['position'],
            current_index + 1,  # 第几个问题（从1开始）
            MAX_QUESTIONS,
            session['questions']  # 历史问题
        )

        # 存储问答记录
        session['questions'].append(req.question)
        session['answers'].append(req.answer)
        session['scores'].append(result['score'])
        session['current_question_index'] = current_index + 1

        # 判断是否继续面试
        is_continue = session['current_question_index'] < MAX_QUESTIONS
        
        # 构建响应
        response = InterviewEvaluateResponse(
            score=result['score'],
            feedback=result['feedback'],
            next_question=result['next_question'] if is_continue else None,
            is_continue=is_continue,
            current_question=current_index + 2 if is_continue else MAX_QUESTIONS + 1,
            total_questions=MAX_QUESTIONS
        )
        return jsonify(response.model_dump()), 200
    except ValidationError as e:
        logger.warning(f'Validation error: {str(e)}')
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 422
    except Exception as e:
        logger.error(f'Error evaluating answer: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@ai_interview_bp.route('/end', methods=['POST'])
@require_api_key('ai_interview')
def end_interview():
    try:
        data = request.json
        req = InterviewEndRequest(**data)
        logger.info(f'Ending interview: {req.interview_id}')

        # 检查面试会话是否存在
        if req.interview_id not in interview_sessions:
            return jsonify({'error': 'Interview session not found'}), 404

        # 获取问答记录
        session = interview_sessions[req.interview_id]
        answers = [
            {
                'question': session['questions'][i],
                'answer': session['answers'][i],
                'score': session['scores'][i] if i < len(session['scores']) else 0
            }
            for i in range(len(session['questions']))
        ]

        # 调用InterviewAgent结束面试
        result = interview_agent.end_interview(req.interview_id, session['position'], answers)

        # 删除面试会话
        del interview_sessions[req.interview_id]

        # 构建响应
        response = InterviewEndResponse(
            interview_id=req.interview_id,
            final_score=result['final_score'],
            summary=result['summary'],
            recommendation=result['recommendation'],
            grade=result.get('grade', '未评级')
        )
        return jsonify(response.model_dump()), 200
    except ValidationError as e:
        logger.warning(f'Validation error: {str(e)}')
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 422
    except Exception as e:
        logger.error(f'Error ending interview: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@ai_interview_bp.route('/status/<interview_id>', methods=['GET'])
@require_api_key('ai_interview')
def get_interview_status(interview_id):
    """获取面试状态"""
    try:
        if interview_id not in interview_sessions:
            return jsonify({'error': 'Interview session not found'}), 404
        
        session = interview_sessions[interview_id]
        return jsonify({
            'interview_id': interview_id,
            'position': session['position'],
            'current_question': session['current_question_index'] + 1,
            'total_questions': MAX_QUESTIONS,
            'is_complete': session['current_question_index'] >= MAX_QUESTIONS
        }), 200
    except Exception as e:
        logger.error(f'Error getting interview status: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500