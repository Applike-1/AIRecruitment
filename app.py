from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 注册蓝图
from app.recruit_qa import recruit_qa_bp
from app.resume_filter import resume_filter_bp
from app.ai_interview import ai_interview_bp

app.register_blueprint(recruit_qa_bp, url_prefix='/api/qa')
app.register_blueprint(resume_filter_bp, url_prefix='/api/resume')
app.register_blueprint(ai_interview_bp, url_prefix='/api/interview')

@app.route('/')
def hello():
    # 提供index.html文件
    return send_from_directory(os.getcwd(), 'index.html')

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)