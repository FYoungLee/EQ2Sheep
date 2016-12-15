from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton, QTableWidget, \
    QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.Qt import QIcon
from datetime import datetime
import json
import eq2s_func, eq2s_quary, eq2s_char


class Eq2db_itemw(QDialog):
    def __init__(self, item_obj, parent=None):
        super(Eq2db_itemw, self).__init__(parent)
        # building item window
        self.qy = None
        self.item_detail = None
        self.item_detail_disco_info = list()
        self.setFixedWidth(420)
        self.setFixedHeight(720)
        layout = QVBoxLayout()
        self.item_name_label = QLabel()
        # background palette
        # pe = QPalette()
        # pe.setColor(QPalette.Window, Qt.black)
        # create name label
        self.item_name_label.setWordWrap(True)
        self.item_name_label.setAlignment(Qt.AlignCenter)
        # self.item_name_label.setPalette(pe)
        # self.item_name_label.setAutoFillBackground(True)
        # create icon label
        self.item_icon_label = QLabel()
        self.item_icon_label.setFixedSize(50, 50)
        self.item_detail_label = QTextBrowser()
        # buttons
        self.btn_layout = QHBoxLayout()

        self.sets_btn = QPushButton('Show Sets')
        self.sets_btn.setFixedWidth(100)
        self.sets_btn.setHidden(True)
        self.sets_btn.clicked.connect(self.send_sets_query_to_thread)

        self.contains_btn = QPushButton('Unpack Contains')
        self.contains_btn.setFixedWidth(100)
        self.contains_btn.setHidden(True)
        self.contains_btn.clicked.connect(self.send_contains_query_to_thread)

        self.dico_btn = QPushButton('Discover')
        self.dico_btn.setEnabled(False)
        self.dico_btn.setFixedWidth(100)
        self.dico_btn.clicked.connect(self.send_disco_query_to_thread)

        self.btn_layout.addWidget(self.sets_btn)
        self.btn_layout.addWidget(self.contains_btn)
        self.btn_layout.addSpacing(180)
        self.btn_layout.addWidget(self.dico_btn)
        # disco table create
        self.item_detail_disco = QTableWidget()
        self.item_detail_disco.setColumnCount(3)
        self.item_detail_disco.setFixedHeight(180)
        self.item_detail_disco.setHorizontalHeaderLabels(['Player', 'Server', 'Date'])
        self.item_detail_disco.setEditTriggers(QTableWidget.NoEditTriggers)
        self.item_detail_disco.setSelectionBehavior(QTableWidget.SelectRows)
        self.item_detail_disco.setSelectionMode(QTableWidget.SingleSelection)
        self.item_detail_disco.setHidden(True)
        self.item_detail_disco.itemClicked.connect(self.showCharWindow)
        # set background color
        # self.item_detail_label.setPalette(pe)
        # self.item_detail_label.setAutoFillBackground(True)
        # set text auto wrap
        # self.item_detail_label.setWordWrap(True)

        topLayout = QHBoxLayout()
        self.refreshBtn = QPushButton('Refresh')
        self.refreshBtn.setFixedWidth(100)
        self.refreshBtn.clicked.connect(self.sendItemQueryToThread)
        self.refreshBtn.setEnabled(False)
        self.favorBtn = QPushButton('Favor')
        self.favorBtn.setFixedWidth(100)
        self.favorBtn.clicked.connect(self.saveToFavor)
        self.favorBtn.setEnabled(False)
        topLayout.addWidget(self.refreshBtn)
        topLayout.addWidget(self.favorBtn)
        topLayout.addSpacing(300)

        upper_layout = QHBoxLayout()
        upper_layout.addWidget(self.item_name_label)
        upper_layout.addWidget(self.item_icon_label)

        layout.addLayout(topLayout)
        layout.addLayout(upper_layout)
        layout.addWidget(self.item_detail_label)
        layout.addLayout(self.btn_layout)
        layout.addWidget(self.item_detail_disco)
        self.setLayout(layout)
        # start query from census
        if isinstance(item_obj, int):
            self.itemid = item_obj
            self.sendItemQueryToThread()
        elif isinstance(item_obj, dict):
            self.cooked_info(item_obj)

    def sendItemQueryToThread(self):
        query = 'http://census.daybreakgames.com/s:fyang/get/eq2/item?id={}'.format(self.itemid)
        self.qy = eq2s_quary.Queries(query, 'item_detail')
        self.qy.rst_sent_items_detail.connect(self.cook_detail)
        self.qy.start()

    def cooked_info(self, item_obj):
        self.setWindowTitle('{} (Modified)'.format(item_obj['name']))
        self.item_detail_label.setText(item_obj['info'])
        pixicon = eq2s_func.get_pixmap_in_db(item_obj['iconid'])
        ticon = QIcon()
        ticon.addPixmap(pixicon)
        self.setWindowIcon(ticon)
        self.item_icon_label.setPixmap(pixicon)

    def cook_detail(self, detail):
        # window title
        try:
            self.item_detail = detail['item_list'][0]
            self.setWindowTitle(self.item_detail['displayname'])
        except (KeyError, IndexError) as err:
            QMessageBox().critical(self, 'Loading Error', 'Time out or Item did not exists.\nTry to reload again.\n{}'
                                   .format(err))
            self.refreshBtn.setEnabled(True)
            return
        # icon handle
        pixicon = eq2s_func.get_pixmap_in_db(self.item_detail['iconid'])
        ticon = QIcon()
        ticon.addPixmap(pixicon)
        self.setWindowIcon(ticon)
        self.item_icon_label.setPixmap(pixicon)
        # set item name header
        name = '<h2><b>{}</b></h2><br>'.format(self.item_detail['displayname'])
        self.item_name_label.setText(name)

        # info start cook
        textInfo = eq2s_func.CookItemText(self.item_detail)

        # set to label
        self.item_detail_label.setText(textInfo.text)

        # buttons contorl
        self.dico_btn.setEnabled(True)
        if textInfo.has_set:
            self.sets_btn.setHidden(False)
        if 'typeinfo' in self.item_detail.keys():
            if 'item_list' in self.item_detail['typeinfo'].keys():
                self.contains_btn.setHidden(False)
        self.favorBtn.setEnabled(True)
        self.refreshBtn.setEnabled(True)

    def send_sets_query_to_thread(self):
        self.sets_btn.setEnabled(False)
        sets_name = self.item_detail['setbonus_info']['displayname']
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/item'
        query = \
            '?setbonus_info.displayname={}&c:limit=20&c:show=displayname,leveltouse,iconid,tier,type,setbonus_info,slot_list'\
                .format(sets_name)
        self.qy = eq2s_quary.Queries(url+query, 'sets')
        self.qy.rst_sent_sets_info.connect(self.sets_sub_windows_build)
        self.qy.start()

    def sets_sub_windows_build(self, pieces):
        print('{} pieces found'.format(pieces['returned']))
        setswin = sets_table(pieces, self.parent())
        setswin.show()
        self.sets_btn.setEnabled(True)

    def send_contains_query_to_thread(self):
        self.contains_btn.setEnabled(False)
        item_list = [x['id'] for x in self.item_detail['typeinfo']['item_list']]
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/item'
        query = '?id={}'.format(','.join([str(x) for x in item_list]))
        self.qy = eq2s_quary.Queries(url + query, 'contains')
        self.qy.rst_sent_sets_info.connect(self.contains_sub_windows_build)
        self.qy.start()

    def contains_sub_windows_build(self, contains):
        containswin = contain_item_table(contains, self.parent())
        containswin.show()
        self.contains_btn.setEnabled(True)

    def send_disco_query_to_thread(self):
        self.dico_btn.setEnabled(False)
        try:
            disco_list = self.item_detail['_extended']['discovered']['world_list']
            query = 'http://census.daybreakgames.com/s:fyang/get/eq2/character?id='
            for each in disco_list:
                query += '{},'.format(each['charid'])
                self.item_detail_disco_info.append(
                    [each['charid'],
                     eq2s_func.worldid2name(each['id']),
                     datetime.fromtimestamp(each['timestamp']).isoformat().replace('T', ' ')])
            query = query[:-1] + '&c:show=name.first'
            self.qy = eq2s_quary.Queries(query, 'disco')
            self.qy.rst_sent_disco_info.connect(self.build_disco_info)
            self.qy.start()
        except KeyError as err:
            QMessageBox().warning(self, 'None', 'No one discovered.\n{}'.format(err))

    def build_disco_info(self, disco_list):
        self.item_detail_disco.setRowCount(len(self.item_detail_disco_info))
        charid2name = {}
        for each in disco_list['character_list']:
            charid2name[each['id']] = each['name']['first']
        for r, w in enumerate(self.item_detail_disco_info):
            o_player = QTableWidgetItem()
            try:
                o_player.setText(charid2name[w[0]])
                o_player.setData(1001, w[0])
            except KeyError:
                o_player.setText('Ninja Player')
            o_player.setTextAlignment(Qt.AlignCenter)
            o_server = QTableWidgetItem(w[1])
            o_server.setTextAlignment(Qt.AlignCenter)
            o_time = QTableWidgetItem(w[2])
            o_time.setTextAlignment(Qt.AlignCenter)
            self.item_detail_disco.setItem(r, 0, o_player)
            self.item_detail_disco.setItem(r, 1, o_server)
            self.item_detail_disco.setItem(r, 2, o_time)
        self.item_detail_disco.resizeColumnsToContents()
        self.dico_btn.setEnabled(True)
        self.item_detail_disco.setHidden(False)

    def showCharWindow(self, char):
        if char.data(1001) is not None:
            char_win = eq2s_char.Eq2db_charw(char.data(1001), self.parent())
            char_win.show()

    def saveToFavor(self):
        self.favorBtn.setEnabled(False)
        try:
            cur = {'name': self.item_detail['displayname'], 'id': self.item_detail['id'],
                   'level': self.item_detail['leveltouse'], 'slot': str(self.item_detail['slot_list']),
                   'type': self.item_detail['type'], 'tier': self.item_detail['tier']}
        except KeyError as err:
            QMessageBox().critical(self, 'Favor Error', 'Saving favorite failed:\n{}'.format(err))
            return
        try:
            with open('item_favor.json', 'r') as f:
                tp = json.loads(f.read())
                tp.append(cur)
        except:
            tp = [cur]
        with open('item_favor.json', 'w') as f:
            f.write(json.dumps(tp))

class sets_table(QDialog):
    def __init__(self, sets_obj, parent=None):
        super(sets_table, self).__init__(parent)
        self.setWindowTitle(sets_obj['item_list'][0]['setbonus_info']['displayname'])
        self.setFixedWidth(500)
        mainLaybel = QVBoxLayout()

        displayLabel = QLabel('<font size="5"><b>{} Found</b></font>'.format(sets_obj['returned']))

        self.setsTable = QTableWidget()
        self.setsTable.setColumnCount(6)
        self.setsTable.setRowCount(sets_obj['returned'])
        self.setsTable.setHorizontalHeaderLabels(['', 'Item Name', 'Lv.', 'Tier', 'Type', 'Slot'])
        self.setsTable.itemClicked.connect(self.display_selected_item)
        self.setsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.setsTable.setSelectionMode(QTableWidget.SingleSelection)
        self.fill_sets_table(sets_obj)

        mainLaybel.addWidget(displayLabel)
        mainLaybel.addWidget(self.setsTable)
        self.setLayout(mainLaybel)

    def fill_sets_table(self, sets_obj):
        try:
            for r, t in enumerate(sets_obj['item_list']):
                icon = QTableWidgetItem()
                ticon = QIcon()
                ticon.addPixmap(eq2s_func.get_pixmap_in_db(t['iconid']))
                icon.setIcon(ticon)
                nm = QTableWidgetItem(t['displayname'])
                nm.setTextAlignment(Qt.AlignCenter)
                nm.setData(1, str(t['id']))
                nm.setToolTip('Click for detail.')
                rlv = QTableWidgetItem(str(t['leveltouse']))
                rlv.setTextAlignment(Qt.AlignCenter)
                tier = QTableWidgetItem(t['tier'])
                tier.setTextAlignment(Qt.AlignCenter)
                tp = QTableWidgetItem(t['type'])
                tp.setTextAlignment(Qt.AlignCenter)
                slot_text = ''
                try:
                    for s in t['slot_list']:
                        slot_text += s['name']
                except KeyError:
                    pass
                slot = QTableWidgetItem(slot_text)
                slot.setTextAlignment(Qt.AlignCenter)
                self.setsTable.setItem(r, 0, icon)
                self.setsTable.setItem(r, 1, nm)
                self.setsTable.setItem(r, 2, rlv)
                self.setsTable.setItem(r, 3, tier)
                self.setsTable.setItem(r, 4, tp)
                self.setsTable.setItem(r, 5, slot)
            self.setsTable.resizeColumnsToContents()
        except BaseException as err:
            QMessageBox().critical(self, 'Result Error', 'Try again.\n{}'.format(err))
            return

    def display_selected_item(self, item):
        if item.data(1) is not None:
            item_win = Eq2db_itemw(item.data(1), self.parent())
            item_win.show()


class contain_item_table(QDialog):
    def __init__(self, contains_obj, parent=None):
        super(contain_item_table, self).__init__(parent)
        self.setWindowTitle('Contains List')
        self.setFixedWidth(500)
        mainLaybel = QVBoxLayout()

        displayLabel = QLabel('<font size="5"><b>{} Pieces</b></font>'.format(contains_obj['returned']))

        self.containsTable = QTableWidget()
        self.containsTable.setColumnCount(6)
        self.containsTable.setRowCount(contains_obj['returned'])
        self.containsTable.setHorizontalHeaderLabels(['', 'Item Name', 'Lv.', 'Tier', 'Type', 'Slot'])
        self.containsTable.itemClicked.connect(self.display_selected_item)
        self.containsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.containsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.containsTable.setSelectionMode(QTableWidget.SingleSelection)
        self.fill_contains_table(contains_obj)

        mainLaybel.addWidget(displayLabel)
        mainLaybel.addWidget(self.containsTable)
        self.setLayout(mainLaybel)

    def fill_contains_table(self, contains_obj):
        try:
            for r, t in enumerate(contains_obj['item_list']):
                icon = QTableWidgetItem()
                ticon = QIcon()
                ticon.addPixmap(eq2s_func.get_pixmap_in_db(t['iconid']))
                icon.setIcon(ticon)
                nm = QTableWidgetItem(t['displayname'])
                nm.setTextAlignment(Qt.AlignCenter)
                nm.setData(1, str(t['id']))
                nm.setToolTip('Click for detail.')
                rlv = QTableWidgetItem(str(t['leveltouse']))
                rlv.setTextAlignment(Qt.AlignCenter)
                tier = QTableWidgetItem(t['tier'])
                tier.setTextAlignment(Qt.AlignCenter)
                tp = QTableWidgetItem(t['type'])
                tp.setTextAlignment(Qt.AlignCenter)
                slot_text = ''
                try:
                    for s in t['slot_list']:
                        slot_text += s['name']
                except KeyError:
                    pass
                slot = QTableWidgetItem(slot_text)
                slot.setTextAlignment(Qt.AlignCenter)
                self.containsTable.setItem(r, 0, icon)
                self.containsTable.setItem(r, 1, nm)
                self.containsTable.setItem(r, 2, rlv)
                self.containsTable.setItem(r, 3, tier)
                self.containsTable.setItem(r, 4, tp)
                self.containsTable.setItem(r, 5, slot)
            self.containsTable.resizeColumnsToContents()
        except BaseException as err:
            QMessageBox().critical(self, 'Result Error', 'Try again.\n{}'.format(err))
            return

    def display_selected_item(self, item):
        if item.data(1) is not None:
            item_win = Eq2db_itemw(item.data(1), self.parent())
            item_win.show()