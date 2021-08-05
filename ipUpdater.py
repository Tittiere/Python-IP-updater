from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from requests import get
import smtplib, ssl, os, json

jsonPath = os.path.dirname(os.path.realpath(__file__)) + "\config.json"
config = {}

msg = """\
Subject: Your IP has changed!

Hi, here's your new IP:\n"""

timestamp = datetime.now()
send = False
ip = 'null'

def loadJson():
    global config
    try:
        with open(jsonPath) as config_file:
            config = json.load(config_file)
    except:
        noJson()

def noJson():
    global config
    config['mailData'] = {
        'senderEmail': 'sender',
        'recieverEmail': 'reciever',
        'senderPwd': 'password'
    }
    config['oldIP'] = get('https://api.ipify.org').text
    config['interval'] = 'interval (minutes)'
    with open(jsonPath, 'w') as config_file:
        json.dump(config, config_file, indent=4)
    print('Write your email data in the "config.json" file, then press a key')
    os.system("pause")

def updateJson():
    global config
    with open(jsonPath, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def updateIP():
    global send, ip, timestamp
    try:
        ip = get('https://api.ipify.org').text
    except:
        pass
    if ip != config['oldIP']:
        timestamp = str(datetime.now()).split(".")[0]
        send = True
        config['oldIP'] = ip
        updateJson()
    else:
        send = False

def sendEmail(msg):
    global timestamp
    msg = msg + str(ip) + "\n" + str(timestamp)
    port = 465  # For SSL
    pwd = config['mailData']['senderPwd']
    senderEmail = config['mailData']['senderEmail']
    receiverEmail = config['mailData']['recieverEmail']
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
            server.login(senderEmail, pwd)
            server.sendmail(senderEmail, receiverEmail, msg)
            server.quit()
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
        print('Username and Password not accepted. Edit the "config.json" file.\nIf this same error comes up again, you might have to give access\nto less secure apps on your gmail account\nhttps://myaccount.google.com/lesssecureapps')
        sched.remove_all_jobs()

def check():
    print('Checking your ip -', str(datetime.now()).split(" ")[1].split(".")[0])
    updateIP()
    if send == True:
        print(f'Your IP has changed\nI\'m sending a new mail\nNew IP: {ip}')
        sendEmail(msg)

loadJson()
try:
    print('Welcome to Gmail IP updater!')
    sched = BlockingScheduler(standalone=True)
    print(float(config['interval']))
    sched.add_job(check, 'interval', minutes=float(config['interval']))
    sched.start()
except ValueError:
    print('The interval you set in the "config.json" file is not acceptable\nPlease write an acceptable value and try again\nTip: you can write integer or floats')
    os.system("pause")
except KeyboardInterrupt:
    print('Thanks for using Claristorio\'s Gmail IP updater!\nMy GitHub: https://github.com/claristorio/python')
    os.system("pause")