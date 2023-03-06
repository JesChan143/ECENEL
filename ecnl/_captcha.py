import json,base64, requests as req, random, string
from ._headers import *


REPORT_URL = "https://api.apitruecaptcha.org/one/report_error"
SOLVE_URL = "https://api.apitruecaptcha.org/one/gettext"

class CaptchaSolver():
  
  def __init__(self,userid,apikey):
    self.userid = userid
    self.apikey = apikey
    
  def solve(self,data):
    
    info = {
      "userid":self.userid,"apikey":self.apikey,
      "data":data
    }
   
    result = {"success":False,"data":[self.dCaptcha()]}
    
    try:
      
      ocr = req.post(SOLVE_URL,json=info)
      data = ocr.json()

      if 'message' not in data:
        
        text = data['result']
        reqID = data['requestId']
        taken = data['time_taken']
        
        result['success'] = True
        result['data'] = [text,reqID,taken]
      
    except:
      pass
    
    return result
    
  def report(self,requestId):
    
    info = {
      "userid":self.userid,"apikey":self.apikey,
      "request_id":requestId
    } 
    
    report = req.post(REPORT_URL,json=info)
    
  def dCaptcha(self):
    return ''.join(random.choices(string.ascii_letters + string.digits,k=8))
