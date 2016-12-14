from PyQt5.QtCore import QThread, pyqtSignal
import requests, json, random


class Queries(QThread):
    # the reason of different signal to broadcast is intend to if multiply feedback need to receive in future.
    rst_sent_items_to_main = pyqtSignal(dict)
    rst_sent_chars_to_main = pyqtSignal(dict)
    rst_sent_guild_to_main = pyqtSignal(dict)
    rst_sent_guild_detail = pyqtSignal(dict)
    rst_sent_chars_detail = pyqtSignal(dict)
    rst_sent_items_detail = pyqtSignal(dict)
    rst_sent_sets_info = pyqtSignal(dict)
    rst_sent_disco_info = pyqtSignal(dict)

    def __init__(self, query, q_type, parent=None):
        super(Queries, self).__init__(parent)
        self.query = query
        self.q_type = q_type
        self.rst = None
        self.headers = ["Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)",
                        "Mozilla/5.0 (compatible; U; ABrowse 0.6;  Syllable) AppleWebKit/420+ (KHTML, like Gecko)",
                        "Mozilla/5.0 (compatible; ABrowse 0.4; Syllable)",
                        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; .NET CLR 3.5.30729)",
                        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; .NET CLR   3.5.30729)",
                        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0;   Acoo Browser; GTB5; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;   SV1) ; InfoPath.1; .NET CLR 3.5.30729; .NET CLR 3.0.30618)",
                        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; Acoo Browser; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; Avant Browser)",
                        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1;   .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)"]
        print('{}: {}'.format(q_type, query))

    def query_item(self):
        while True:
            try:
                headers = {'User-Agent': random.choice(self.headers)}
                req = requests.get(self.query, timeout=12, headers=headers)
                self.rst = json.loads(req.text)
                return
            except BaseException as err:
                print('Query Error: ', err)
        self.rst = {}

    def run(self):
        self.query_item()
        if self.q_type == 'item':
            self.rst_sent_items_to_main.emit(self.rst)
        elif self.q_type == 'item_detail' or self.q_type == 'collection':
            self.rst_sent_items_detail.emit(self.rst)
        elif self.q_type == 'sets' or self.q_type == 'contains':
            self.rst_sent_sets_info.emit(self.rst)
        elif self.q_type == 'disco':
            self.rst_sent_disco_info.emit(self.rst)
        elif self.q_type == 'char':
            self.rst_sent_chars_to_main.emit(self.rst)
        elif self.q_type == 'guild':
            self.rst_sent_guild_to_main.emit(self.rst)
        elif self.q_type == 'char_detail':
            self.rst_sent_chars_detail.emit(self.rst)
        elif self.q_type == 'guild_detail':
            self.rst_sent_guild_detail.emit(self.rst)


