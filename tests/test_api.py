import os
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'
API_KEY = os.getenv('TEST_API_KEY', 'your_api_key_here')

def test_qa_ask():
    print('测试 /api/qa/ask...')
    url = f'{BASE_URL}/api/qa/ask'
    headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}
    data = {'question': '公司有哪些福利待遇？'}
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200, f'状态码错误: {response.status_code}'
    result = response.json()
    assert 'answer' in result, '响应缺少answer字段'
    assert 'sources' in result, '响应缺少sources字段'
    assert 'confidence' in result, '响应缺少confidence字段'
    print(f'  状态码: {response.status_code}')
    print(f'  响应: {json.dumps(result, ensure_ascii=False)}')
    print('  通过!')

def test_resume_analyze():
    print('测试 /api/resume/analyze...')
    url = f'{BASE_URL}/api/resume/analyze'
    headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}
    data = {
        'resume_content': '张三，5年Python开发经验，熟练使用Flask、Django等框架',
        'job_description': '招聘Python后端开发工程师，要求3年以上经验，精通Flask'
    }
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200, f'状态码错误: {response.status_code}'
    result = response.json()
    assert 'score' in result, '响应缺少score字段'
    assert 'skills_match' in result, '响应缺少skills_match字段'
    assert 'experience_match' in result, '响应缺少experience_match字段'
    assert 'education_match' in result, '响应缺少education_match字段'
    assert 'overall_comment' in result, '响应缺少overall_comment字段'
    assert 'recommendation' in result, '响应缺少recommendation字段'
    print(f'  状态码: {response.status_code}')
    print(f'  响应: {json.dumps(result, ensure_ascii=False)}')
    print('  通过!')

def test_interview_start():
    print('测试 /api/interview/start...')
    url = f'{BASE_URL}/api/interview/start'
    headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}
    data = {'job_position': 'Python开发工程师', 'candidate_name': '张三'}
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200, f'状态码错误: {response.status_code}'
    result = response.json()
    assert 'interview_id' in result, '响应缺少interview_id字段'
    assert 'first_question' in result, '响应缺少first_question字段'
    assert 'estimated_duration' in result, '响应缺少estimated_duration字段'
    print(f'  状态码: {response.status_code}')
    print(f'  响应: {json.dumps(result, ensure_ascii=False)}')
    return result.get('interview_id')

def test_interview_evaluate(interview_id):
    print('测试 /api/interview/evaluate...')
    url = f'{BASE_URL}/api/interview/evaluate'
    headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}
    data = {
        'interview_id': interview_id,
        'question': '请介绍一下自己',
        'answer': '我是张三，有5年开发经验...'
    }
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200, f'状态码错误: {response.status_code}'
    result = response.json()
    assert 'score' in result, '响应缺少score字段'
    assert 'feedback' in result, '响应缺少feedback字段'
    assert 'next_question' in result, '响应缺少next_question字段'
    assert 'is_continue' in result, '响应缺少is_continue字段'
    print(f'  状态码: {response.status_code}')
    print(f'  响应: {json.dumps(result, ensure_ascii=False)}')
    print('  通过!')

def test_interview_end(interview_id):
    print('测试 /api/interview/end...')
    url = f'{BASE_URL}/api/interview/end'
    headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}
    data = {'interview_id': interview_id}
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200, f'状态码错误: {response.status_code}'
    result = response.json()
    assert 'interview_id' in result, '响应缺少interview_id字段'
    assert 'final_score' in result, '响应缺少final_score字段'
    assert 'summary' in result, '响应缺少summary字段'
    assert 'recommendation' in result, '响应缺少recommendation字段'
    print(f'  状态码: {response.status_code}')
    print(f'  响应: {json.dumps(result, ensure_ascii=False)}')
    print('  通过!')

def test_unauthorized():
    print('测试无API Key访问...')
    url = f'{BASE_URL}/api/qa/ask'
    headers = {'Content-Type': 'application/json'}
    data = {'question': '测试问题'}
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 401, f'状态码错误: {response.status_code}'
    print(f'  状态码: {response.status_code}')
    print('  通过!')

def test_missing_params():
    print('测试缺少必需参数...')
    url = f'{BASE_URL}/api/qa/ask'
    headers = {'Content-Type': 'application/json', 'X-API-Key': API_KEY}
    data = {}
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 422, f'状态码错误: {response.status_code}'
    print(f'  状态码: {response.status_code}')
    print('  通过!')

if __name__ == '__main__':
    print('=' * 50)
    print('开始API测试...')
    print('=' * 50)

    try:
        test_qa_ask()
        print()
        test_resume_analyze()
        print()
        interview_id = test_interview_start()
        print()
        if interview_id:
            test_interview_evaluate(interview_id)
            print()
            test_interview_end(interview_id)
            print()
        test_unauthorized()
        print()
        test_missing_params()
        print()
        print('=' * 50)
        print('所有测试通过!')
        print('=' * 50)
    except AssertionError as e:
        print(f'测试失败: {e}')
    except requests.exceptions.ConnectionError:
        print('无法连接到服务器，请确保Flask应用正在运行')