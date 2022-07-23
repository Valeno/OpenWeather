import requests
import json
import pandas as pd
from datetime import date, timedelta
from os.path import exists
import time

api_key = "api_key"
lat = ["33.426971", "32.7157", "34.0522"]
lon = ["-117.611992", "-117.1611", "-118.2437"]
city_name = ["san-clemente", "san-diego", "los-angeles"]    

def get_date(day):
    today = date.today()
    go_to = timedelta(days=day)
    the_date = today + go_to
    return the_date

unix_time = lambda x: time.mktime(x.timetuple())


def main():
    # Create the header for dataframe
    df_header = ['actual', 'actual_high', 'actual_low']
    for day in range(1, 8):
        df_header.append(f"day{day}_date")
        df_header.append(f"day{day}_high")
        df_header.append(f"day{day}_low")

    # Get required values from open weather map
    weather_dict = {}
    for idx, city in enumerate(city_name):
        hist_url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat[idx]}&lon={lon[idx]}&dt={int(unix_time(get_date(-1)))}&appid={api_key}&units=imperial"
        hist_url2 = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat[idx]}&lon={lon[idx]}&dt={int(unix_time(get_date(0)))}&appid={api_key}&units=imperial"
        hist_info, hist_info2 = requests.get(hist_url).text, requests.get(hist_url2).text
        data, data2 = json.loads(hist_info), json.loads(hist_info2)
        min_max = []
        # sorting yesterdays weather for PST
        for tmptr in data['hourly'][7:]:
            min_max.append(tmptr["temp"])
        for tmptr in data2['hourly'][:7]:
            min_max.append(tmptr['temp'])
        min_max = [get_date(-1).strftime("%Y-%m-%d"), max(min_max), min(min_max)]
        weather_dict.update({city: min_max})
 
    for idx, city in enumerate(city_name):
        daily_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat[idx]}&lon={lon[idx]}&exclude=minutely,hourly&appid={api_key}&units=imperial'
        page = requests.get(daily_url).text
        forecast = json.loads(page)
        daily_temp = []
        for idx, i in enumerate(forecast['daily'][1:], start=1):
            daily_temp.append(get_date(idx).strftime("%Y-%m-%d"))
            daily_temp.append(i['temp']['max'])
            daily_temp.append(i['temp']['min'])
        for i in range(0, len(daily_temp)):
            weather_dict[city].append(daily_temp[i])

    # Create DataFrame
    for city in city_name:
        df = pd.DataFrame(columns=df_header)   
        for idx, cols in enumerate(df_header):  # Place dictionary values into the columns created
            df.loc[0, cols] = weather_dict[city][idx]
        if exists(city + '.csv'):
            df.to_csv(f'{city}.csv', mode='a', index=False, header=False)
        else:    
            df.to_csv(f'{city}.csv', index=False)
        
if __name__ == '__main__':     
    main()
