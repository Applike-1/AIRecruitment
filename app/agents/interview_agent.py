import os
import json
import random
from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.utils.logger import logger

class InterviewAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question_bank = self._load_question_bank()
    
    def _load_question_bank(self) -> Dict[str, List[str]]:
        """
        加载面试题库
        """
        return {
            'general': [
                '请介绍一下你自己',
                '你为什么选择我们公司？',
                '你未来3-5年的职业规划是什么？',
                '你最大的优点和缺点是什么？',
                '你期望的薪资范围是多少？',
                '你为什么离开上一家公司？',
                '你对我们公司了解多少？',
                '你有什么问题要问我吗？'
            ],
            'technical': [
                '请描述一个你解决过的技术难题',
                '你是如何保证代码质量的？',
                '你熟悉哪些设计模式？请举例说明',
                '你是如何处理性能优化问题的？',
                '你常用的开发工具和技术栈是什么？',
                '请解释什么是RESTful API？',
                '你如何处理数据库事务？',
                '请描述TCP/IP协议的工作原理',
                '什么是微服务架构？有什么优缺点？',
                '如何保证系统的高可用性？'
            ],
            'behavioral': [
                '请描述一个你与团队成员合作完成的项目',
                '你是如何处理工作中的压力和挑战的？',
                '请分享一个你从失败中学到的经验',
                '你是如何与不同性格的同事相处的？',
                '你如何处理与上级的意见分歧？',
                '请描述一次你主动承担额外工作的经历',
                '你如何平衡工作和生活？',
                '你是如何学习新技术的？'
            ]
        }
    
    def start_interview(self, job_position: str, user_id: str = None) -> Dict[str, Any]:
        """
        开始面试，生成第一个问题
        """
        try:
            # 构造提示
            prompt = f"""
            你是一个专业的面试官，正在面试{job_position}职位的候选人。
            请生成一个适合该职位的首个面试问题。
            问题应该简洁明了，能够帮助了解候选人的基本情况。
            
            请只返回问题本身，不要包含其他内容。
            """
            
            # 调用LLM生成问题
            first_question = self.chat(prompt)
            
            # 如果LLM调用失败，使用预设问题
            if not first_question or first_question.startswith('错误'):
                first_question = f'请介绍一下你为什么适合{job_position}这个职位？'
            
            # 生成面试ID
            interview_id = f'int_{hash(job_position + str(user_id or "")) % 1000000}'
            
            return {
                'interview_id': interview_id,
                'first_question': first_question,
                'estimated_duration': 30
            }
        except Exception as e:
            logger.error(f'开始面试失败: {str(e)}')
            # 返回默认问题
            return {
                'interview_id': f'int_{random.randint(100000, 999999)}',
                'first_question': f'请介绍一下你为什么适合{job_position}这个职位？',
                'estimated_duration': 30
            }
    
    def evaluate_answer(self, interview_id: str, question: str, answer: str, 
                        job_position: str, question_number: int, total_questions: int,
                        history_questions: List[str] = None) -> Dict[str, Any]:
        """
        评估候选人的回答，并生成下一个问题
        """
        try:
            history_questions = history_questions or []
            
            # 构造提示
            prompt = f"""
            你是一个专业的面试官，正在面试{job_position}职位的候选人。
            
            当前是第 {question_number}/{total_questions} 个问题。
            
            面试问题：{question}
            候选人回答：{answer}
            
            历史问题列表：{', '.join(history_questions) if history_questions else '无'}
            
            请对候选人的回答进行评估，并根据回答内容和岗位需求生成下一个问题。
            下一个问题应该与之前的问题不重复，且能够进一步了解候选人的能力。
            
            请以JSON格式返回以下内容：
            {{
                "score": 85,
                "feedback": "回答很全面，展示了相关经验",
                "next_question": "请描述一个你解决过的技术难题"
            }}
            
            其中：
            - score: 评分（0-100），根据回答的质量、相关性、深度进行评分
            - feedback: 对回答的具体反馈和建议
            - next_question: 下一个面试问题
            """
            
            # 调用LLM评估回答
            response = self.chat(prompt)
            
            # 尝试解析JSON响应
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    result = json.loads(response[json_start:json_end])
                    # 验证结果
                    if 'score' not in result:
                        result['score'] = 75
                    if 'feedback' not in result:
                        result['feedback'] = '回答较为完整'
                    if 'next_question' not in result:
                        result['next_question'] = self._get_next_question(job_position, history_questions)
                    return result
            except Exception as e:
                logger.warning(f'解析LLM响应失败: {str(e)}')
            
            # 如果解析失败，返回默认评估
            return self._get_default_evaluation(job_position, history_questions)
        except Exception as e:
            logger.error(f'评估回答失败: {str(e)}')
            return self._get_default_evaluation(job_position, history_questions)
    
    def _get_next_question(self, job_position: str, history_questions: List[str]) -> str:
        """
        根据岗位和历史问题生成下一个问题
        """
        # 合并所有题库
        all_questions = []
        for category in self.question_bank.values():
            all_questions.extend(category)
        
        # 过滤已问过的问题
        available_questions = [q for q in all_questions if q not in history_questions]
        
        if available_questions:
            return random.choice(available_questions)
        else:
            return f'你认为自己最适合{job_position}这个职位的原因是什么？'
    
    def _get_default_evaluation(self, job_position: str, history_questions: List[str]) -> Dict[str, Any]:
        """
        获取默认评估结果
        """
        return {
            'score': 75,
            'feedback': '回答较为完整，可以进一步深入了解',
            'next_question': self._get_next_question(job_position, history_questions)
        }
    
    def end_interview(self, interview_id: str, job_position: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        结束面试，生成最终评估
        """
        try:
            # 计算平均得分
            total_score = sum(a.get('score', 0) for a in answers)
            avg_score = total_score / len(answers) if answers else 0
            
            # 构建问答文本
            answers_text = '\n'.join([
                f"问题{i+1}: {a['question']}\n回答: {a['answer']}\n评分: {a.get('score', 0)}\n"
                for i, a in enumerate(answers)
            ])
            
            # 构造提示
            prompt = f"""
            你是一个专业的面试官，正在对候选人的面试表现进行最终评估。
            
            应聘职位：{job_position}
            面试问题数量：{len(answers)}
            
            面试问答记录：
            {answers_text}
            
            请对候选人的整体表现进行综合评估。
            
            评分标准：
            - 60分及以上为及格
            - 80分及以上为优秀
            
            请以JSON格式返回以下内容：
            {{
                "final_score": 85,
                "summary": "面试整体表现评价，包括候选人的优势和待改进之处",
                "recommendation": "建议录用",
                "grade": "优秀"
            }}
            
            其中：
            - final_score: 最终评分（0-100）
            - summary: 面试总结，至少200字，包括候选人的优势、不足和改进建议
            - recommendation: 录用建议（建议录用/不建议录用/需要进一步考虑）
            - grade: 评级（优秀/良好/及格/不及格）
            """
            
            # 调用LLM生成最终评估
            response = self.chat(prompt)
            
            # 尝试解析JSON响应
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    result = json.loads(response[json_start:json_end])
                    result['interview_id'] = interview_id
                    # 确保有评级
                    if 'grade' not in result:
                        result['grade'] = self._get_grade(result['final_score'])
                    return result
            except Exception as e:
                logger.warning(f'解析LLM响应失败: {str(e)}')
            
            # 如果解析失败，返回基于平均分的默认评估
            return self._get_default_final_evaluation(interview_id, avg_score)
        except Exception as e:
            logger.error(f'结束面试失败: {str(e)}')
            return self._get_default_final_evaluation(interview_id, 70)
    
    def _get_grade(self, score: float) -> str:
        """
        根据分数获取评级
        """
        if score >= 80:
            return '优秀'
        elif score >= 70:
            return '良好'
        elif score >= 60:
            return '及格'
        else:
            return '不及格'
    
    def _get_default_final_evaluation(self, interview_id: str, avg_score: float) -> Dict[str, Any]:
        """
        获取默认最终评估结果
        """
        grade = self._get_grade(avg_score)
        
        if avg_score >= 80:
            recommendation = '建议录用'
            summary = f'面试整体表现优秀！候选人平均得分{avg_score:.1f}分。候选人展现了扎实的专业能力和良好的沟通技巧，具备较强的学习能力和团队协作精神。建议优先考虑录用。'
        elif avg_score >= 60:
            recommendation = '需要进一步考虑'
            summary = f'面试整体表现合格。候选人平均得分{avg_score:.1f}分。候选人具备基本的专业技能，但在某些方面还有提升空间。建议与用人部门进一步沟通评估。'
        else:
            recommendation = '不建议录用'
            summary = f'面试表现未达到要求。候选人平均得分{avg_score:.1f}分。候选人在专业技能或沟通能力方面存在明显不足，建议不予录用。'
        
        return {
            'interview_id': interview_id,
            'final_score': round(avg_score, 1),
            'summary': summary,
            'recommendation': recommendation,
            'grade': grade
        }

if __name__ == '__main__':
    agent = InterviewAgent()
    print('测试InterviewAgent...')
    result = agent.start_interview('后端开发工程师')
    print(f'开始面试: {result}')