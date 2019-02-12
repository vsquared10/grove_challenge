import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import sys
from time import sleep

def get_NEO_data(start=None, end=None):
    if not start:
        start = datetime.strftime(datetime.now() - timedelta(days=7), '%Y-%m-%d')
    if not end:
        end = datetime.strftime(datetime.now(), '%Y-%m-%d')
    url = 'https://api.nasa.gov/neo/rest/v1/feed?start_date={}&end_date={}&api_key={}'
    resp = requests.get(url.format(start, end, my_key))
    if resp.status_code != 200:
        if resp.status_code == 429:
            retry_time = int(resp.headers['Retry-After'])
            print('Rate limit reached. Retrying again after {} seconds...'.format(retry_time))
            sleep(retry_time)
            d = get_NEO_data(start=start, end=end)
        else:
            print(resp.status_code, resp.json())
            print(resp.status_code, resp.json()['error_message'])
    d = resp.json()
    if d['element_count'] == 0:
        start = input('No data available, please enter a start date (YYYY-MM-DD): ')
        end = input('Enter an end date (YYYY-MM-DD): ')
        d = get_NEO_data(start=start, end=end)
    return d

def hazard_df_builder(data):
    neos = data['near_earth_objects']
    df = pd.DataFrame(columns=['id', 'close_approach_date', 'miles_from_earth', 'hazardous'])
    for day in neos.keys():
        for neo in neos[day]:
            close_approach = neo['close_approach_data'][0]['close_approach_date']
            row = {'id': neo['id'],
                   'close_approach_date': datetime.strptime(close_approach, '%Y-%m-%d'),
                   'miles_from_earth': float(neo['close_approach_data'][0]['miss_distance']['miles']),
                   'hazardous': neo['is_potentially_hazardous_asteroid']}
            df = df.append(row, ignore_index=True)
    return df[df.hazardous == True][['id', 'close_approach_date', 'miles_from_earth']]


def query_splitter(start, end):
    if not start and not end:
        return [{'s': None,'e': None}]
    duration = abs((start - end).days)
    print(str(duration) + ' total days.')
    if duration > 7:
        query_dates = []
        rounds = duration // 7
        remaining = duration % 7
        print(str(rounds) + ' queries made and one query with ', str(remaining) + ' days.')
        temp_s = start
        temp_e = temp_s + timedelta(days=7)
        for r in range(0, rounds):
            query_dates.append({'s': datetime.strftime(temp_s, '%Y-%m-%d'),
                                'e': datetime.strftime(temp_e, '%Y-%m-%d')})
            temp_s = temp_e
            temp_e = temp_e + timedelta(days=7)
        if remaining != 0:
            last = temp_s + timedelta(days=remaining)
            query_dates.append({'s': datetime.strftime(temp_s, '%Y-%m-%d'),
                                'e': datetime.strftime(last, '%Y-%m-%d')})
    else:
        query_dates = [{'s': datetime.strftime(start, '%Y-%m-%d'),
                        'e': datetime.strftime(end, '%Y-%m-%d')}]
    return query_dates


def etl_pipeline(start=None, end=None):
    if start is not None and end is not None:
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')
    queries = query_splitter(start, end)
    dfs = []
    for q in queries:
        chunk = get_NEO_data(start=q['s'], end=q['e'])
        dfs.append(hazard_df_builder(chunk))
    return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":
    my_key = os.environ.get('NASA_API_KEY')
    if my_key == None:
        print('please export a valid API key before running the script')
        sys.exit()
    filename = sys.argv[1]
    try:
        st = sys.argv[2]
    except IndexError:
        st = None
    try:
        ed = sys.argv[3]
    except IndexError:
        ed = None
    potentially_hazardous_asteroids = etl_pipeline(start=st, end=ed)
    potentially_hazardous_asteroids.drop_duplicates(inplace=True)
    potentially_hazardous_asteroids.to_csv(filename, index=False)
