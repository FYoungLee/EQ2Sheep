from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from datetime import datetime
import eq2s_func, eq2s_quary, eq2s_item, eq2s_aas, eq2s_char


class Eq2db_guildw(QDialog):
    def __init__(self, gid, parent=None):
        super(Eq2db_guildw, self).__init__(parent)
        guildLayoutAll = QVBoxLayout()
        self.setFixedSize(480, 400)
        self.guild_info_label = QLabel()
        self.guild_members_table = QTableWidget()
        self.guild_members_table.setColumnCount(5)
        self.guild_members_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.guild_members_table.setSelectionMode(QTableWidget.SingleSelection)
        self.guild_members_table.setHorizontalHeaderLabels(('Rank', 'Name', 'A_Class', 'Lv.', 'Join'))
        self.guild_members_table.itemClicked.connect(self.whenCharSelected)

        self.refreshBtn = QPushButton('Refresh')
        self.refreshBtn.setFixedWidth(100)
        self.refreshBtn.clicked.connect(self.sendGuildQueryToThread)

        guildLayoutAll.addWidget(self.refreshBtn)
        guildLayoutAll.addWidget(self.guild_info_label)
        guildLayoutAll.addWidget(self.guild_members_table)

        self.setLayout(guildLayoutAll)

        self.sendGuildQueryToThread(gid)

    def sendGuildQueryToThread(self, gid):
        self.refreshBtn.setEnabled(False)
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/guild'
        query1 = '?id={}'.format(gid)
        query2 = '&c:resolve=members(name,type,guild)'
        self.qy = eq2s_quary.Queries(url + query1 + query2, 'guild_detail')
        self.qy.rst_sent_guild_detail.connect(self.whenGuildInfoReceived)
        self.qy.start()

    def whenGuildInfoReceived(self, detail):
        try:
            self.guildDitail = detail['guild_list'][0]
            title = self.guildDitail['name']
            self.setWindowTitle(title)
        except KeyError or IndexError:
            QMessageBox().critical(self, 'Loading Error', 'Time out or Guild did not exists,\nTry to reload.')
            self.refreshBtn.setEnabled(True)
            return
        textInfo = '<font size="4">'

        textInfo += 'World : {}<br>'.format(self.guildDitail['world'])
        textInfo += 'Date Formed : {}<br>'.format(datetime.fromtimestamp(self.guildDitail['dateformed']).isoformat())
        textInfo += 'Accounts : {}<br>'.format(self.guildDitail['accounts'])
        textInfo += 'Guild Lv : {}<br>'.format(self.guildDitail['level'])
        textInfo += 'Guild XP : {}<br>'.format(self.guildDitail['guildxp'])

        textInfo += '</font>'
        self.guild_info_label.setText(textInfo)
        self.refreshBtn.setEnabled(True)
        self.displayMembers()

    def displayMembers(self):
        rank = {}
        for each in self.guildDitail['rank_list']:
            rank[each['id']] = each['name']

        mlist = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        for each in self.guildDitail['member_list']:
            m = {}
            if isinstance(each['name'], dict):
                m = {'name': each['name']['first']}
            elif isinstance(each['name'], str):
                m = {'name': each['name']}
            try:
                m['adclass'] = each['type']['class']
                m['adlv'] = each['type']['level']
                m['join'] = datetime.fromtimestamp(each['guild']['joined']).isoformat()
                m['id'] = each['id']
            except:
                pass
            if 'id' in m.keys():
                mlist[each['guild']['rank']].append(m)
            else:
                mlist[8].append(m)
        self.guild_members_table.setRowCount(len(self.guildDitail['member_list']))
        r = 0
        for e in range(8):
            for m in mlist[e]:
                try:
                    rankitem = QTableWidgetItem(rank[e])
                    rankitem.setTextAlignment(Qt.AlignCenter)
                    self.guild_members_table.setItem(r, 0, rankitem)
                    nmitem = QTableWidgetItem(m['name'])
                    nmitem.setTextAlignment(Qt.AlignCenter)
                    nmitem.setData(1000, m['id'])
                    nmitem.setToolTip('Click for character\'s detail')
                    self.guild_members_table.setItem(r, 1, nmitem)
                    if 'adclass' in m.keys():
                        adcls = QTableWidgetItem(m['adclass'])
                        adcls.setTextAlignment(Qt.AlignCenter)
                        self.guild_members_table.setItem(r, 2, adcls)
                        adlv = QTableWidgetItem(str(m['adlv']))
                        adlv.setTextAlignment(Qt.AlignCenter)
                        self.guild_members_table.setItem(r, 3, adlv)
                        jt = QTableWidgetItem(m['join'])
                        jt.setTextAlignment(Qt.AlignCenter)
                        self.guild_members_table.setItem(r, 4, jt)
                except:
                    pass
                r += 1
        self.guild_members_table.resizeColumnsToContents()

    def whenCharSelected(self, item):
        if item.data(1000):
            char_win = eq2s_char.Eq2db_charw(item.data(1000), self.parent())
            char_win.show()

