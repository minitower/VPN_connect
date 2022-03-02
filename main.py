from vpnCon import VPN_connect


def main(max_retry = 100):
    """
    Main function of VPN_connect script. Run
    for automate process of VPN connect

    Args:
        max_retry (type: int): number of trying
    connetion from host to VPN server
    """
    vpn = VPN_connect()
    vpn.requestForNewIPAddresses()
    vpn.parseCSVTable()
    ovpn_conf, ip_address, cc, speed = vpn.findRelevantVPN()
    vpn.buildOvpnConnect(ovpn_conf=ovpn_conf)
    check = vpn.checkVPNConnect()
    if check != 0:
        while check != 0:
            print('IP the same, retry')
            ovpn_conf, ip_address, cc, speed = vpn.findRelevantVPN()
            vpn.buildOvpnConnect(ovpn_conf=ovpn_conf)
            check = vpn.checkVPNConnect()
    if check == 0:
        print('Connection established sucsessfull!')
        print(f'Your IP: {ip_address}')
        print(f'Country: {cc}')
        print(f'Current speed: {speed}')

if __name__ == '__main__':
    main(max_retry=100)
