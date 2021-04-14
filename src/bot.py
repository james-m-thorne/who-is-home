import subprocess
import pandas as pd


# Subclass fbchat.Client and override required methods
class HomeBot:

    def __init__(self):
        self.ip = '192.168.1.1/24'
        self.devices = {
            'James': '7a:dc:cd:81:da:16',
            'Kristine': '9e:cc:99:75:6e:83',
            'Casey': '44:59:e3:72:5e:17',
            'Ayesha': '32:24:99:93:d4:cb',
            'Dinul': '22:22:70:87:50:ea',
        }
        self.data = pd.DataFrame([], columns=list(self.devices.keys()))

    def scan(self):
        result = []
        try:
            answered_list = subprocess.check_output("sudo arp-scan -lx --retry=6", shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        except:
            return result
        for answer in answered_list.split('\n'):
            try:
                mac = answer.split('\t')[1]
                result.append(mac)
            except IndexError:
                continue

        return result

    def collect_whos_home(self):
        while True:
            now = pd.Timestamp.now(tz='NZ')
            scanned_mac = self.scan()
            result = {}
            for person, mac in self.devices.items():
                if mac in scanned_mac:
                    result[person] = 1
                else:
                    result[person] = 0

            self.data = pd.concat([self.data, pd.DataFrame(result, index=[now])])
            self.data = self.data[-1000:]
            print(f'{now}: {result}')

    def get_whos_home(self, seconds):
        now = pd.Timestamp.now(tz='NZ')
        home_in_period = self.data[self.data.index > (now - pd.Timedelta(seconds=seconds))].sum()
        return home_in_period.to_dict()

    def get_timeseries(self, name, seconds):
        now = pd.Timestamp.now(tz='NZ')
        timeseries = self.data.loc[self.data.index > (now - pd.Timedelta(seconds=seconds)), name].to_dict()
        timeseries = {str(key): value for key, value in timeseries.items()}
        print(timeseries)
        return timeseries