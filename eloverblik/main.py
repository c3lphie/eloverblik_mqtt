import requests
import schedule
import pytz

import paho.mqtt.publish as publish

from subscription import Subscription
from tarif import Tarif
from eloverblik import ElOverblik

import time
import tomllib
import sys
from pprint import pprint
from datetime import datetime


def load_conf(path):
    with open(path, "rb") as f:
        return tomllib.load(f)

config = load_conf(sys.argv[1])
final_prices = []

el_overblik = ElOverblik(token=config["general"]["eloverblik_token"])
el_overblik.get_meteringpointids()


def fetch_prices():
    global final_prices

    chargedata = el_overblik.get_chargedata()
    
    tarif_sums = [0]*24
    sub_sum = 0
    
    for tarif in chargedata[0]["tariffs"]:
        pprint(tarif)
        prices = tarif.price_pr_hour()
        for i, x in enumerate(prices):
            tarif_sums[i] += x["price"]
            
    for subscription in chargedata[0]["subscription"]:
        sub_sum += subscription.price_pr_hour()
               
    now = datetime.now()
             
    spot_pris = f"https://www.elprisenligenu.dk/api/v1/prices/{now.year}/{now.month:02}-{now.day:02}_{config["general"]["price_class"]}.json"
             
    elpris = requests.get(spot_pris).json()
    elpris = [
        {
            "start": datetime.fromisoformat(x["time_start"]),
            "end": datetime.fromisoformat(x["time_end"]),
            "price": x["DKK_per_kWh"],
        }
        for x in elpris
    ]

             
    elpris.sort(key=lambda x: x["start"])
             
    final_prices = []
    for i in range(len(elpris)):
        final_prices.append(
            {
                "start": elpris[i]["start"],
                "end": elpris[i]["end"],
                "price": round((elpris[i]["price"] + tarif_sums[i] + sub_sum) * 1.25, 3),
            }
        )

def print_prices():
    tz = pytz.timezone(config["general"]["timezone"])
    now = datetime.now()
    now = now.astimezone(tz)
    print(now)
    for x in final_prices:
        print(x["start"], x["end"], x["price"])

def print_current_price():
    now = datetime.now()
    now = now.astimezone(pytz.timezone(config["general"]["timezone"]))
    for x in final_prices:
        if x["start"] <= now and now <= x["end"]:
            pprint(x["price"])
            break


def publish_current_price(topic):
    now = datetime.now()
    now = now.astimezone(pytz.timezone(config["general"]["timezone"]))
    for x in final_prices:
        if x["start"] <= now and now <= x["end"]:
            publish.single(topic, x["price"],
                           retain=True, hostname=config["mqtt"]["server"])
            break




def main():
    fetch_prices()
    schedule.every().day.at("23:59", config["general"]["timezone"]).do(el_overblik.get_data_token)
    schedule.every().day.at("00:00", config["general"]["timezone"]).do(fetch_prices)
    schedule.every().minute.do(print_current_price)
    schedule.every().minute.do(publish_current_price, topic=config["mqtt"]["topic"])
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
