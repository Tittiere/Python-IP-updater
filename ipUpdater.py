from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from requests import get
import smtplib, json, ssl, os

def pause():
    if os.name == 'nt':
        os.system('pause')
    else:
        input('Press enter to continue ')

# exe way of knowing path to file:
jsonPath = os.getcwd() + os.path.sep + "config.json"
# vscode .py program way of knowing path to file
# jsonPath = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "config.json"
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
        if type(config['mailData']['receiverEmail']) == type(config['mailData']['senderEmail']):
            print('Now you can send your IP to multiple mails.\nIf you want to do it update the config.json file with\na python list of the mails you want to send the ip.\nIf you don\'t know how to write one, delete the config.json file and the program will create an example for you.')
            aus = []
            aus.append(config['mailData']['receiverEmail'])
            config['mailData']['receiverEmail'] = aus
            updateJson()
    except Exception as e:
        print(e)
        noJson()

def noJson():
    global config
    config['mailData'] = {
        'senderEmail': 'sender',
        'receiverEmail': ['receiver1', 'receiver2', 'delete or add users if you need'],
        'senderPwd': 'password'
    }
    config['oldIP'] = get('https://api.ipify.org').text
    config['interval'] = 'interval (minutes)'
    with open(jsonPath, 'w') as config_file:
        json.dump(config, config_file, indent=4)
    print('Write your email data in the "config.json" file, then press a key')
    while True:
        pause()
        with open(jsonPath) as config_file:
            config2 = json.load(config_file)
        if config == config2:
            print('Please, write your mail data in the "config.json" file')
        else:
            break
        
def updateJson():
    global config
    with open(jsonPath, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def updateIP():
    global send, ip, timestamp, config
    try:
        ip = get('https://api.ipify.org').text
    except:
        pass
    with open(jsonPath) as config_file:
        config = json.load(config_file)
    if len(ip) <= 15:
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
    context = ssl.create_default_context()
    for mail in config['mailData']['receiverEmail']:
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
                server.login(senderEmail, pwd)
                server.sendmail(senderEmail, mail, msg)
                server.quit()
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
            print('Username and Password not accepted. Edit the "config.json" file.\nIf this same error comes up again, you might have to give access\nto less secure apps on your gmail account\nhttps://myaccount.google.com/lesssecureapps')
            sched.remove_all_jobs()

def check():
    global config
    print('Checking your ip -', str(datetime.now()).split(" ")[1].split(".")[0])
    updateIP()
    ip = config['oldIP']
    if send == True:
        print(f'Your IP has changed\nI\'m sending a new mail\nNew IP: {ip}')
        sendEmail(msg)

loadJson()
try:
    print('Welcome to Gmail IP updater!')
    sched = BlockingScheduler(standalone=True)
    mins = config['interval'].replace(',', '.').replace('"', '')
    sched.add_job(check, 'interval', minutes=float(mins))
    sched.start()
except ValueError:
    print('The interval you set in the "config.json" file is not acceptable\nPlease write an acceptable value and try again\nTip: you can write integers or floats')
    pause()
except KeyboardInterrupt:
    print('Thanks for using Claristorio\'s Gmail IP updater!\nMy GitHub: https://github.com/claristorio/python')
    pause()