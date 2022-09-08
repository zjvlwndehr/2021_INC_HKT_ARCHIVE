# Client 192.168.50.14
# Server 192.168.50.17
# Computer, TV, Light, Ondol(Boiler) = 0, 1, 2, 3
# on, off = 1, 0

class Dummy(Exception):
    pass

class Storage(Exception):
    def __init__(self):
        from htmadmin import HTMLFILES
        self.conf = Dummy()
        self.config()
        self.conf.scoreserver = "10.141.9.88"

        self.data = datahandler(self)
        self.html = HTMLFILES(self)
        self.hw = hwmanager(self)
        pass
    
    def config(self):
        from json import load
        f = open('config.json', 'r')
        config = load(f)
        self.configparser(config)
        f.close()

        return 0

    def configparser(self, config):
        try:
            self.conf.userid = config['userid']
        except KeyError:
            raise KeyError('Config Userid is not defined')
        return 0
    
    #def usrchk(self):
    #    from time import sleep
    #    if self.conf.checker == "ping":
    #        from os import system
    #        while True:
    #            rtn = system("ping -n 1 " + self.conf.host + " > nul")
    #            if rtn == 0: 
    #                if self.data.user == False: self.data.actionupdate(4, True)
    #            else:
    #                if self.data.user == True: self.data.actionupdate(4, False)
    #            sleep(5)
    #    
    #    elif self.conf.checker == "ftp":
    #        userid = "test"
    #        password = "test"
    #        import ftplib
    #        while True:
    #            try:
    #                # timeout 2 sec
    #                ftp = ftplib.FTP(self.conf.host, userid, password, timeout=2)
    #                ftp.quit()
    #                if self.data.user == False: self.data.actionupdate(4, True)
    #                break
    #            except ftplib.all_errors:
    #                if self.data.user == False: self.data.actionupdate(4, False)
    #                sleep(5)
    #                break
    #    pass

class datahandler(Exception):
    def __init__(self, storage):
        self.storage = storage
        self.data = []
        self.led = False
        self.boil = False
        self.dataload()
        pass
    
    def dataload(self):
        from json import loads
        f = open('data.json', 'r')
        try:
            data = loads(f.read())
        except:
            data = {"userid": None, "data": []}

        f.close()
        if self.storage.conf.userid != data['userid']:
            if (data['userid'] == None or data['userid'] == '') and data["data"] == []:
                self.data = []
                self.datastore()
            else:
                raise NameError('Userid is not matched')
        
        self.data = data["data"]
        
        return 0

    def datastore(self):
        from json import dumps
        f = open('data.json', 'w')
        f.write(dumps({"userid": self.storage.conf.userid, "data": self.data}))
        f.close()
        return 0

    def actionupdate(self, action: int, value: bool):
        from time import time
        if action in [0,1,2,3]:
            print("Action: " + str(action) + " " + str(value))
            self.data.append([action, value, time()])
            self.datastore()
            if action == 2:
                self.led = value
            elif action == 3:
                self.boil = value
            self.sendtoserver(action, value)

            return 0
        else:
            raise ValueError('Invalid action')
    
    def sendtoserver(self, action: int, value: bool):
        from json import dumps
        from requests import get
        
        try:
            r = get("http://" + self.storage.conf.scoreserver + "/action", json={"userid": self.storage.conf.userid, "action": action, "status": int(value)})
        except:
            print("Server is not online")
            return -1
        if r.status_code == 200:
            return 0
        else:
            raise ValueError('Score Server Error')

class hwmanager(Exception):
    def __init__(self, storage):
        self.storage = storage

        import RPi.GPIO as GPIO

        self.GPIO = GPIO
        self.led_channel = 17
        self.lcd_channel = 27

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.led_channel, GPIO.OUT)
        GPIO.setup(self.lcd_channel, GPIO.OUT)

        GPIO.output(self.led_channel, GPIO.LOW)
        GPIO.output(self.lcd_channel, GPIO.LOW)

        self.storage.data.led = False
        self.storage.data.boil = False 

        pass
    
    def i2c_load(self):
        if self.storage.data.boil == True:
            import I2C
            self.lcdmanager = I2C.lcd()
        else:
            raise ValueError('LCD is not connected')

    def manage(self, action: int):
        from threading import Thread
        if action == 0:
            if self.storage.data.led == True:
                Thread(target=self.led_off).start()
                self.storage.data.actionupdate(2, False)
            else:
                Thread(target=self.led_on).start()
                self.storage.data.actionupdate(2, True)
        elif action == 1:
            if self.storage.data.boil == True:
                Thread(target=self.lcd_off_thread).start()
                self.storage.data.actionupdate(3, False)
            else:
                Thread(target=self.lcd_on_thread).start()
                self.storage.data.actionupdate(3, True)
        else:
            raise ValueError('Invalid action')
        return 0

    def led_on(self):
        from time import sleep
        self.GPIO.output(self.led_channel, self.GPIO.HIGH)
        if self.storage.data.boil == True: 
            self.lcdmanager.lcd_clear()
            self.lcdmanager.lcd_display_string("MainRoom LED ON", 1)
            self.lcdmanager.lcd_display_string("Now: 6*C", 2)
            sleep(2)
            self.lcdmanager.lcd_clear()
            self.lcdmanager.lcd_display_string("2021-11-27", 1)
            self.lcdmanager.lcd_display_string("Now: 6*C", 2)
        
    def led_off(self):
        from time import sleep
        self.GPIO.output(self.led_channel, self.GPIO.LOW)
        if self.storage.data.boil == True: 
            self.lcdmanager.lcd_clear()
            self.lcdmanager.lcd_display_string("MainRoom LED OFF", 1)
            self.lcdmanager.lcd_display_string("Now: 6*C", 2)
            sleep(2)
            self.lcdmanager.lcd_clear()
            self.lcdmanager.lcd_display_string("2021-11-27", 1)
            self.lcdmanager.lcd_display_string("Now: 6*C", 2)

    def lcd_on_thread(self):
        from time import sleep
        self.GPIO.output(self.lcd_channel, self.GPIO.HIGH)
        sleep(0.5)
        self.i2c_load()
        sleep(1)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("Hi!", 1)
        self.lcdmanager.lcd_display_string("BOILER V1.0", 2)
        sleep(2)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("Loading", 1)
        self.lcdmanager.lcd_display_string("Please Wait...", 2)
        sleep(2)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("Set Temp to 22*C", 1)
        self.lcdmanager.lcd_display_string("Now: 6*C", 2)
        sleep(1)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("22*C AUTO", 1)
        self.lcdmanager.lcd_display_string("Now: 6*C", 2)
        sleep(1)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("Set Temp to 22*C", 1)
        self.lcdmanager.lcd_display_string("Now: 6*C", 2)
        sleep(1)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("22*C AUTO", 1)
        self.lcdmanager.lcd_display_string("Now: 6*C", 2)
        sleep(1)
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("2021-11-27", 1)
        self.lcdmanager.lcd_display_string("Now: 6*C", 2)
    
    def lcd_off_thread(self):
        from time import sleep
        self.lcdmanager.lcd_clear()
        self.lcdmanager.lcd_display_string("Boil Off", 1)
        self.lcdmanager.lcd_display_string("Bye", 2)

        sleep(1)
        self.lcdmanager.lcd_clear()
        del(self.lcdmanager)
        self.GPIO.output(self.lcd_channel, self.GPIO.LOW)

        return 0

from flask import *

storage = Storage()
app = Flask(__name__)
app.debug = True

@app.route('/')
def main():
    rtn = request.args
    print(rtn)
    if 'action' in rtn and rtn["action"] in ["led", "boil"]:
        if rtn["action"] == "led":
            storage.hw.manage(0)
        elif rtn["action"] == "boil":
            storage.hw.manage(1)
    print(storage.data.led, storage.data.boil)
    return storage.html.mainpageheader()

@app.route('/worktest')
def pagetest():
    return "It Works!"

@app.route('/test')
def test():
    return "OK"

# Return Icons for each action
@app.route('/icons/<iconfile>')
def icon(iconfile):
    try:
        return send_file('icon/{icofile}'.format(icofile=iconfile))
    except:
        raise ValueError('Invalid icon file')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)