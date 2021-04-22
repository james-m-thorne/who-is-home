import subprocess
from datetime import datetime, timedelta


class HomeScanner:

    def __init__(self):
        self.ip = '192.168.1.1/24'
        self.devices = {
            'James': '7a:dc:cd:81:da:16',
            'Kristine': '9e:cc:99:75:6e:83',
            'Casey': '44:59:e3:72:5e:17',
            'Ayesha': '32:24:99:93:d4:cb',
            'Dinul': '22:22:70:87:50:ea',
        }
        self.data = []

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
            now = datetime.now()
            scanned_mac = self.scan()
            result = {}
            for person, mac in self.devices.items():
                if mac in scanned_mac:
                    result[person] = 1
                else:
                    result[person] = 0

            self.data.append({'time': now, 'result': result})
            self.data = self.data[-1000:]
            print(f'{now}: {result}')

    def get_whos_home(self, seconds):
        min_time = datetime.now() - timedelta(seconds=seconds)
        home_in_period = [point['result'] for point in self.data if point['time'] > min_time]
        result = {}
        for person in self.devices:
            result[person] = sum(item.get(person, 0) for item in home_in_period)
        return result

    def get_timeseries(self, name, seconds):
        min_time = datetime.now() - timedelta(seconds=seconds)
        timeseries = {str(point['time']): point.get('result', {}).get(name) for point in self.data if point['time'] > min_time}
        return timeseries
