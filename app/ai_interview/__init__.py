from flask import Blueprint

ai_interview_bp = Blueprint('ai_interview', __name__)

from . import routes