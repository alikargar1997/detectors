# from websocket import create_connection
import json
import logging
import time
from datetime import datetime, timezone
import requests as req
from dateutil import tz
import asyncio
import websockets
import os

from_zone = tz.gettz('UTC')
to_zone = tz.tzlocal()


def ExtractFieldsMessage(tweet):
    result = json.loads(tweet)
    date = utc_to_local(result['@timestamp'])
    tweet_link = result['source']
    # Is_retweeted = result['retweeted']
    user_name = result['user']
    tweet_text = result['message']
    # <b>bold</b>
    # <i>italic</i>
    message = "منبع: توییتر" + "\n" \
                               "کاربر: " + str(user_name) + "\n" + \
              "تاریخ انتشار: " + date.strftime("%Y-%m-%d") + "\n" + \
              "زمان انتشار: " + date.strftime("%H:%M:%S") + "\n\n\n" + \
              str(tweet_link) + "\n\n"
    # str(tweet_text) + "\n\n\n" + \

    return message


def utc_to_local(utc_dt):
    utc = datetime.strptime(utc_dt, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return central


async def twitter_stream():
    uri = "ws://136.243.248.228:3232"
    while True:
        # last_tweet = None
        try:
            async with websockets.connect(uri) as websocket:
                logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
                print('Connected to {}'.format(uri))
                logging.info('Create Connection to {}'.format(uri))
                TOKEN = '1015275477:AAHlIojvnrU8GBXOu161pyMPYX3GjnuEPgU'
                Channel_UserName = '@atipardaz_posts'
                api_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}&parse_mode=HTML'
                while True:
                    if websocket.open:
                        try:
                            tweet = await websocket.recv()
                            tlg_message = ExtractFieldsMessage(tweet)
                            # print(tlg_message)
                            resp = req.get(api_url.format(TOKEN, Channel_UserName, tlg_message))
                            # if resp.status_code == 429:
                            #     print(resp.text)
                            #     time.sleep(30)
                            # print(resp.text)
                            # last_tweet = datetime.now()
                            logging.info('Send tweet.')
                        except Exception as err:
                            logging.error("Exception")
                            logging.error("Casuse: %s" % err)
                    else:
                        websocket = await websockets.connect(uri)
                    # if last_tweet and (datetime.now() - last_tweet).total_seconds() > 900:
                    #     await websocket.close()
                    #     os.system("sudo /etc/init.d/logstash stop")
                    #     time.sleep(5)
                    #     os.system("sudo /etc/init.d/logstash start")
                    #     time.sleep(10)
                    #     websocket = await websockets.connect(uri)
                    #     req.get(
                    #         url="http://login.qasedak-sms.ir/SMSInOutBox/SendSms?username=Atipardaz&password=22965&from=10000088960782&to=09378105380&text=twitter service stopped!")
                    #     continue
        except:
            os.system("sudo /etc/init.d/logstash stop")
            time.sleep(5)
            os.system("sudo /etc/init.d/logstash start")
            req.get(
                url="http://login.qasedak-sms.ir/SMSInOutBox/SendSms?username=Atipardaz&password=22965&from=10000088960782&to=09378105380&text=twitter service stopped!")
            time.sleep(500)
            continue


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(twitter_stream())
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    #
    # TOKEN = '1015275477:AAHlIojvnrU8GBXOu161pyMPYX3GjnuEPgU'
    # Channel_UserName = '@atipardaz_posts'
    # api_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}&parse_mode=HTML'
    #
    # ip = '0.0.0.0:3232'
    # ws = create_connection('ws://{}'.format(ip))
    # print('Connected to {}'.format(ip))
    # logging.info('Create Connection to {}'.format(ip))
    #
    # while True:
    #     try:
    #         tweet = ws.recv()
    #         logging.info(tweet)
    #
    #         tlg_message = ExtractFieldsMessage(tweet)
    #         print(tlg_message)
    #         resp = req.get(api_url.format(TOKEN, Channel_UserName, tlg_message))
    #         logging.info('Send tweet.')
    #     except Exception as err:
    #         logging.error("Exception")
    #         logging.error("Casuse: %s" % err)
    #
    # ws.close()
