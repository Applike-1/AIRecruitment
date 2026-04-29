from pydantic import BaseModel, Field
from typing import Optional, List

class QAAskRequest(BaseModel):
    question: str = Field(..., description="用户提出的招聘相关问题")
    user_id: Optional[str] = Field(None, description="用户ID")

class QAAskResponse(BaseModel):
    answer: str = Field(..., description="AI生成的答案")
    sources: List[str] = Field(default_factory=list, description="参考的知识库文档")
    confidence: float = Field(..., description="回答置信度 0-1")

class ResumeAnalyzeRequest(BaseModel):
    resume_content: str = Field(..., description="简历内容（文本或HTML）")
    job_description: str = Field(..., description="岗位描述")
    user_id: Optional[str] = Field(None, description="用户ID")

class ResumeAnalyzeResponse(BaseModel):
    score: float = Field(..., description="综合评分 0-100")
    skills_match: float = Field(..., description="技能匹配度 0-1")
    experience_match: float = Field(..., description="经验匹配度 0-1")
    education_match: float = Field(..., description="学历匹配度 0-1")
    overall_comment: str = Field(..., description="综合评价")
    recommendation: str = Field(..., description="推荐意见：强烈推荐/推荐/待定/不推荐")

class InterviewStartRequest(BaseModel):
    job_position: str = Field(..., description="应聘职位")
    candidate_name: Optional[str] = Field(None, description="候选人姓名")
    candidate_info: Optional[dict] = Field(None, description="候选人背景信息")
    user_id: Optional[str] = Field(None, description="用户ID")

class InterviewStartResponse(BaseModel):
    interview_id: str = Field(..., description="面试会话ID")
    first_question: str = Field(..., description="第一个面试问题")
    estimated_duration: int = Field(..., description="预计面试时长（分钟）")

class InterviewEvaluateRequest(BaseModel):
    interview_id: str = Field(..., description="面试会话ID")
    question: str = Field(..., description="当前问题")
    answer: str = Field(..., description="候选人回答")
    user_id: Optional[str] = Field(None, description="用户ID")

class InterviewEvaluateResponse(BaseModel):
    score: float = Field(..., description="回答评分 0-100")
    feedback: str = Field(..., description="评价反馈")
    next_question: Optional[str] = Field(None, description="下一问题（若无则为空）")
    is_continue: bool = Field(..., description="是否继续面试")

class InterviewEndRequest(BaseModel):
    interview_id: str = Field(..., description="面试会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")

class InterviewEndResponse(BaseModel):
    interview_id: str = Field(..., description="面试会话ID")
    final_score: float = Field(..., description="最终评分 0-100")
    summary: str = Field(..., description="面试总结")
    recommendation: str = Field(..., description="录用建议")