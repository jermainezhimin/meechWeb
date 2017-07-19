# Written by Jermaine Cheng, SUTD ca. 2016
from flask import Flask, render_template, request, url_for,json, redirect
from urllib import urlencode
import ast
import requests
import random
import datetime
import serial
import time

#####################################
## Functions
#####################################

bSpd = 'B5'

def gSpeed():
  ser.write('Q1\n')
  time.sleep(1)
  return ser.readline().strip()

def gHeart():
  ser.write('Q0\n')
  time.sleep(1)
  return ser.readline().strip()

def gRefill():
  ser.write('Q2\n')
  time.sleep(1)
  return ser.readline().strip()

#Gets Serial from the raspberry pi
def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
 
  return cpuserial

#####################################
## Flask App
#####################################

#Initialization Serial 
ser = serial.Serial('/dev/ttyACM0', 115200) # Establish the connection on a specific port
time.sleep(3) #give the connection a second to settle

#Flask app initializing and datetime json formatting
app = Flask(__name__)
app.debug = True
json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)

@app.route("/")
def start():
  return render_template('register.html')

@app.route("/bInit")
def bInit():
  ser.write('BI\n')
  time.sleep(1)
  return
  
@app.route("/cInit")
def cInit():
  ser.write('CI\n')
  time.sleep(1)
  return
 
@app.route("/cSet/<mode>")
def cSet(mode):
  if (mode == "START"):
	  ser.write('C1\n')
	  time.sleep(1)
	  ser.readline().strip()
	  return 
    
  elif (mode == "STOP"):
	  ser.write('C0\n')
	  time.sleep(1)
	  ser.readline().strip()
	  return 
 
@app.route("/bSet/<mode>")
def bSet(mode):
  if (mode == "START"):
    ser.write(bSpd + '\n')
    time.sleep(1)
    ser.readline().strip()
    return 
  elif (mode == "STOP"):
    ser.write('B0\n')
    time.sleep(1)
    ser.readline().strip()
    return 

@app.route("/bSpeed/<number>")
def bSpeed(number):
  if number < 7 : 
    bSpeed = 'B' + str(number)
    ser.write('B' + str(number) + '\n')
    time.sleep(1)
    ser.readline().strip()
    return 
@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/signIn',methods=['GET'])
def signIn():
 
    # read the posted values from the UI
    pName = request.args['pName']
    phpnum = request.args['phpnum']
 
    # validate the received values
    if pName and phpnum:
      url = 'http://hirudo-dev.ap-southeast-1.elasticbeanstalk.com/patient/signin'
      data = {
        "pname" : pName,
        "phpnum" : phpnum,
      }
      
      r = requests.get(url, data=data)
      if r.status_code==200:
        p = r.json()
        app.logger.debug(p)    
        return redirect(url_for('data',patient=p))
    else:
      return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route('/showSignUp')
def showSignUp():
    return render_template('/signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    pName = request.form['pName']
    phpnum = request.form['phpnum']
    pGender = request.form['pGender']
    admittedDate = request.form['admittedDate']
    tid = request.form['tid']
    wid = request.form['wid']
    bed = request.form['bed']
 
    # validate the received values
    if pName and phpnum and pGender and admittedDate and tid and wid and bed :
      url = 'http://hirudo-dev.ap-southeast-1.elasticbeanstalk.com/patient/register'
      data = {
        "pname" : pName,
        "phpnum" : phpnum,
        "pgender" : pGender,
        "admittedDate" : admittedDate,
        "tid" : tid,
        "wid" : wid,
        "bed" : bed
        }
      
      headers = {'Content-Type': 'application/json'}
      r = requests.post(url, data=json.dumps(data), headers=headers)
     # app.logger.debug(r.json())
      if r.status_code==200:
        payload = {"pname" : pName, "phpnum" : phpnum}
        req = requests.get('http://hirudo-dev.ap-southeast-1.elasticbeanstalk.com/patient/id', params=payload)
        p = req.json()
        app.logger.debug(p)    
        return redirect(url_for('data',patient=p))
    else:
      return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route("/data/<patient>")
def data(patient):
  pat = json.loads(str(patient).replace("u'","'").replace("'","\""))
  app.logger.debug(pat)
  app.logger.debug(type(pat))

  pid = pat['pid']
  pname = pat['pname']
  if (pat['pgender'].lower() == 'm'):
    pGender = 'Male'
  else:
    pGender = 'Female'
  wid = pat['wid']
  bed = pat['bed']

  temp = round(random.uniform(36.5, 37.9),1)
  app.logger.debug(temp)
  hr = 67.5
  app.logger.debug(hr)
  fr = 0
  app.logger.debug(fr)
  time = datetime.datetime.now()
  url = 'http://hirudo-dev.ap-southeast-1.elasticbeanstalk.com/patient/data'
  data = {"uid": pid,
          "date": time,
          "Temp": temp,
          "HR": hr,
          "FR": fr
          }

  headers = {'Content-Type': 'application/json'}
  r = requests.post(url, data=json.dumps(data), headers=headers)
  
  return render_template('/home.html',pid=pid,pname=pname, bed=bed,wid=wid,pGender=pGender, time=time)

@app.route('/updateData/<int:patient>')
def updateData(patient):
  pid = patient
  temp = round(random.uniform(36.5, 37.9),1)
  app.logger.debug(temp)
  hr = gHeart()
  app.logger.debug(hr)
  fr = gSpeed()[:2]
  app.logger.debug(fr)
  time = datetime.datetime.now()
  url = 'http://hirudo-dev.ap-southeast-1.elasticbeanstalk.com/patient/data'
  data = {"uid": pid,
          "date": time,
          "Temp": temp,
          "HR": hr,
          "FR": fr
          }
  app.logger.debug(data)

  headers = {'Content-Type': 'application/json'}
  r = requests.post(url, data=json.dumps(data), headers=headers)
  return json.dumps(data)



if __name__ == "__main__":
    app.run()


