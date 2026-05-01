import os
import requests
import json
import sys

# 设置编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'
API_KEY = os.getenv('TEST_API_KEY', 'your_api_key_here')

def test_resume_scoring():
    """测试简历评分功能"""
    print("测试简历评分功能...")
    
    # 测试数据
    resume_text = """
    个人信息
    姓名：张三
    电话：13800138000
    邮箱：zhangsan@example.com
    
    教育背景
    本科，计算机科学与技术，2018年毕业于清华大学
    
    工作经历
    5年Python开发经验，熟悉Flask和Django框架。
    在ABC公司担任后端开发工程师，负责公司核心业务系统开发。
    在DEF公司担任高级开发工程师，带领团队完成多个项目。
    
    项目经验
    负责电商平台后端系统开发，使用Python、Flask、MySQL技术栈。
    设计并实现微服务架构，提升系统性能和可扩展性。
    优化数据库查询，将响应时间减少50%。
    
    技能
    熟练掌握Python、Flask、Django、MySQL、Git等技术。
    具备良好的沟通协调能力，能够与团队成员有效合作。
    
    自我评价
    具备丰富的项目经验，善于解决技术难题，注重代码质量和团队协作。
    """
    
    job_description = "负责公司后端系统开发，使用Python技术栈，需要具备Flask和Django框架经验，至少2年工作经验。"
    
    # 调用API
    url = f'{API_BASE_URL}/resume/score'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    data = {
        'resume_text': resume_text,
        'job_description': job_description
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f'状态码: {response.status_code}')
    result = response.json()
    print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
    
    # 验证结果
    if 'score' in result:
        print(f'[OK] 简历评分功能正常，评分: {result["score"]}')
    else:
        print('[FAIL] 简历评分功能异常')

def test_interview_agent():
    """测试面试Agent功能"""
    print("\n测试面试Agent功能...")
    
    # 开始面试
    url = f'{API_BASE_URL}/interview/start'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    data = {
        'job_position': '后端开发工程师',
        'user_id': 'test_user_001'
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f'开始面试 - 状态码: {response.status_code}')
    result = response.json()
    print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
    
    if 'interview_id' in result:
        interview_id = result['interview_id']
        print(f'[OK] 开始面试功能正常，面试ID: {interview_id}')
        
        # 评估回答
        url = f'{API_BASE_URL}/interview/evaluate'
        data = {
            'interview_id': interview_id,
            'question': result['first_question'],
            'answer': '我有5年Python开发经验，熟悉Flask和Django框架，曾负责多个大型项目的开发。'
        }
        
        response = requests.post(url, headers=headers, json=data)
        print(f'评估回答 - 状态码: {response.status_code}')
        result = response.json()
        print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
        
        if 'score' in result:
            print(f'[OK] 评估回答功能正常，评分: {result["score"]}')
        else:
            print('[FAIL] 评估回答功能异常')
        
        # 结束面试
        url = f'{API_BASE_URL}/interview/end'
        data = {
            'interview_id': interview_id
        }
        
        response = requests.post(url, headers=headers, json=data)
        print(f'结束面试 - 状态码: {response.status_code}')
        result = response.json()
        print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
        
        if 'final_score' in result:
            print(f'[OK] 结束面试功能正常，最终评分: {result["final_score"]}')
        else:
            print('[FAIL] 结束面试功能异常')
    else:
        print('[FAIL] 开始面试功能异常')

def test_qa_agent():
    """测试问答Agent功能"""
    print("\n测试问答Agent功能...")
    
    url = f'{API_BASE_URL}/qa/ask'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    data = {
        'question': '如何投递简历？'
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f'状态码: {response.status_code}')
    result = response.json()
    print(f'响应: {json.dumps(result, ensure_ascii=False, indent=2)}')
    
    if 'answer' in result:
        print('[OK] 问答Agent功能正常')
    else:
        print('[FAIL] 问答Agent功能异常')

if __name__ == '__main__':
    print("=" * 50)
    print("测试真实实现功能")
    print("=" * 50)
    
    try:
        test_resume_scoring()
        test_interview_agent()
        test_qa_agent()
        
        print("\n" + "=" * 50)
        print("所有测试完成")
        print("=" * 50)
    except Exception as e:
        print(f'测试失败: {str(e)}')