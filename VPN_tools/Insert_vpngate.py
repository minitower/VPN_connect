import requests
import sqlite3
import pandas as pd
import os
from base64 import b64decode


class VPN_connect:

    def __init__(self):
        """
        Class for build new OpenVPN connect from free DB.
        Free VPN download from https://vpngate.net
        """
        self.vpn_db = sqlite3.connect('VPN_tools/DataStorage/vpngate.db')
        self.last_update = self.vpn_db.execute('SELECT * FROM info')
        pass

    def requestForNewIPAddresses(self):
        """
        Import new list of IP for build OpenVPN connection
        """
        req = requests.get('http://www.vpngate.net/api/iphone')
        con = req.content.decode('UTF-8')
        con = con.replace('*vpn_servers\r\n#', '')
        
        with open('parse.csv', 'w') as f:
            f.write(con)
    
    def lastUpdate(self, datetime='now', err_code=0, insert=True):
        """
        Func for insert information of last update in vpngate.db Data Base
        
        Args:
            :param insert (type: bool): if True - insert new update result on vpngate.info table
            :param datetime (type: datetime.datetime OR pd.Timestamp OR datetime-like ):
                datetime of update. If "now" - write in DateTime field real-time.
            :param err_code (type: Int): in this version can be only 0 and 1 - if 0 then programm 
            update Data Base without Fatal Error. Else - Fatal Error found
        """
        self.df_update = pd.read_sql_query(
            'SELECT * FROM info', self.vpn_db)
        update_df = pd.DataFrame([[pd.Timestamp.now().replace(microsecond=0), 
                                    err_code]], columns=['DateTime', 'Update/error'])
        print(self.df_update)
        if insert:
            update_df.to_sql('info', self.vpn_db, index=False, if_exists='append')

    def openvpnFileCreator(self, message):
        """
        Func for decode and write message to file. 
        
        Args:
            message (type: str): message from vpngate csv file. 
                    Encode for base64
        
        Return:
            path (type: str): path of new file with config
        """
        pathes = [i for i in os.walk('./VPN_tools/DataStorage/openVPNConf')][-1][-1]
        tmp_arr = []
        for i in pathes:
            i.split('.')
            tmp_arr.append(int(i.split('.')[0]))
        tmp_arr.sort()
        path = f'VPN_tools/DataStorage/openVPNConf/{tmp_arr[-1]+1}.ovpn'
        with open(path, 'w+') as f:
            f.write(b64decode(message))
        return '/home/minitower/Desktop/projects/VPN_connect/'+path
    
    def insertToSQLite(self):
        """
        Func for create INSERT request for ./DataStorage/vpngate.db
        This Data Base will be used for connect to most relevant VPN server
        """
        df = pd.read_csv('parse.csv')
        df.columns = ['hostname', 'ip', 'score', 
                        'ping', 'speed', 'country_full', 
                        'country', 'n_session', 'uptime', 
                        'total_users', 'total_traffic', 
                        'log_type', 'operator', 'message', 
                        'path_to_ovpn']
        df = df[0:-1]
        df['message'] = ['NULL']*len(df)
        df = df.drop_duplicates(subset = 'ip')
        answer = input(f'{df}\n\n\nINSERT (UPDATE) ON vpngate DATABASE? (Y/n)')
        df.index = pd.RangeIndex(start=0, stop=len(df))
        if answer.lower == ['n', 'no']:
            self.lastUpdate(err_code=1)
            return 1
        else:
            df.to_sql('vpngate', self.vpn_db, index=False, if_exists='append')
            self.lastUpdate()
            print('Insert on "vpngate.vpngate" is sucsessfull!')
            return 0
            
        
        
