from VPN_tools.Insert_vpngate import VPN_connect
import pandas as pd
import sqlite3
import shlex
import subprocess as sp


def main():
    print('Start VPN_connect script...')
    vpn = VPN_connect()
    sql = sqlite3.connect('./VPN_tools/DataStorage/vpngate.db')
    df_info = pd.DataFrame(sql.execute('SELECT * FROM info').fetchall())
    need_update = True
    df_info.columns=['date', 'err']
    df_info = df_info.loc[df_info['err'] == 0]
    print(pd.Timestamp(df_info['date'].values[-1]))
    if pd.Timestamp(df_info['date'].values[-1])+ pd.Timedelta(days=1) <= pd.Timestamp.now():
        print('UPDATE')
        need_update = True
    if need_update:
       vpn.requestForNewIPAddresses()
       vpn.insertToSQLite()
    
    args=shlex.split('rm parse.csv')
    sp.Popen(args=args)


if __name__ == '__main__':
    main()