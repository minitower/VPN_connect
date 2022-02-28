import sqlite3
import pandas as pd
import subprocess as sp
import shlex

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
        self.sql = sqlite3.connect('./VPN_tools/DataStorage/vpngate.db')
        self.vpngate_df = pd.read_sql_query('SELECT * FROM vpngate', self.sql)
        self.sortby = sortby

    def findRelevantVPN(self):
        """
        Func for make decision about IP address for
        OpenVPN connect
        """
        self.vpngate_df = self.vpngate_df.sort_values(by='ping')
        self.ovpn_path = self.ovpn_path.iloc[0]['path_to_ovpn']
        
    def buildOvpnConnect():
        """
        Func for build connection from local machine
        to host IP address via OpenVPN protocol
        """
        self.args = shlex.split(f'sudo openvpn {self.ovpn_path}')
        self.proc = sp.Popen(args=self.args)

    def destroyOvpnConnect():
        """
        Func for terminate ovpn connection
        """
        self.proc.kill()
