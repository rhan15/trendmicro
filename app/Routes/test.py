from flask import Blueprint,request
from app.helpers.handlerResponse import *
from app.helpers.mdl import *


test_bp = Blueprint("test", __name__)
@test_bp.route('/')
def test():
   return proced_test()

def proced_test():
   try:
       parse_dt9_filename("DT91A01O.5CH")
       return "Success"
   except Exception as e:
       return create_error_response(message="Terjadi Kesalahan", error_message=f"Error: {e}")
      