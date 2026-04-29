from flask import Blueprint

recruit_qa_bp = Blueprint('recruit_qa', __name__)

from . import routes