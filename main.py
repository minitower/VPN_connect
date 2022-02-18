import requests
import sqlite3


class VPN_connect:

    def __init__(self):
        """
        Class for build new OpenVPN connect from free DB.
        Free VPN download from https://vpngate.net
        """
        self.vpn_db = sqlite3.connect('./data_storage/vpngate.db')
        pass

    def new_vpn_address(self, save=True):
        """
        Download new VPN addresses from https://vpngate.net
        :param save: bool, create tmp file with content of responce of not
        """
        req = requests.get('http://www.vpngate.net/api/iphone')
        con = req.content.decode('UTF-8')
        con = con.replace('*vpn_servers\r\n#', '')
        final_arr = []
        insert_str = []
        
        if save:
            with open('pars.csv', 'w') as f:
                f.write(con)
        
        con = con.split('\n')[1:-2]
        for i in con:
            val = i.split(',')
            #insert_str += '('+','.join(val)+'), '
        #self.vpn_db.execute(f'INSERT INTO vpngate_VALUES {insert_str}')
        
def main():
    vpn = VPN_connect()
    vpn.new_vpn_address()
        
if __name__ == '__main__':
    main()