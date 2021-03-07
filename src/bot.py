import re
import fbchat
import pandas as pd
import scapy.all as scapy

fbchat._util.USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36']
fbchat._state.FB_DTSG_REGEX = re.compile(r'"name":"fb_dtsg","value":"(.*?)"')


# Subclass fbchat.Client and override required methods
class HomeBot(fbchat.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ip = '192.168.1.1/24'
        self.devices = {
            'James': '7a:dc:cd:81:da:16',
            'Kristine': '9e:cc:99:75:6e:83',
            'Casey': '44:59:e3:72:5e:17',
            'Ayesha': '32:24:99:93:d4:cb',
            'Dinul': '22:22:70:87:50:ea',
            'Michael': '3a:15:0b:f2:44:1b',
            'Melly': '8e:3f:44:d4:6b:8d',
        }
        self.data = pd.DataFrame([], columns=list(self.devices.keys()))

    def scan(self):
        broadcast_ether_arp_req_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=self.ip)

        answered_list = scapy.srp(broadcast_ether_arp_req_frame, retry=10, timeout=1, verbose=False)[0]
        result = []
        for i in range(0, len(answered_list)):
            mac = answered_list[i][1].hwsrc
            result.append(mac)

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
            fbchat.log.info(f'{now}: {result}')

    def get_whos_home(self, minutes):
        now = pd.Timestamp.now(tz='NZ')
        home_in_period = self.data[self.data.index > (now - pd.Timedelta(minutes=minutes))].sum()
        return list(home_in_period[home_in_period > 0].index)

    def onMessage(self, **kwargs):
        thread_id = kwargs.get('thread_id')
        thread_type = kwargs.get('thread_type')
        message_object = kwargs.get('message_object')

        if thread_id not in ['2741121805903379', '100006948673842']:
            return

        if '!whoshome' in message_object.text.lower():
            fbchat.log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
            self.markAsDelivered(thread_id, message_object.uid)
            self.markAsRead(thread_id)
            self.reactToMessage(message_object.uid, fbchat.MessageReaction.YES)

            command = message_object.text.lower().split(' ')
            if len(command) == 2:
                minutes = int(command[1]) if command[1].isdigit() else 2
            else:
                minutes = 2

            people_home = self.get_whos_home(minutes)
            if len(people_home) > 1:
                people_home[-1] = 'and ' + people_home[-1]
            elif len(people_home) == 0:
                people_home.append('No one')

            self.send(
                fbchat.Message(text=f'{", ".join(people_home)} {"was" if len(people_home) <= 1 else "were"} home in the last {minutes} minutes.'),
                thread_id=thread_id,
                thread_type=thread_type
            )
