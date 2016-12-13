from PyQt5.QtCore import QThread, pyqtSignal
import requests, json


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
        print('{}: {}'.format(q_type, query))

    def query_item(self):
        while True:
            try:
                req = requests.get(self.query, timeout=12)
                self.rst = json.loads(req.text)
                return
            except BaseException as err:
                print('Query Error: ', err)
        self.rst = {}

    def run(self):
        self.query_item()
        if self.q_type == 'item':
            self.rst_sent_items_to_main.emit(self.rst)
        elif self.q_type == 'item_detail':
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

