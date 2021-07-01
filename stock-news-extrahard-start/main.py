import requests
import datetime as dt
import pandas as pd
import json
import smtplib

global today_str, yesterday_str

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
my_email = "Your_email"
password = "Your_ password"


# News parameters
def get_news():
    news_parameters = {
        "apiKey": "newsapi key",
        "q": COMPANY_NAME,
        "from": yesterday_str,
        "to": today_str,
        "sortBy": "popularity"
    }

    # Fetch data from the database
    data2 = requests.get("https://newsapi.org/v2/everything?", params=news_parameters)
    data2.raise_for_status()
    news_data = data2.json()

    dict1 = json.dumps(news_data).replace('"', '"')
    news = json.loads(dict1)

    articles = {
        "Stock": STOCK,
        "variation": variation_percentage,
        "Header1": news["articles"][0]["title"],
        "Description1": news["articles"][0]["description"],
        "Header2": news["articles"][1]["title"],
        "Description2": news["articles"][1]["description"],
        "Header3": news["articles"][2]["title"],
        "Description3": news["articles"][2]["description"]
    }

    return articles


# ----------------------------Getting the Stock DATA-------------------------------
# Returns if a day is a weekday
def is_business_day(date):
    return bool(len(pd.bdate_range(date, date)))


# Alphavantage parameters
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "datatype": "json",
    "apikey": "alphavantagekey"
}

# Fetch data from the database
data = requests.get("https://www.alphavantage.co/query?", params=stock_parameters)
data.raise_for_status()
stock_data = data.json()
#
stock_today = dt.datetime.today() - dt.timedelta(days=1)

is_workable = stock_today.weekday()

# Check if the today is monday and adjust the previous day to a weekday
if is_workable == 0:
    today = stock_today
    yesterday = stock_today - dt.timedelta(days=3)
    yesterday_str = str(yesterday)
    today_str = str(today)
elif is_workable < 5:
    today = stock_today
    yesterday = today - dt.timedelta(days=1)
    yesterday_str = str(yesterday)
    today_str = str(today)

# Getting closing prices from de database
today_closing_price = float(stock_data["Time Series (Daily)"][today_str[:10]]["4. close"])
yesterday_closing_price = float(stock_data["Time Series (Daily)"][yesterday_str[:10]]["4. close"])

# Calculating variation percentage from the previous prices
variation_percentage = ((yesterday_closing_price - today_closing_price) / today_closing_price) * 100

if abs(variation_percentage) >= 5:
    current_news = get_news()
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs="DestinationAddress",
            msg="Subject: Tesla Changes2\n\n"
                f"""Stock: {current_news['Stock']}\n
            variation: {current_news['variation']}\n
            {current_news['Header1']}\n
            {current_news['Description1']}\n
            {current_news['Header2']}\n
            {current_news['Description2']}\n
            {current_news['Header3']}\n
            {current_news['Description3']}\n""")
