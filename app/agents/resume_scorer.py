import re
import os
import requests
import json
from typing import Dict, List, Any

class ResumeScorer:
    def extract_info(self, resume_text: str) -> Dict[str, Any]:
        """
        从简历文本中提取信息
        """
        info = {
            'skills': [],
            'experience_years': 0,
            'education': '',
            'format_completeness': 0,
            'education_score': 0,
            'communication_score': 0,
            'project_score': 0
        }
        
        # 提取技能（简单关键词匹配）
        common_skills = ['Python', 'Flask', 'Django', 'JavaScript', 'React', 'Vue', 'HTML', 'CSS', 'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Git', 'Docker', 'AWS', 'Azure', 'Linux', 'Java', 'C++', 'C#', 'PHP', 'Ruby']
        for skill in common_skills:
            if re.search(rf'\b{skill}\b', resume_text, re.IGNORECASE):
                info['skills'].append(skill)
        
        # 提取工作经验年数
        experience_match = re.search(r'(\d+)\s*年.*经验', resume_text, re.IGNORECASE)
        if experience_match:
            info['experience_years'] = int(experience_match.group(1))
        
        # 提取教育背景
        education_match = re.search(r'(本科|硕士|博士|大专)', resume_text, re.IGNORECASE)
        if education_match:
            info['education'] = education_match.group(1)
        
        # 评估格式完整度（简单规则）
        sections = ['个人信息', '教育背景', '工作经历', '项目经验', '技能', '自我评价']
        for section in sections:
            if section in resume_text:
                info['format_completeness'] += 1
        info['format_completeness'] = min(100, (info['format_completeness'] / len(sections)) * 100)
        
        # 评估学历得分
        education_levels = {'博士': 100, '硕士': 85, '本科': 70, '大专': 50}
        info['education_score'] = education_levels.get(info['education'], 50)
        
        # 评估沟通能力（基于简历中的描述）
        communication_keywords = ['沟通', '协调', '团队合作', '协作', '交流', '演讲', '汇报']
        communication_count = sum(1 for keyword in communication_keywords if keyword in resume_text)
        info['communication_score'] = min(100, 50 + communication_count * 10)
        
        # 评估项目经验（基于项目数量和描述）
        project_keywords = ['项目', '负责', '开发', '实现', '设计', '优化']
        project_count = sum(1 for keyword in project_keywords if keyword in resume_text)
        info['project_score'] = min(100, 50 + project_count * 5)
        
        return info
    
    def score(self, resume_info: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据岗位要求对简历进行评分
        """
        # 技能匹配得分（40%）
        required_skills = job_requirements.get('required_skills', [])
        matched_skills = [skill for skill in resume_info['skills'] if skill in required_skills]
        skill_score = (len(matched_skills) / len(required_skills)) * 40 if required_skills else 40
        
        # 工作年限得分（30%）
        min_years = job_requirements.get('min_years', 0)
        experience_score = min(30, (resume_info['experience_years'] / min_years) * 30) if min_years > 0 else 30
        
        # 学历得分（20%）
        education_levels = {'博士': 20, '硕士': 15, '本科': 10, '大专': 5}
        education_score = education_levels.get(resume_info['education'], 0)
        
        # 格式完整度得分（10%）
        format_score = resume_info['format_completeness'] * 0.1
        
        # 总分
        total_score = skill_score + experience_score + education_score + format_score
        
        return {
            'total_score': min(100, total_score),
            'skill_score': skill_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'format_score': format_score,
            'matched_skills': matched_skills
        }
    
    def analyze_with_llm(self, resume_text: str, job_desc: str) -> Dict[str, Any]:
        """
        使用LLM分析简历与岗位匹配度
        """
        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            api_key = 'test_key'  # 测试用，实际使用时需要设置环境变量
        
        # DeepSeek API端点
        url = 'https://api.deepseek.com/v1/chat/completions'
        
        # 请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # 构造提示
        prompt = f"""
        请分析以下简历是否符合岗位要求。
        岗位描述：{job_desc}
        简历：{resume_text}
        
        请以JSON格式输出以下内容：
        {{
            "matched_skills": ["技能1", "技能2"],
            "experience_years": 3,
            "total_score": 85,
            "comments": "简短评语"
        }}
        """
        
        # 请求体
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 500
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                # 提取JSON部分
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    llm_result = json.loads(content[json_start:json_end])
                    return llm_result
                else:
                    # 返回默认结果
                    return {
                        'matched_skills': [],
                        'experience_years': 0,
                        'total_score': 0,
                        'comments': '无法解析LLM响应'
                    }
            else:
                # 返回默认结果
                return {
                    'matched_skills': [],
                    'experience_years': 0,
                    'total_score': 0,
                    'comments': f'LLM API调用失败: {response.status_code}'
                }
        except Exception as e:
            # 返回默认结果
            return {
                'matched_skills': [],
                'experience_years': 0,
                'total_score': 0,
                'comments': f'LLM API调用异常: {str(e)}'
            }
    
    def combined_score(self, resume_text: str, job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        结合规则评分和LLM评分，得到最终得分
        """
        # 规则评分
        resume_info = self.extract_info(resume_text)
        rule_score = self.score(resume_info, job_requirements)
        
        # LLM评分
        job_desc = job_requirements.get('job_description', '')
        llm_score = self.analyze_with_llm(resume_text, job_desc)
        
        # 加权结合
        weight_rule = 0.6  # 规则评分权重
        weight_llm = 0.4  # LLM评分权重
        final_score = rule_score['total_score'] * weight_rule + llm_score['total_score'] * weight_llm
        
        return {
            'final_score': min(100, final_score),
            'rule_score': rule_score,
            'llm_score': llm_score,
            'resume_info': resume_info
        }
    
    def generate_ability_chart(self, resume_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成能力图数据
        """
        # 计算各项能力得分
        education_score = resume_info['education_score']
        experience_score = min(100, resume_info['experience_years'] * 10 + 50)
        skill_score = min(100, len(resume_info['skills']) * 5 + 50)
        professional_score = min(100, resume_info['education_score'] * 0.7 + skill_score * 0.3)
        communication_score = resume_info['communication_score']
        project_score = resume_info['project_score']
        
        return {
            'labels': ['学历', '工龄', '技术', '专业', '沟通', '项目经验'],
            'datasets': [{
                'label': '能力评分',
                'data': [
                    education_score,
                    experience_score,
                    skill_score,
                    professional_score,
                    communication_score,
                    project_score
                ],
                'backgroundColor': 'rgba(0, 123, 255, 0.2)',
                'borderColor': 'rgba(0, 123, 255, 1)',
                'borderWidth': 2
            }]
        }