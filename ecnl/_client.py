import json,base64,re, time,os
from requests import Session
from bs4 import BeautifulSoup as bs
from PIL import Image, ImageOps, ImageFilter
from io import BytesIO
from ._headers import *
from ._captcha import CaptchaSolver

INDEX = "https://ecandl.net"

LOGIN_URL = f"{INDEX}/login.php"
DASHB_URL = f"{INDEX}/dashboard"
CAPTC_URL= f"{INDEX}/session_captcha.php"
SOLVR_URL = "https://ecnl-ecnl.vercel.app/getWord"

class Client():
  
  def __init__(self,username,password,enabled=False):
    self.username = username
    self.password = password
    self.enabled = enabled
    self.s = Session()
    
    self.key = None
    self.userid = None
    self.apikey = None
    self.logged = False
    self.jumbled = None
    self.definition = None
    
    self.banner()
  
  def login(self):
    
    self.setCookie()
    
    if not self.isLogged():
      while True:
        
        result = self.cHelper()
        data = self.getInfo(result['data'][0])
        
        login = self.s.post(LOGIN_URL,data=data,headers=head)
   
        if login.url == DASHB_URL:
          self.banner()
          self.getCookie()
          self.setKey()
          self.logged = True
          break
        else:
          if len(result['data']) == 2:
            ocr.report(result['data'][1])
        
    else:
      self.setKey()
      self.logged = True
  
  def cHelper(self):
    
    ocr = CaptchaSolver(self.userid,self.apikey)
    
    captcha = ocr.solve(self.getCaptcha()) if self.enabled else self.showCaptcha()
    
    return captcha
   
  def isLogged(self):
    
    dash = self.s.get(DASHB_URL,headers=gHead)
    
    dashCt = bs(dash.content, "html.parser")
   
    logged = False
    
    if dash.url == DASHB_URL:
      logged = True
      
    return logged
  
  def getData(self):
    
    task = f"{INDEX}/jumble🤐problem/{self.key}/task"
    
    problem = self.s.get(task,headers=gHead)
    
    taskCt = bs(problem.content, "html.parser")
    strong = taskCt.find_all('strong')
    
    points = (strong[1].text).split('₱')[1]
    solved = [x for x in (strong[2].text).split(" ") if x.isdigit()]
    csrf = taskCt.find("input", {"name":"csrftoken"})['value']
    
    claim = True
    
    if int(solved[0]) < 50:
   
      self.jumbled = re.findall(r'\b[A-Z]+(?:\s+[A-Z]+)*\b',problem.text)[-1]
    
      self.definition = (taskCt.find_all("div", {"class": "text-center"})[1].text).split("➡ ")[1].split(' 👀')[0]
      
      claim = False
    
    return csrf, solved, points,claim
  
  def doTask(self):
    
    while self.logged:
      try:
        
        data = self.getData()
        
        if data[3]:
          self.claim()
        else:
          self.solve(data[0],data[1],data[2])
          
      except Exception as e:
        print(e)
        pass
    else:
      
      print(" [!] Login Failed")
  
  def claim(self):
    
    ocr = CaptchaSolver(self.userid,self.apikey)
    
    csrf = self.getData()[0]
    
    retry = 0
    
    while True:
      
      self.mt(40,f"[50/50] Solving Captcha, Tries ( {retry} )",1)
      
      csrf = self.getData()[0]
      
      result = ocr.solve(self.getCaptcha())
      captcha = result['data'][0]
      
      data = f"csrftoken={csrf}&answer_code={captcha}"
      alert_url = f"{INDEX}/jumble🤐alert/{self.key}/task"
      claim_url = f"{INDEX}/jumble🤢success/{self.key}/task"
      
      claim = self.s.post(claim_url,headers=pHead,data=data)
      alert = self.s.get(alert_url,headers=gHead)
      
      if claim.text == "token": #not in ['incorrect','bypass']:
        print(f" \x1b[1K\r[50/50] Solved and Claimed, Congratulation... \n")
        break
      else:
        if len(result['data']) == 2:
          ocr.report(result['data'][1])
      
      retry += 1
  
  def solve(self,csrf,num,pts):
    
    answer = self.unscrumble(self.definition,self.jumbled)["word"]
    
    self.mt(15,"[??/50] Fetching new question, please wait",1)
    
    print(f" \x1b[1K\r[{num[0]}/{num[1]}] Definition : {self.definition}")
    
    data = f"csrftoken={csrf}&answer_code={answer}"
    
    submit_url = f"{INDEX}/jumble🤢success/{self.key}/task"
    
    submit = self.s.post(submit_url,headers=pHead,data=data)
    
    color = "\033[92m" if submit.text == "captcha" else "\033[31m"
    
    print(f" Hint : \033[33m{self.jumbled}\033[0m     Answer : {color}{answer}\033[0m     Points : {pts}\n")
  
  def setKey(self):
    
    dash = self.s.get(DASHB_URL,headers=head)
    
    dashCt = bs(dash.content, "html.parser")
    
    key = dashCt.findAll("a", {"class":"dropdown-item"})[0]['href'].split('/')[4]
    
    self.key = key
  
  def setApi(self,userid,apikey):
    self.userid = userid
    self.apikey = apikey
    
    self.login()
  
  def setCookie(self):
    
    cookies = json.load(open("cookies.json"))
    
    if self.username in cookies:
      self.s.cookies["PHPSESSID"] = cookies[self.username]
      
  def getCookie(self):
    
    cookies = json.load(open("cookies.json"))
    cookies[self.username] = self.s.cookies['PHPSESSID']
    
    with open("cookies.json","w") as update:
      json.dump(cookies, update,indent=2)
  
  def getInfo(self,captcha):
    
    data = f"username={self.username}&password={self.password}&cf-turnstile-response=&answer_code={captcha}&submit="
    
    return data
  
  def showCaptcha(self):
    
    response = self.s.get(CAPTC_URL,headers=gHead)
    enc = base64.b64encode(response.content).decode('ascii')
    
    img = Image.open(BytesIO(response.content))
    img.show()
    
    captcha = input(" Enter Captcha : ") 
    
    return {"success":True,"data":[captcha]}
    
  def getCaptcha(self):
    
    response = self.s.get(CAPTC_URL,headers=gHead)
    enc = base64.b64encode(response.content).decode('ascii')
    
    #img = Image.open(BytesIO(response.content))
    #img.save("captcha.png")
    
    return enc
    
  def mt(self,num,remark,typ):
    typ = "%M:%S"
    for x in range(num,0,-1):
      print(f'\r{remark} : {time.strftime(typ,time.gmtime(x))}', end='')
      time.sleep(1)
      
  def unscrumble(self,definition,word):
    fetch = self.s.get(f"{SOLVR_URL}/{definition}/{word}")
    return fetch.json()
  
  def banner(self):
    
    os.system('cls' if os.name=='nt' else 'clear')
    
    print("""    __________  ____     
   / __/ ___/ |/ / /    Basic User     
  / _// /__/    / /__   v6.9 w/ Captcha Solver
 /___/\___/_/|_/____/   By : xnote12 | Jojo\n""") 