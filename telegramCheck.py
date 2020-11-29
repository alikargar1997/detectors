import schedule
import threading
import time
import requests as req
import os
import logging


class TelegramCheck:
    def __init__(self):
        self.token = "1068720893:AAHND0FT6WuhOT-_rWbPDwLurpqqasQpt-4"
        self.date = {"m_date": None}
        self.url = "https://api.telegram.org/bot{}/getUpdates".format(self.token)
        self.schedule_delay_min = 10

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    def get_message(self):
        while True:
            try:
                new_date = req.post(self.url, {"limit": 1, 'offset': -1}).json()['result'][0]['channel_post']['date']
                break
            except:
                time.sleep(20)
        if new_date == self.date['m_date']:
            os.system("kill -9 `cat /home/twitter_stream_socket/twitter_stream.pid`")
            os.system("rm -rf /home/twitter_stream_socket/twitter_stream.pid")
            os.system(
                "nohup python3.6 /home/twitter_stream_socket/TW_Socket.py > /home/twitter_stream_socket/log & echo $! > twitter_stream.pid")
            req.get(
                url="http://login.qasedak-sms.ir/SMSInOutBox/SendSms?username=Atipardaz&password=22965&from=10000088960782&to=09378105380&text=twitter socket freezed!")
            logging.info('message sent')
        else:
            self.date.update({"m_date": new_date})

    def schedule_task(self):
        schedule.every(self.schedule_delay_min).minutes.do(self.get_message)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    tc = TelegramCheck()
    tc.schedule_task()
