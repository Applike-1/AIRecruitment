from flask import Blueprint

resume_filter_bp = Blueprint('resume_filter', __name__)

from . import routes