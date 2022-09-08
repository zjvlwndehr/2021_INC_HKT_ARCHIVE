import os
import firebase_admin
from firebase_admin import credentials, db
import time
import json
import pandas as pd
from flask import *
class DB_API():
    ON, OFF = 1, 0 ## machine on/off
    COMPUTER, TV, LIGHT, ONDOL = 0, 1, 2, 3 ## 인덱스넘버 machinemode
    
    value = [200, 100, 300, 500] ## 기기 가중치
    cred = credentials.Certificate("hackertondb-8ff1e-firebase-adminsdk-5bop7-2f49233a6d.json")
    firebase_admin.initialize_app(cred,{"databaseURL":"https://hackertondb-8ff1e-default-rtdb.firebaseio.com/"})
    
    def __init__(self):
        self.__init__
    
    def exists_key(keyPath):
        if os.path.exists(keyPath):
            return 0
        else:
            return 1
    
    ### score을 기준으로 순위가 내림차순인 html 표를 response로 전달합니다.
    def sort(self, user, ref):
        arr = user
        sc = [0] * len(ref)
        for i in range(0, len(ref)):
            sc[i] = ref[user[i]]['score']

        for r in range(1, len(user)):
            for i in range(r, 0, -1):
                if(ref[user[i-1]]['score'] < ref[user[i]]['score']):
                    arr[i-1], arr[i] = arr[i], arr[i-1]
                    sc[i-1], sc[i] = sc[i], sc[i-1]

        data = {'score':sc, 'id':arr}
        df = pd.DataFrame(data)
        
        html = df.to_html('index.html')
        print(df)
        return 0

    ### db를 업데이트 합니다 ###
    def update_db_reference(self,userid, machinemode, onoff):
        ref = db.reference('/')
        ref_time = db.reference(userid + '/time_prev')
        time_prev = ref_time.get()
        ref_score = db.reference(userid + '/score')
        score_prev = ref_score.get()
        time_now = int(time.time())

        if onoff == self.ON:
            print("debug: score_prev:", score_prev)
            score = int(((time_now - time_prev) *  self.value[machinemode]) / 1000) + score_prev
            print("debug: New score:{0}".format(score))
            ref.update({
                userid : {
                    'score' : score,
                    'time_prev' : int(time_now)
                }
            })
            
            return self.sort(list(ref.get()), ref.get())
        elif onoff == self.OFF:
            ref.update({
                userid : {
                    'score' : score_prev,
                    'time_prev' : int(time_now)
                }
            })
            return self.sort(list(ref.get()), ref.get())
        else:
            return 1

### json key path ###
keyPath = os.path.dirname(__file__) + "hackertondb-8ff1e-firebase-adminsdk-5bop7-9a34aef574.json"
# userid = 'tklco1'
isinstance = DB_API()

# isinstance.update_db_reference(userid, DB_API.ONDOL, DB_API.OFF)

app = Flask(__name__)
app.debug = True

@app.route('/')
def main():
    rtn = request.args
    print(rtn)
    return "1"


@app.route('/worktest')
def pagetest():
    return "It Works!"

@app.route('/action')
def action():
    data = request.json
    print(data)
    isinstance.update_db_reference(userid=data["userid"], machinemode=data["action"], onoff=data["status"])
    return "OK"

@app.route('/scoreboard')
def score():
    f = open('index.html','r')
    rtn = f.read()
    f.close()
    return rtn

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)