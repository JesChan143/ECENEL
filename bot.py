from ecnl import Client

#Captcha Api Credentials
userid = "hakdog@gmail.com"
apikey = "mgaungas"

# True Auto Solve, False Manual Solve
bot = Client("username","password",True)
bot.setApi(userid,apikey)
bot.doTask()

