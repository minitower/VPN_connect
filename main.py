import requests



class VPN_connect:

    def __init__(self):
        """
        Class for build new OpenVPN connect from free DB.
        Free VPN download from https://vpngate.net
        """
        pass

    def new_vpn_address(self, save=True):
        """
        Download new VPN addresses from https://vpngate.net
        :param save: bool, create tmp file with content of responce of not
        """
        req = requests.get('http://www.vpngate.net/api/iphone')
        con = req.content.decode('UTF-8')
        con = con.replace('*vpn_servers\r\n#', '')
        
        if save:
            with open('pars.csv', 'w') as f:
                f.write(con)
        