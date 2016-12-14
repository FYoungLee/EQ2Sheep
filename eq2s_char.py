from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QTableWidget, QLabel,\
    QTableWidgetItem, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.Qt import QIcon, QSize
from datetime import datetime
import json
import eq2s_func, eq2s_quary, eq2s_item, eq2s_aas, eq2s_guild


class Eq2db_charw(QDialog):
    def __init__(self, charpak, parent=None):
        super(Eq2db_charw, self).__init__(parent)
        self.setFixedHeight(490)
        self.qy = None
        # self.charID = charpak
        self.charDitail = None
        self.adornIDList = list()
        charLayoutAll = QVBoxLayout()
        charLayoutDisplay = QHBoxLayout()
        charLayoutBtn = QHBoxLayout()

        self.leftEquipTable = QTableWidget()
        self.leftEquipTable.setIconSize(QSize(24, 24))
        self.leftEquipTable.setColumnCount(2)
        self.leftEquipTable.setRowCount(12)
        self.leftEquipTable.setHorizontalHeaderLabels(['Name', 'Icon'])
        self.leftEquipTable.verticalHeader().setVisible(False)
        self.leftEquipTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.leftEquipTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.leftEquipTable.setSelectionMode(QTableWidget.SingleSelection)
        self.leftEquipTable.itemClicked.connect(self.display_selected_item)
        self.leftEquipTable.setFixedWidth(300)
        self.leftEquipTable.setColumnWidth(0, 266)
        self.leftEquipTable.setColumnWidth(1, 32)
        # self.leftEquipTable.setVerticalHeaderLabels(['Head', 'Chest', 'Shoulders', 'Forearms', 'Hands', 'Legs', 'Feet',
        #                                              'Charm', 'Charm', 'Food', 'Drink'])
        self.statusLabel = QTextBrowser()
        self.statusLabel.setFixedWidth(280)

        self.rightEquipTable = QTableWidget()
        self.rightEquipTable.setIconSize(QSize(24, 24))
        self.rightEquipTable.setColumnCount(2)
        self.rightEquipTable.setRowCount(12)
        self.rightEquipTable.setHorizontalHeaderLabels(['Icon', 'Name'])
        self.rightEquipTable.verticalHeader().setVisible(False)
        self.rightEquipTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rightEquipTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.rightEquipTable.setSelectionMode(QTableWidget.SingleSelection)
        self.rightEquipTable.itemClicked.connect(self.display_selected_item)
        self.rightEquipTable.setFixedWidth(300)
        self.rightEquipTable.setColumnWidth(0, 32)
        self.rightEquipTable.setColumnWidth(1, 265)
        # self.rightEquipTable.setVerticalHeaderLabels(['Cloak', 'Neck', 'Ear', 'Ear', 'Finger', 'Finger', 'Wrist', 'Wrist',
        #                                               'Waist', 'Primary', 'Secondary', 'Ranged', 'Ammo'])
        charLayoutDisplay.addWidget(self.leftEquipTable)
        charLayoutDisplay.addWidget(self.statusLabel)
        charLayoutDisplay.addWidget(self.rightEquipTable)

        self.guildBtn = QPushButton('Guild')
        self.guildBtn.setFixedWidth(100)
        self.guildBtn.clicked.connect(self.whenGuildBtnClicked)
        self.guildBtn.setEnabled(False)

        self.aaBtn = QPushButton(' AA ')
        self.aaBtn.setFixedWidth(100)
        self.aaBtn.clicked.connect(self.whenAABtnClicked)
        self.aaBtn.setEnabled(False)

        self.spellBtn = QPushButton('Spells')
        self.spellBtn.setFixedWidth(100)
        self.spellBtn.clicked.connect(self.whenSpellBtnClicked)
        self.spellBtn.setEnabled(False)

        self.achieveBtn = QPushButton('Achievenments')
        self.achieveBtn.setFixedWidth(100)
        self.achieveBtn.clicked.connect(self.whenAchieveBtnClicked)
        self.achieveBtn.setEnabled(False)

        charLayoutBtn.addWidget(self.aaBtn)
        charLayoutBtn.addWidget(self.spellBtn)
        charLayoutBtn.addWidget(self.achieveBtn)
        charLayoutBtn.addWidget(self.guildBtn)

        topLayout = QHBoxLayout()
        self.refreshBtn = QPushButton('Refresh')
        self.refreshBtn.setFixedWidth(100)
        self.refreshBtn.clicked.connect(self.sendCharQueryToThread)
        self.refreshBtn.setEnabled(False)
        self.favorBtn = QPushButton('Favor')
        self.favorBtn.setFixedWidth(100)
        self.favorBtn.clicked.connect(self.saveToFavor)
        self.favorBtn.setEnabled(False)
        topLayout.addWidget(self.refreshBtn)
        topLayout.addWidget(self.favorBtn)

        charLayoutAll.addLayout(topLayout)
        charLayoutAll.addLayout(charLayoutDisplay)
        charLayoutAll.addLayout(charLayoutBtn)

        self.setLayout(charLayoutAll)
        self.id = charpak
        self.sendCharQueryToThread()

    def sendCharQueryToThread(self):
        self.refreshBtn.setEnabled(False)
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/character'
        query1 = '?id={}'.format(self.id)
        query2 = '&c:resolve=equipmentslots'
        self.qy = eq2s_quary.Queries(url + query1 + query2, 'char_detail')
        self.qy.rst_sent_chars_detail.connect(self.whenCharInfoReceived)
        self.qy.start()

    def whenCharInfoReceived(self, detail):
        try:
            self.charDitail = detail['character_list'][0]
            title = self.charDitail['displayname']
            if 'guild' in self.charDitail.keys():
                title += ' Guild : {}'.format(self.charDitail['guild']['name'])
                self.guildBtn.setEnabled(True)
            self.setWindowTitle(title)
        except KeyError or IndexError:
            QMessageBox().critical(self, 'Loading Error', 'Time out or Character did not exists,\nTry to reload.')
            self.refreshBtn.setEnabled(True)
            return
        textInfo = eq2s_func.CookCharText(self.charDitail)
        self.statusLabel.setText(textInfo.text)
        self.displayCharEquipment()
        try:
            if len(self.charDitail['alternateadvancements']['alternateadvancement_list']) == 0:
                self.aaBtn.setEnabled(False)
            else:
                self.aaBtn.setEnabled(True)
        except KeyError:
            self.aaBtn.setEnabled(False)
        self.refreshBtn.setEnabled(True)
        self.spellBtn.setEnabled(True)
        self.achieveBtn.setEnabled(True)
        self.favorBtn.setEnabled(True)

    def displayCharEquipment(self):
        self.adornCollect(self.charDitail['equipmentslot_list'])
        for each in self.charDitail['equipmentslot_list']:
            if 'item' in each.keys():
                pos = eq2s_func.slot2position(each['id'])
                self.fillEachPieceOfEquip(each, pos[0], pos[1])

    def fillEachPieceOfEquip(self, equip, side, pos):
        tooltip = eq2s_func.CookItemText(equip['item'])
        try:
            epnm = QTableWidgetItem(equip['item']['displayname'])
            epnm.setToolTip(tooltip.text)
            epnm.setData(1001, equip['item']['iconid'])
            epnm.setData(1002, equip['item']['displayname'])
            if side == 'l':
                epnm.setTextAlignment(Qt.AlignRight)
            else:
                epnm.setTextAlignment(Qt.AlignLeft)
            epicon = QTableWidgetItem()
            icon = QIcon()
            icon.addPixmap(eq2s_func.get_pixmap_in_db(equip['item']['iconid']))
            epicon.setIcon(icon)
            epicon.setToolTip(tooltip.text)
            epicon.setData(1001, equip['item']['iconid'])
            epicon.setData(1002, equip['item']['displayname'])
            if side == 'l':
                self.leftEquipTable.setItem(pos, 0, epnm)
                self.leftEquipTable.setItem(pos, 1, epicon)
            elif side == 'r':
                self.rightEquipTable.setItem(pos, 0, epicon)
                self.rightEquipTable.setItem(pos, 1, epnm)
        except KeyError:
            pass

    def display_selected_item(self, item_info):
        cooked_info = {'name': item_info.data(1002), 'info': item_info.toolTip(), 'iconid': item_info.data(1001)}
        item_win = eq2s_item.Eq2db_itemw(cooked_info, self.parent())
        item_win.show()

    def whenAABtnClicked(self):
        aapaket = {'current': self.charDitail['alternateadvancements']['alternateadvancement_list']}
        try:
            for each in self.charDitail['orderedalternateadvancement_list']:
                aapaket[each['profilename']] = each['alternateadvancement_list']
        except KeyError:
            pass
        aas = eq2s_aas.Eq2db_aas(aapaket, self)
        aas.show()

    def whenSpellBtnClicked(self):
        self.spellBtn.setEnabled(False)
        query = 'http://census.daybreakgames.com/s:fyang/get/eq2/character?id='
        query += str(self.charDitail['id'])
        query += '&c:resolve=spells&c:show=spell_list'
        self.qy = eq2s_quary.Queries(query, 'char_detail')
        self.qy.rst_sent_chars_detail.connect(self.spellsReceived)
        self.qy.start()

    def whenAchieveBtnClicked(self):
        self.achieveBtn.setEnabled(False)
        query = 'http://census.daybreakgames.com/s:fyang/get/eq2/character?id='
        query += str(self.charDitail['id'])
        query += '&c:resolve=achievements&c:show=achievements'
        self.qy = eq2s_quary.Queries(query, 'char_detail')
        self.qy.rst_sent_chars_detail.connect(self.achievementReceived)
        self.qy.start()

    def whenGuildBtnClicked(self):
        guild_win = eq2s_guild.Eq2db_guildw(self.charDitail['guild']['id'], self.parent())
        guild_win.show()

    def adornCollect(self, eqpLst):
        # I need a list those keys contain all of this character's adornments and slot id information
        aid = {}
        for eachitem in eqpLst:
            if 'item' in eachitem.keys() and 'adornment_list' in eachitem['item'].keys():
                for eachadorn in eachitem['item']['adornment_list']:
                    if 'id' in eachadorn.keys():
                        # first one is adornment's id which the index is 0
                        # second one is the id that adorn attached to which the index is 1
                        self.adornIDList.append([eachadorn['id'], eachitem['id']])
                        aid[eachadorn['id']] = 1
        if len(aid):
            query = 'http://census.daybreakgames.com/s:fyang/get/eq2/item?id='
            for each in aid.keys():
                query += '{},'.format(each)
            query = query[:-1] + '&c:show=displayname,modifiers,effect_list'
            self.qy = eq2s_quary.Queries(query, 'item_detail')
            self.qy.rst_sent_items_detail.connect(self.adornInfoReceived)
            self.qy.start()

    def adornInfoReceived(self, adorn_info):
        aid2info = {}
        for each in adorn_info['item_list']:
            text = eq2s_func.CookItemText(each, short=True).text
            text = '{}<br>{}'.format(each['displayname'], text)
            aid2info[each['id']] = text
            # print(each['id'], '\n', text, '\n')
        for each in self.adornIDList:
            # get the table position of each adornment
            tablePos = eq2s_func.slot2position(each[1])
            # attach adorn text into each table item
            try:
                if tablePos[0] == 'l':
                    t = self.leftEquipTable.item(tablePos[1], 0).toolTip()
                    t += '<br>{}'.format(aid2info[each[0]])
                    self.leftEquipTable.item(tablePos[1], 0).setToolTip(t)
                    self.leftEquipTable.item(tablePos[1], 1).setToolTip(t)
                elif tablePos[0] == 'r':
                    t = self.rightEquipTable.item(tablePos[1], 0).toolTip()
                    t += '<br>{}'.format(aid2info[each[0]])
                    self.rightEquipTable.item(tablePos[1], 0).setToolTip(t)
                    self.rightEquipTable.item(tablePos[1], 1).setToolTip(t)
            except AttributeError:
                badPosition = QTableWidgetItem('Missing Item from DBG Databases')
                badPosition.setTextAlignment(Qt.AlignCenter)
                badPosition.setToolTip(aid2info[each[0]])
                if tablePos[0] == 'l':
                    self.leftEquipTable.setItem(tablePos[1], 0, badPosition)
                elif tablePos[0] == 'r':
                    self.rightEquipTable.setItem(tablePos[1], 1, badPosition)

    def spellsReceived(self, spell_info):
        try:
            raw_spells = spell_info['character_list'][0]['spell_list']
        except KeyError or TypeError:
            QMessageBox().warning(self, 'Loading Error', 'Time out or Data did not exists\nTry again.')
            self.spellBtn.setEnabled(True)
            return

        splw = Eq2db_char_spellsw(raw_spells, self.charDitail['displayname'], self)
        splw.show()
        self.spellBtn.setEnabled(True)

    def achievementReceived(self, achieve_info):
        try:
            raw_achs = achieve_info['character_list'][0]['achievements']
        except KeyError or TypeError:
            QMessageBox().warning(self, 'Loading Error', 'Time out or Data did not exists\nTry again.')
            self.achieveBtn.setEnabled(True)
            return

        splw = Eq2db_char_achievew(raw_achs, self.charDitail['displayname'], self)
        splw.show()
        self.achieveBtn.setEnabled(True)

    def saveToFavor(self):
        self.favorBtn.setEnabled(False)
        try:
            cur = {'name': self.charDitail['displayname'], 'id': self.charDitail['id'],
                   'level': self.charDitail['type']['level'], 'class': self.charDitail['type']['class']}
        except KeyError as err:
            QMessageBox().critical(self, 'Favor Error', 'Saving favorite failed:\n{}'.format(err))
            return
        try:
            with open('char_favor.json', 'r') as f:
                tp = json.loads(f.read())
                tp.append(cur)
        except:
            tp = [cur]
        with open('char_favor.json', 'w') as f:
            f.write(json.dumps(tp))


class Eq2db_char_spellsw(QDialog):
    def __init__(self, raw_spells, char_name, parent=None):
        super(Eq2db_char_spellsw, self).__init__(parent)
        self.setWindowTitle('{} Spells'.format(char_name))
        self.setFixedSize(800, 500)
        splLayout = QHBoxLayout()
        self.spellsTable = QTableWidget()
        self.spellsTable.setColumnCount(5)
        self.spellsTable.setHorizontalHeaderLabels(('Level', 'Name', 'Tier', 'Type', 'Given By'))
        self.spellsTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.spellsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.spellsTable.setSelectionMode(QTableWidget.SingleSelection)
        self.spellsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        splLayout.addWidget(self.spellsTable)
        self.setLayout(splLayout)

        self.spells = self.filterSpells(raw_spells)
        self.fillTable()

    def filterSpells(self, raw_spells):
        # using dict to filter same spell in different level, keep the highest one
        desc = {}
        for each in raw_spells:
            if each['given_by'] in ('tradeskillclass', 'alternateadvancement'):
                continue
            # when failed on mapping description as a key then use name instead.
            # some spells have none description.
            if isinstance(each['description'], dict):
                desc[each['name']] = each
                continue
            if each['description'] in desc.keys() and desc[each['description']]['level'] > each['level']:
                continue
            else:
                desc[each['description']] = each
        self.spellsTable.setRowCount(len(desc))
        # making a level ordered spell dict using level as a key
        leveled_spells = {}
        for each in desc:
            if desc[each]['level'] not in leveled_spells.keys():
                leveled_spells[desc[each]['level']] = []
            leveled_spells[desc[each]['level']].append(desc[each])

        return leveled_spells

    def fillTable(self):
        levelrange = tuple(self.spells.keys())
        r = 0
        for level in sorted(levelrange):
            for spell in self.spells[level]:
                lvitem = QTableWidgetItem(str(spell['level']))
                lvitem.setTextAlignment(Qt.AlignCenter)
                self.spellsTable.setItem(r, 0, lvitem)
                nmitem = QTableWidgetItem(spell['name'])
                nmitem.setTextAlignment(Qt.AlignCenter)
                try:
                    ticon = QIcon()
                    ticon.addPixmap(eq2s_func.get_pixmap_in_db(spell['icon']['id'], 'spellicons'))
                    nmitem.setIcon(ticon)
                except:
                    pass
                dtxt = eq2s_func.CookSpellText(spell)
                nmitem.setToolTip(dtxt)
                self.spellsTable.setItem(r, 1, nmitem)
                tieritem = QTableWidgetItem(spell['tier_name'])
                tieritem.setTextAlignment(Qt.AlignCenter)
                self.spellsTable.setItem(r, 2, tieritem)
                typeitem = QTableWidgetItem(spell['type'].capitalize())
                typeitem.setTextAlignment(Qt.AlignCenter)
                self.spellsTable.setItem(r, 3, typeitem)
                gbitem = QTableWidgetItem(spell['given_by'].capitalize())
                gbitem.setTextAlignment(Qt.AlignCenter)
                self.spellsTable.setItem(r, 4, gbitem)
                r += 1
        self.spellsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.spellsTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.spellsTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.spellsTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)


class Eq2db_char_achievew(QDialog):
    def __init__(self, raw_achs, char_name, parent=None):
        super(Eq2db_char_achievew, self).__init__(parent)
        self.setWindowTitle('{} Achievements'.format(char_name))
        self.setFixedSize(700, 500)
        achLayout = QVBoxLayout()
        achLabel = QLabel()
        labeltxt = 'Total Points: {}<br>Total Counts: {}<br>Completed: {}<br>Points: {}<br>'.format(
            raw_achs['total_points'], raw_achs['total_count'], raw_achs['completed'], raw_achs['points']
        )
        achLabel.setText(labeltxt)
        self.achTable = QTableWidget()
        self.achTable.setColumnCount(5)
        self.achTable.setHorizontalHeaderLabels(('Completed', 'Name', 'Pts', 'Type', 'Category'))
        self.achTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.achTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.achTable.setSelectionMode(QTableWidget.SingleSelection)
        self.achTable.setRowCount(len(raw_achs['achievement_list']))
        self.achTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        achLayout.addWidget(achLabel)
        achLayout.addWidget(self.achTable)
        self.setLayout(achLayout)

        self.fillAchTable(raw_achs['achievement_list'])

    def fillAchTable(self, achs):
        tm = []
        untm = []
        tm_achs = {}
        for each in achs:
            if each['completed_timestamp']:
                tm.append(each['completed_timestamp'])
                tm_achs[each['completed_timestamp']] = each
            else:
                untm.append(each)
        r = 0
        for each in sorted(tm, reverse=True):
            ct = QTableWidgetItem(datetime.fromtimestamp(each).isoformat().replace('T', ' '))
            ct.setTextAlignment(Qt.AlignCenter)
            self.achTable.setItem(r, 0, ct)
            nm = QTableWidgetItem(tm_achs[each]['name'])
            nm.setTextAlignment(Qt.AlignCenter)
            nm.setToolTip(tm_achs[each]['desc'])
            self.achTable.setItem(r, 1, nm)
            pts = QTableWidgetItem(str(tm_achs[each]['points']))
            pts.setTextAlignment(Qt.AlignCenter)
            self.achTable.setItem(r, 2, pts)
            tp = QTableWidgetItem(tm_achs[each]['category'])
            tp.setTextAlignment(Qt.AlignCenter)
            self.achTable.setItem(r, 3, tp)
            cate = QTableWidgetItem(tm_achs[each]['subcategory'])
            cate.setTextAlignment(Qt.AlignCenter)
            self.achTable.setItem(r, 4, cate)
            r += 1

        for each in untm:
            try:
                ct = QTableWidgetItem('Uncompleted')
                ct.setTextAlignment(Qt.AlignCenter)
                self.achTable.setItem(r, 0, ct)
                nm = QTableWidgetItem(each['name'])
                nm.setTextAlignment(Qt.AlignCenter)
                nm.setToolTip(each['desc'])
                self.achTable.setItem(r, 1, nm)
                pts = QTableWidgetItem(str(each['points']))
                pts.setTextAlignment(Qt.AlignCenter)
                self.achTable.setItem(r, 2, pts)
                tp = QTableWidgetItem(each['category'])
                tp.setTextAlignment(Qt.AlignCenter)
                self.achTable.setItem(r, 3, tp)
                cate = QTableWidgetItem(each['subcategory'])
                cate.setTextAlignment(Qt.AlignCenter)
                self.achTable.setItem(r, 4, cate)
            except KeyError:
                pass
            r += 1
        self.achTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.achTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.achTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.achTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

class Eq2db_char_collection(QDialog):
    def __init__(self, col, parent=None):
        super(Eq2db_char_collection, self).__init__(parent)