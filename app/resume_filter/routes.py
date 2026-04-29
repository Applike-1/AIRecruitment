from . import resume_filter_bp
from flask import request, jsonify
from app.utils.logger import logger
from app.utils.auth import require_api_key
from api.schemas import ResumeAnalyzeRequest, ResumeAnalyzeResponse
from app.agents.resume_scorer import ResumeScorer
from pydantic import ValidationError
import PyPDF2
import io

# 尝试导入docx，如果失败则提供降级方案
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning('python-docx不可用，Word文件处理功能受限')

# 初始化简历评分器
scorer = ResumeScorer()

def extract_text_from_file(file):
    """
    从上传的文件中提取文本
    """
    filename = file.filename.lower()
    text = ""
    
    if filename.endswith('.pdf'):
        # 处理PDF文件
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() or ""
        except Exception as e:
            logger.error(f'处理PDF文件错误: {str(e)}')
            return None
    elif filename.endswith('.docx'):
        # 处理Word文件
        if not DOCX_AVAILABLE:
            logger.warning('python-docx不可用，无法处理Word文件')
            return None
        try:
            doc = Document(io.BytesIO(file.read()))
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f'处理Word文件错误: {str(e)}')
            return None
    else:
        # 处理文本文件
        try:
            text = file.read().decode('utf-8')
        except Exception as e:
            logger.error(f'处理文本文件错误: {str(e)}')
            return None
    
    return text

@resume_filter_bp.route('/analyze', methods=['POST'])
@require_api_key('resume_filter')
def analyze_resume():
    try:
        data = request.json
        req = ResumeAnalyzeRequest(**data)
        logger.info('Received resume for analysis')

        # 提取岗位要求
        job_requirements = {
            'required_skills': ['Python', 'Flask', 'Django', 'MySQL', 'Git'],
            'min_years': 2,
            'job_description': req.job_description
        }

        # 调用评分器进行评分
        combined_result = scorer.combined_score(req.resume_text, job_requirements)
        logger.info(f'评分结果: {combined_result}')

        # 构建响应
        response = ResumeAnalyzeResponse(
            score=int(combined_result['final_score']),
            skills_match=combined_result['rule_score']['skill_score'] / 40,
            experience_match=combined_result['rule_score']['experience_score'] / 30,
            education_match=combined_result['rule_score']['education_score'] / 20,
            overall_comment=combined_result['llm_score'].get('comments', '规则评分: 技能匹配度高，工作经验符合要求'),
            recommendation='推荐' if combined_result['final_score'] >= 70 else '不推荐'
        )
        return jsonify(response.model_dump()), 200
    except ValidationError as e:
        logger.warning(f'Validation error: {str(e)}')
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 422
    except Exception as e:
        logger.error(f'Error analyzing resume: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

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

@resume_filter_bp.route('/upload', methods=['POST'])
@require_api_key('resume_filter')
def upload_resume():
    try:
        logger.info('收到简历文件上传请求')
        
        # 检查是否有文件上传
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        # 检查是否有岗位描述
        job_description = request.form.get('job_description')
        if not job_description:
            return jsonify({'error': 'Missing job_description parameter'}), 400
        
        # 提取文件文本
        resume_file = request.files['resume']
        resume_text = extract_text_from_file(resume_file)
        
        if not resume_text:
            return jsonify({'error': 'Failed to extract text from resume file'}), 400
        
        # 提取岗位要求（简单处理，实际应用中可能需要更复杂的解析）
        job_requirements = {
            'required_skills': ['Python', 'Flask', 'Django', 'MySQL', 'Git'],  # 示例技能
            'min_years': 2,  # 示例工作年限要求
            'job_description': job_description
        }
        
        # 调用评分器进行评分
        combined_result = scorer.combined_score(resume_text, job_requirements)
        logger.info(f'评分结果: {combined_result}')
        
        # 生成简历总结
        summary = f"简历总结：候选人具备{len(combined_result['rule_score']['matched_skills'])}项匹配技能，工作经验{combined_result['resume_info']['experience_years']}年，学历为{combined_result['resume_info']['education'] or '未知'}。"
        
        # 生成能力图数据
        ability_data = scorer.generate_ability_chart(combined_result['resume_info'])
        
        # 构建响应，包含能力图数据和简历总结
        response = {
            'score': combined_result['final_score'],
            'matched_skills': combined_result['rule_score']['matched_skills'],
            'feedback': combined_result['llm_score'].get('comments', '规则评分: 技能匹配度高，工作经验符合要求'),
            'summary': summary,
            'ability_data': ability_data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f'简历上传API错误: {str(e)}')
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500