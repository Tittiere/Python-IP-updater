from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from requests import get
import smtplib, json, os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def pause():
    if os.name == 'nt':
        os.system('pause')
    else:
        input('Press enter to continue ')

jsonPath = os.getcwd() + os.path.sep + "config.json"
config = {}
std_config = {}
std_config['mailData'] = {
    'senderEmail': 'sender',
    'receiverEmail': ['receiver1', 'receiver2', 'delete or add users if you need'],
    'senderPwd': 'password'
}
std_config['oldIP'] = 'None'
std_config['interval'] = 'interval (minutes)'

scheduler = BlockingScheduler(standalone=True)

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
        return True
    except FileNotFoundError:
        noJson()
        return False

def noJson():
    with open(jsonPath, 'w') as config_file:
        json.dump(std_config, config_file, indent=4)
    print('Write your email data in the "config.json" file')
        
def updateJson():
    global config
    with open(jsonPath, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def updateIP():
    global send, ip, timestamp, config
    try:
        ip = get('https://api64.ipify.org/').text
    except:
        pass
    with open(jsonPath) as config_file:
        config = json.load(config_file)
    if len(ip) <= 15 and ip.lower() != "bad gateway":
        if ip != config['oldIP']:
            timestamp = str(datetime.now()).split(".")[0]
            send = True
            config['oldIP'] = ip
        else:
            send = False

def sendEmail(msg):
    global timestamp, scheduler
    msg = msg + str(ip) + "\n" + str(timestamp)
    port = 587
    pwd = config['mailData']['senderPwd']
    senderEmail = config['mailData']['senderEmail']
    for mail in config['mailData']['receiverEmail']:
        try:
            with smtplib.SMTP('smtp.office365.com', port) as server:
                server.starttls()
                server.login(senderEmail, pwd)
                server.sendmail(senderEmail, mail, msg)
                server.quit()
            updateJson()
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
            print('Username or Password not accepted. Edit the "config.json" file.')
            scheduler.remove_all_jobs()

def check():
    global config
    print('Checking your ip -', str(datetime.now()).split(" ")[1].split(".")[0])
    updateIP()
    ip = config['oldIP']
    if send == True:
        print(f'Your IP has changed\nI\'m sending a new mail\nNew IP: {ip}')
        sendEmail(msg)

cont = loadJson()
if config == std_config:
    cont = False
    print("Please, add all the information needed in the config.json file")
if cont:
    try:
        print('Welcome to IP updater!')
        check()
        mins = config['interval'].replace(',', '.').replace('"', '')
        scheduler.add_job(check, 'interval', minutes=float(mins), id='AA')
        scheduler.start()
    except ValueError:
        print('The interval you set in the "config.json" file is not acceptable\nPlease write an acceptable value and try again\nTip: you can write integers or floats')
        pause()
    except KeyboardInterrupt:
        print('Thanks for using Tittiere\'s Gmail IP updater!\nMy GitHub: https://github.com/Tittiere')
        pause()
else:
    pause()