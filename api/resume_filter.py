from flask import Blueprint, request, jsonify
from app.agents.resume_scorer import ResumeScorer
from app.utils.auth import require_api_key
from app.utils.logger import logger

resume_filter_bp = Blueprint('resume_filter', __name__)

# 初始化简历评分器
scorer = ResumeScorer()

@resume_filter_bp.route('/score', methods=['POST'])
@require_api_key('resume_filter')
def score_resume():
    try:
        logger.info('收到简历评分请求')
        data = request.json
        logger.info(f'请求数据: {data}')
        
        # 验证请求数据
        if not data or 'resume_text' not in data or 'job_description' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        resume_text = data['resume_text']
        job_description = data['job_description']
        
        # 提取岗位要求（简单处理，实际应用中可能需要更复杂的解析）
        job_requirements = {
            'required_skills': ['Python', 'Flask', 'Django', 'MySQL', 'Git'],  # 示例技能
            'min_years': 2,  # 示例工作年限要求
            'job_description': job_description
        }
        
        # 调用评分器进行评分
        combined_result = scorer.combined_score(resume_text, job_requirements)
        logger.info(f'评分结果: {combined_result}')
        
        # 构建响应
        response = {
            'score': combined_result['final_score'],
            'matched_skills': combined_result['rule_score']['matched_skills'],
            'feedback': combined_result['llm_score'].get('comments', '规则评分: 技能匹配度高，工作经验符合要求')
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f'简历评分API错误: {str(e)}')
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500