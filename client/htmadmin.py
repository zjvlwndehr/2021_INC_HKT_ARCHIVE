class HTMLFILES(Exception):
    def __init__(self, storage):
        self.storage = storage
        pass

    def mainpageheader(self):

        if self.storage.data.led == True:
            led = '''<img src="/icons/led_on.png" alt="LED ON" onclick="location.href='/?action=led'">'''
        else:
            led = '''<img src="/icons/led_off.png" alt="LED OFF" onclick="location.href='/?action=led'">'''
        
        if self.storage.data.boil == True:
            boil = '''<img src="/icons/boil_on.png" alt="BOIL ON" onclick="location.href='/?action=boil'">'''
        else:
            boil = '''<img src="/icons/boil_off.png" alt="BOIL OFF" onclick="location.href='/?action=boil'">'''

        return '''
<!DOCTYPE html>
<html lang="kr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Manager</title>
</head>
<body>
    <div class="container">
        <h1>Device Manager</h1>
        <h2>LED</h2>
        {led}
        <h2>Boiler</h2>
        {boil}
    </div>
    <div class="container">
        <h1>ScoreBoard</h1>
        <iframe src="http://{serverip}/scoreboard" width="100%" height="500px"></iframe>
    </div>
</body>
</html>
        '''.format(led=led, boil=boil, serverip=self.storage.conf.scoreserver)