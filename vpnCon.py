import pandas as pd
import os
import requests
from base64 import b64decode


class VPN_connect:

    def __init__(self, sortby=['ping']):
        """
        Class of VPN_connect script for establish
        connecton to VPN server from ./VPN_tools/
        DataStorage/vpngate.db

        Args:
            sortby (type: lst): column or columns which 
                will be maximised in decision vector
                Default: ping
        """
        self.sortby = sortby
        self.url_vpngate = 'http://www.vpngate.net/api/iphone' #csv table with VPN servers
        self.old_ip = requests.get('https://api.ipify.org').content.decode('UTF-8')
        if os.path.exists('parse.csv'):
            self.vpngate_df = pd.read_csv('parse.csv')
        else:
            self.vpngate_df = None

    def requestForNewIPAddresses(self, save=True):
        """
        Import new list of IP for build OpenVPN connection

        Args:
            save (type: bool): save csv table with response from 
                vpngate.net or not

        Return:
            pd.DataFrame with csv table from vpngate.net
        """
        req = requests.get(self.url_vpngate)
        con = req.content.decode('UTF-8')
        con = con.replace('*vpn_servers\r\n#', '').replace('*\r\n', '')
        con = con.split('\n')[:-1]
        parsed_arr = []
        for i in con:
            tmp = i.replace('\r', '')
            tmp = i.split(',')
            parsed_arr.append(tmp)

        self.vpngate_df = pd.DataFrame(parsed_arr)
        
        if save:
            self.vpngate_df.to_csv('parse.csv')
        
        return self.vpngate_df
    
    def decodeOVPNConfig(self, ovpn_b64):
        """
        Func for pd.apply on self.vpngate_df. Decode OpenVPN
        config from base64 hash and append new string to Data Frame

        Args:
            ovpn_b64 (type: string): ovpn config in base64 encoding  
        """
        return b64decode(ovpn_b64).decode('utf-8')
        
    
    def parseCSVTable(self, vpngate_df=None):
        """
        Func for parse CSV table from response of vpngate.net.
        Try to find self.vpngate_df, if can not - parse table from
        main.py provided

        Args:
            vpngate_df (type: pd.DataFrame, default: None):
            Used for situation, where self.vpngate did not found
        
        Return:
            pd.DataFrame with parsed data
        """
        if self.vpngate_df is None:
            self.vpngate_df = vpngate_df
        
        if list(self.vpngate_df[self.vpngate_df.columns[0]].values[0:10]) \
                        == [i for i in range(10)]:
            self.vpngate_df = self.vpngate_df.drop(self.vpngate_df.columns[0], axis=1)
        
        self.vpngate_df.columns = ['hostname', 'ip', 'score', 'ping', 'speed', 'country', 
                                    'cc', 'nSession', 'uptime', 'nUsers', 'totalTraffic', 
                                    'logType', 'operator', 'message', 'config']
        self.vpngate_df = self.vpngate_df.drop(0)
        self.vpngate_df = self.vpngate_df.reset_index(drop=True)
        self.vpngate_df['config'] = self.vpngate_df['config'].apply(self.decodeOVPNConfig)

        return self.vpngate_df


    def findRelevantVPN(self, vpngate_df=None):
        """
        Func for make decision about IP address for
        OpenVPN connect.

        Args:
            vpngate_df (type: pd.DataFrame, default: None):
            Used if self.vpngate_df = None. Provided by main.py 
        """
        if self.vpngate_df is None:
            self.vpngate_df = vpngate_df
        self.vpngate_df = self.vpngate_df.sort_values(by=self.sortby)
        self.vpngate_df = self.vpngate_df.reset_index(drop=True)
        self.ovpn_conf = self.vpngate_df.iloc[0]['config']
        self.ip_address = self.vpngate_df.iloc[0]['ip']
        self.cc = self.vpngate_df.iloc[0]['cc']
        self.speed = self.vpngate_df.iloc[0]['speed']
        print("Top five VPN server: \n", self.vpngate_df.head(5))
        return self.ovpn_conf, self.ip_address, self.cc, self.speed
 

    def buildOvpnConnect(self, ovpn_conf=None):
        """
        Func for build connection from local machine
        to host IP address via OpenVPN protocol.

        Args:
            ovpn_conf (type: str): string with Open VPN config of
                site in the top of list. Provide on main.py if 
                self.ovpn_conf is None
        """
        if self.ovpn_conf is None:
            if ovpn_conf is not None:
                self.ovpn_conf = ovpn_conf
            else:
                raise ValueError(f'Non of ovpn_conf file is not provided, '
                                    f'please, print one of this string')
        with open('tmp.ovpn', 'w+') as f:
                f.write(self.ovpn_conf)
        os.system(f'sudo openvpn tmp.ovpn')


    def checkVPNConnect(self):
        """
        Func for check IP address after buildOvpnConnect().
        If IP address is still old, then opvn did not work, else
        ovpn connect estamblished
        """
        self.new_ip = requests.get('https://api.ipify.org').content.decode('UTF-8')
        if self.new_ip == self.old_ip:
            print('IP addresses the same!')
            self.vpngate_df = self.vpngate_df.drop(self.vpngate_df.loc[
                                        self.vpngate_df['ip'] == self.ip_address].index)
            
            self.vpngate_df.to_csv('parse.csv')
            return 1
        else:
            print(f'Connection established! New IP address: {self.new_ip}')
            return 0
    

    def destroyOvpnConnection(self, ovpn_path, checker = True):
        """
        Func try request "pidstat" command, grep the result and 
        find pid of current open vpn connection, then build OS
        signal "SIGKILL"
        """
        os.system("pidstat | grep 'openvpn' | awk '{print $4}' >> log")
        with open('log', 'r') as f:
            pid = f.read().encode('utf8')
        pid = pid.replace('\n', '')
        os.system("sudo kill " + pid)
        
