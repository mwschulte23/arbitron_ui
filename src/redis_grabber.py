import os
import json
import redis
import numpy as np
import pandas as pd
import datetime as dt
from urllib import parse

from src import SITES
#TODO needs optimization - will need a 'thinky' session on best solution

class RedisGrabber:
    def __init__(self):
        self.redis_url = parse.urlparse(os.getenv('REDISCLOUD_URL'))
        self.data = self.get_data()


    def __str__(self):
        return 'Arb Aggregator'


    def _current_arbs(self, data):
        grouper = lambda x: x.loc[(x['site1_last_updated'] == x['site1_last_updated'].max()) &
                                  (x['site2_last_updated'] == x['site2_last_updated'].max())]
        out_df = data.groupby(['side1', 'side2',
                               'side1_site', 'side2_site',
                               'start_time']).apply(grouper)
        out_df.drop_duplicates(keep='first', inplace=True)

        return out_df


    def get_data(self):
        r = redis.Redis(host=self.redis_url.hostname,
                         port=self.redis_url.port,
                         password=self.redis_url.password)
        # c_sites = ['MyBookie.ag', 'Bovada', 'GTbets', 'LowVig.ag', 'Betfair']

        row_list = []

        for key in r.keys('arb*'):
            data = json.loads(r.get(key))
            row_list.append(pd.DataFrame(data, index=[0]))

        data = self._current_arbs(pd.concat(row_list, axis=0, sort=False))
        data.index = np.arange(len(data))
        data.sort_values(by='start_time', ascending=False, inplace=True)
        # data = data.loc[data['side1_site'].isin(c_sites)]
        # data = data.loc[data['side2_site'].isin(c_sites)]

        return data


    def _to_moneyline(self, x):
        if x > 2:
            out = f'+{(x - 1) * 100:.0f}'
        elif x < 2 and x != 1:
            out = f'{-100 / (x - 1):.0f}'
        else:
            out = 'N/A'

        return out


    def formatted_output(self):
        time_thresh = dt.datetime.now() + dt.timedelta(hours=2)

        df = self.data[(pd.to_datetime(self.data['start_time']) > dt.datetime.now() - dt.timedelta(hours=12))]

        arb_list = []

        for _, row in df.iterrows():
            arb_dict = {}
            if pd.to_datetime(row['start_time']) < time_thresh and (row['side1_odds'] != 1 or row['side2_odds'] != 1):
                arb_dict['start_time'] = row['start_time']
                arb_dict['team1'] = row['side1']
                arb_dict['team2'] = row['side2']
                arb_dict['odds1'] = row['side1_odds']
                arb_dict['odds2'] = row['side2_odds']
                arb_dict['ml1'] = self._to_moneyline(row['side1_odds'])
                arb_dict['ml2'] = self._to_moneyline(row['side2_odds'])
                arb_dict['site1'] = row['side1_site']
                arb_dict['site2'] = row['side2_site']
                arb_dict['upside'] = f'{100 * (1 - row["comb_prob"]):.1f}%'
                arb_dict['site1_url'] = SITES[row['side1_site']]
                arb_dict['site2_url'] = SITES[row['side2_site']]
                arb_dict['site1_update'] = row['site1_last_updated']
                arb_dict['site2_update'] = row['site2_last_updated']
                arb_list.append(arb_dict)

        return arb_list