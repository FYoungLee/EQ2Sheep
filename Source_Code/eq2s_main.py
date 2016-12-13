from PyQt5.QtWidgets import QWidget, QTabWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, \
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.Qt import QIcon, QSize
from datetime import datetime
import eq2s_func, eq2s_quary, eq2s_item, eq2s_char, eq2s_guild


class EQ2DB_MainW(QWidget):
    def __init__(self, parent=None):
        super(EQ2DB_MainW, self).__init__(parent)
        # connect to icons sql db
        # set main window info and size
        self.qy = None
        self.setWindowTitle('EQII Sheep    V0.618  by: Fyoung')
        self.setFixedSize(750, 700)
        # create main tab object
        self.mainTabWidget = QTabWidget()
        self.add_item_tab_content()
        self.add_char_tab_content()
        self.add_guild_tab_content()

        # combine sub_tabs together
        self.mainTabWidget.addTab(self.itemWidget, ' ITEMS ')
        self.mainTabWidget.addTab(self.charWidget, 'CHARACTERS')
        self.mainTabWidget.addTab(self.guildWidget, ' GUILDS ')
        self.mainTabWidget.tabBarClicked.connect(self.adjust_win_size)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.mainTabWidget)

        self.setLayout(self.mainLayout)

        self.show()

    def add_guild_tab_content(self):
        self.guildWidget = QWidget()
        self.guildLayout = QVBoxLayout()
        self.add_guild_tab_piece()
        self.guildWidget.setLayout(self.guildLayout)

    def add_guild_tab_piece(self):
        with open('Chars.txt', 'r') as f:
            server_options = f.read().split('&')[-1]

        guild_1st_row_layout = QHBoxLayout()
        # name
        self.guild_name_input = QLineEdit()
        guild_1st_row_layout.addWidget(self.guild_name_input)
        guild_1st_row_layout.addWidget(QLabel('Name'))
        guild_1st_row_layout.addSpacing(30)
        # world
        self.guild_world_combox = QComboBox()
        for e in server_options.split(','):
            self.guild_world_combox.addItem(e)
        guild_1st_row_layout.addWidget(self.guild_world_combox)
        guild_1st_row_layout.addWidget(QLabel('Server'))
        guild_1st_row_layout.addSpacing(30)
        guild_1st_row_layout.addSpacing(200)

        guild_2nd_row_layout = QHBoxLayout()
        # guild level
        self.guild_level_min_line = QLineEdit()
        self.guild_level_min_line.setFixedWidth(40)
        guild_2nd_row_layout.addWidget(self.guild_level_min_line)
        guild_2nd_row_layout.addWidget(QLabel('-'))
        self.guild_level_max_line = QLineEdit()
        self.guild_level_max_line.setFixedWidth(40)
        guild_2nd_row_layout.addWidget(self.guild_level_max_line)
        guild_2nd_row_layout.addWidget(QLabel('Guild Level'))
        guild_2nd_row_layout.addSpacing(40)

        # accounts
        self.guild_account_min_line = QLineEdit()
        self.guild_account_min_line.setFixedWidth(40)
        guild_2nd_row_layout.addWidget(self.guild_account_min_line)
        guild_2nd_row_layout.addWidget(QLabel('-'))
        self.guild_account_max_line = QLineEdit()
        self.guild_account_max_line.setFixedWidth(40)
        guild_2nd_row_layout.addWidget(self.guild_account_max_line)
        guild_2nd_row_layout.addWidget(QLabel('Accounts'))

        self.guild_find_btn = QPushButton(' Find ')
        self.guild_find_btn.setFixedWidth(100)
        self.guild_find_btn.clicked.connect(self.send_guild_query_to_thread)

        # guild table view
        self.guildTableView = QTableWidget()
        self.guildTableView.setColumnCount(4)
        self.guildTableView.setHorizontalHeaderLabels(['Name', 'Server', 'Lv', 'Accounts'])
        self.guildTableView.itemClicked.connect(self.display_selected_guild)
        self.guildTableView.setEditTriggers(QTableWidget.NoEditTriggers)
        self.guildTableView.setSortingEnabled(True)
        self.guildTableView.setSelectionBehavior(QTableWidget.SelectRows)
        self.guildTableView.setSelectionMode(QTableWidget.SingleSelection)

        # put all things together
        self.guildLayout.addLayout(guild_1st_row_layout)
        self.guildLayout.addLayout(guild_2nd_row_layout)
        self.guildLayout.addWidget(self.guild_find_btn)
        self.guildLayout.addWidget(self.guildTableView)

    def send_guild_query_to_thread(self):
        self.guild_find_btn.setEnabled(False)
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/guild?'
        cmd = ''
        if self.guild_name_input.text() is not '':
            cmd += 'name_lower=^{}'.format(self.guild_name_input.text().lower())
        if self.guild_world_combox.currentText() is not '':
            cmd += '&world={}'.format(self.guild_world_combox.currentText())
        if self.guild_level_min_line.text() is not '':
            cmd += '&level=]{}'.format(self.guild_level_min_line.text())
        if self.guild_level_max_line.text() is not '':
            cmd += '&level=[{}'.format(self.guild_level_max_line.text())
        if self.guild_account_min_line.text() is not '':
            cmd += '&accounts=]{}'.format(self.guild_account_min_line.text())
        if self.guild_account_max_line.text() is not '':
            cmd += '&level=[{}'.format(self.guild_account_max_line.text())

        cmd += '&c:show=name,world,level,accounts&c:limit=1000'

        self.qy = eq2s_quary.Queries(url + cmd, 'guild')
        self.qy.rst_sent_guild_to_main.connect(self.guild_result_received)
        self.qy.start()

    def guild_result_received(self, rst):
        try:
            rows = len(rst['guild_list'])
            # display the result into table
            if rows == 0:
                QMessageBox().warning(self, 'None', 'Nothing found.')
                self.char_find_btn.setEnabled(True)
                return
        except KeyError:
            QMessageBox().warning(self, 'None', 'Nothing found.')
            self.char_find_btn.setEnabled(True)
            return
        self.guildTableView.setRowCount(rows)
        try:
            for r, t in enumerate(rst['guild_list']):
                nm = QTableWidgetItem()
                nm.setTextAlignment(Qt.AlignCenter)
                nm.setData(1000, 'guild')
                nm.setData(1001, t['id'])
                nm.setText(t['name'])
                nm.setToolTip('Click for guild\'s detail.')
                world = QTableWidgetItem(t['world'])
                world.setTextAlignment(Qt.AlignCenter)
                lv = QTableWidgetItem(str(t['level']))
                lv.setTextAlignment(Qt.AlignCenter)
                acc = QTableWidgetItem(str(t['accounts']))
                acc.setTextAlignment(Qt.AlignCenter)
                self.guildTableView.setItem(r, 0, nm)
                self.guildTableView.setItem(r, 1, world)
                self.guildTableView.setItem(r, 2, lv)
                self.guildTableView.setItem(r, 3, acc)
            self.guildTableView.resizeColumnsToContents()
        except BaseException as err:
            QMessageBox().critical(self, 'Result Error', 'Try again.\n{}'.format(err))
            self.guild_find_btn.setEnabled(True)
            return
        self.guild_find_btn.setEnabled(True)


    def display_selected_guild(self, guild):
        if guild.data(1000) == 'guild':
            guild_win = eq2s_guild.Eq2db_guildw(guild.data(1001), self)
            guild_win.show()

    def add_char_tab_content(self):
        self.charWidget = QWidget()
        self.charLayout = QVBoxLayout()
        self.add_char_tab_piece()
        self.charWidget.setLayout(self.charLayout)

    def add_char_tab_piece(self):
        with open('Chars.txt', 'r') as f:
            sub_options = f.read().split('&')
        # build character option area
        char_1st_row_layout = QHBoxLayout()
        # name
        self.char_name_input = QLineEdit()
        char_1st_row_layout.addWidget(self.char_name_input)
        char_1st_row_layout.addWidget(QLabel('Name'))
        char_1st_row_layout.addSpacing(30)
        # world
        self.char_world_combox = QComboBox()
        for e in sub_options[2].split(','):
            self.char_world_combox.addItem(e)
        char_1st_row_layout.addWidget(self.char_world_combox)
        char_1st_row_layout.addWidget(QLabel('Server'))
        char_1st_row_layout.addSpacing(30)
        char_1st_row_layout.addSpacing(200)
        # # guild
        # self.char_guild_line = QLineEdit()
        # char_1st_row_layout.addWidget(self.char_guild_line)
        # char_1st_row_layout.addWidget(QLabel('Guild'))
        
        char_2nd_row_layout = QHBoxLayout()
        # class
        self.char_class_min_line = QLineEdit()
        self.char_class_min_line.setFixedWidth(40)
        char_2nd_row_layout.addWidget(self.char_class_min_line)
        char_2nd_row_layout.addWidget(QLabel('-'))
        self.char_class_max_line = QLineEdit()
        self.char_class_max_line.setFixedWidth(40)
        char_2nd_row_layout.addWidget(self.char_class_max_line)
        char_2nd_row_layout.addWidget(QLabel('Lv.'))
        self.char_class_combox = QComboBox()
        for e in sub_options[0].split(','):
            self.char_class_combox.addItem(e)
        char_2nd_row_layout.addWidget(self.char_class_combox)
        char_2nd_row_layout.addWidget(QLabel('Adventure Class'))
        char_2nd_row_layout.addSpacing(40)
        # trade class
        self.char_trade_class_min_line = QLineEdit()
        self.char_trade_class_min_line.setFixedWidth(40)
        char_2nd_row_layout.addWidget(self.char_trade_class_min_line)
        char_2nd_row_layout.addWidget(QLabel('-'))
        self.char_trade_class_max_line = QLineEdit()
        self.char_trade_class_max_line.setFixedWidth(40)
        char_2nd_row_layout.addWidget(self.char_trade_class_max_line)
        char_2nd_row_layout.addWidget(QLabel('Lv.'))
        self.char_trade_class_combox = QComboBox()
        for e in sub_options[1].split(','):
            self.char_trade_class_combox.addItem(e.capitalize())
        char_2nd_row_layout.addWidget(self.char_trade_class_combox)
        char_2nd_row_layout.addWidget(QLabel('Tradeskill Class'))

        self.char_find_btn = QPushButton(' Find ')
        self.char_find_btn.setFixedWidth(100)
        self.char_find_btn.clicked.connect(self.send_char_query_to_thread)

        # char table view
        self.charTableView = QTableWidget()
        self.charTableView.setColumnCount(6)
        self.charTableView.setHorizontalHeaderLabels(['Name', 'Adv.Class', 'Lv', 'Trade.Class', 'Lv', 'Guild'])
        self.charTableView.itemClicked.connect(self.display_selected_char)
        self.charTableView.setEditTriggers(QTableWidget.NoEditTriggers)
        self.charTableView.setSortingEnabled(True)
        self.charTableView.setSelectionBehavior(QTableWidget.SelectRows)
        self.charTableView.setSelectionMode(QTableWidget.SingleSelection)

        # put all things together
        self.charLayout.addLayout(char_1st_row_layout)
        self.charLayout.addLayout(char_2nd_row_layout)
        self.charLayout.addWidget(self.char_find_btn)
        self.charLayout.addWidget(self.charTableView)

    def send_char_query_to_thread(self):
        self.char_find_btn.setEnabled(False)
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/character?'
        cmd = ''
        if self.char_name_input.text() is not '':
            cmd += 'name.first_lower=^{}'.format(self.char_name_input.text().lower())
        if self.char_world_combox.currentText() is not '':
            cmd += '&locationdata.world={}'.format(self.char_world_combox.currentText())
        if self.char_class_min_line.text() is not '':
            cmd += '&type.level=]{}'.format(self.char_class_min_line.text())
        if self.char_class_max_line.text() is not '':
            cmd += '&type.level=[{}'.format(self.char_class_max_line.text())
        if self.char_class_combox.currentText() is not '':
            cmd += '&type.class={}'.format(self.char_class_combox.currentText())
        if self.char_trade_class_min_line.text() is not '':
            cmd += '&type.ts_level=]{}'.format(self.char_trade_class_min_line.text())
        if self.char_trade_class_max_line.text() is not '':
            cmd += '&type.ts_level=[{}'.format(self.char_trade_class_max_line.text())
        if self.char_trade_class_combox.currentText() is not '':
            cmd += '&type.ts_class={}'.format(self.char_trade_class_combox.currentText().lower())

        cmd += '&c:show=displayname,type.class,type.level,type.ts_class,type.ts_level,guild.name,guild.id&c:limit=1000'

        self.qy = eq2s_quary.Queries(url + cmd, 'char')
        self.qy.rst_sent_chars_to_main.connect(self.char_result_received)
        self.qy.start()

    def char_result_received(self, rst):
        try:
            rows = len(rst['character_list'])
            # display the result into table
            if rows == 0:
                QMessageBox().warning(self, 'None', 'Nothing found.')
                self.char_find_btn.setEnabled(True)
                return
        except KeyError:
            QMessageBox().warning(self, 'None', 'Nothing found.')
            self.char_find_btn.setEnabled(True)
            return
        self.charTableView.setRowCount(rows)
        try:
            for r, t in enumerate(rst['character_list']):
                nm = QTableWidgetItem()
                nm.setTextAlignment(Qt.AlignCenter)
                nm.setData(1000, 'name')
                nm.setData(1001, t['id'])
                nm.setText(t['displayname'])
                nm.setToolTip('Click for character\'s detail.')
                cls = QTableWidgetItem(t['type']['class'])
                cls.setTextAlignment(Qt.AlignCenter)
                cls_ad_lv = QTableWidgetItem(str(t['type']['level']))
                cls_ad_lv.setTextAlignment(Qt.AlignCenter)
                tscls = QTableWidgetItem()
                tscls.setTextAlignment(Qt.AlignCenter)
                cls_ts_lv = QTableWidgetItem()
                cls_ts_lv.setTextAlignment(Qt.AlignCenter)
                try:
                    tscls.setText(t['type']['ts_class'].capitalize())
                    cls_ts_lv.setText(str(t['type']['ts_level']))
                except:
                    pass
                gnm = QTableWidgetItem()
                gnm.setTextAlignment(Qt.AlignCenter)
                try:
                    gnm.setData(1000, 'guild')
                    gnm.setData(1001, t['guild']['id'])
                    gnm.setText(t['guild']['name'])
                    gnm.setToolTip('Click for guild detail')
                except:
                    pass
                self.charTableView.setItem(r, 0, nm)
                self.charTableView.setItem(r, 1, cls)
                self.charTableView.setItem(r, 2, cls_ad_lv)
                self.charTableView.setItem(r, 3, tscls)
                self.charTableView.setItem(r, 4, cls_ts_lv)
                self.charTableView.setItem(r, 5, gnm)
            self.charTableView.resizeColumnsToContents()
        except BaseException as err:
            QMessageBox().critical(self, 'Result Error', 'Try again.\n{}'.format(err))
            self.char_find_btn.setEnabled(True)
            return
        self.char_find_btn.setEnabled(True)

    def display_selected_char(self, char):
        if char.data(1000) == 'name':
            char_win = eq2s_char.Eq2db_charw(char.data(1001), self)
            char_win.show()
        elif char.data(1000) == 'guild':
            guild_win = eq2s_guild.Eq2db_guildw(char.data(1001), self)
            guild_win.show()

    def add_item_tab_content(self):
        self.itemWidget = QWidget()
        self.itemlayout = QVBoxLayout()
        self.add_item_tab_piece()
        self.itemWidget.setLayout(self.itemlayout)

    def add_item_tab_piece(self):
        with open('Items.txt', 'r') as f:
            sub_options = f.read().split('\n')
        # build item option area
        item_option_layout = QVBoxLayout()
        # name
        item_name_layout = QHBoxLayout()
        self.item_name_input = QLineEdit()
        item_name_layout.addWidget(self.item_name_input)
        item_name_layout.addWidget(QLabel('Item Name'))
        # status
        statusLayout = QHBoxLayout()
        self.statusCombox = QComboBox()
        self.statusCombox.addItem('')
        self.statusDict = eq2s_func.aquire_modifiers()
        for e in self.statusDict.keys():
            self.statusCombox.addItem(e)
        self.statusCompare = QComboBox()
        self.statusCompare.setFixedWidth(40)
        self.statusCompare.addItem('>')
        self.statusCompare.addItem('=')
        self.statusCompare.addItem('<')
        self.statusValue = QLineEdit()
        self.statusValue.setFixedWidth(40)
        self.statusBtn = QPushButton('Add')
        self.statusBtn.clicked.connect(self.build_status_queries)
        self.statusBtn.setFixedWidth(100)
        self.statusBtn_del = QPushButton('Del')
        self.statusBtn_del.clicked.connect(self.del_last_status_query)
        self.statusBtn_del.setFixedWidth(100)
        statusLayout.addWidget(self.statusCombox)
        statusLayout.addWidget(self.statusCompare)
        statusLayout.addWidget(self.statusValue)
        statusLayout.addWidget(self.statusBtn)
        statusLayout.addWidget(self.statusBtn_del)
        statusLayout.addWidget(QLabel('Status Edit'))

        self.statusLine = QLineEdit()
        self.statusLine.setDisabled(True)
        allStatusLayout = QVBoxLayout()
        allStatusLayout.addLayout(statusLayout)
        allStatusLayout.addWidget(self.statusLine)
        # level requirement
        item_level_layout = QHBoxLayout()
        self.item_level_require_line_min = QLineEdit()
        self.item_level_require_line_min.setFixedWidth(50)
        item_level_layout.addWidget(self.item_level_require_line_min)
        toLabel1 = QLabel('-')
        toLabel1.setFixedWidth(10)
        item_level_layout.addWidget(toLabel1)
        self.item_level_require_line_max = QLineEdit()
        self.item_level_require_line_max.setFixedWidth(50)
        item_level_layout.addWidget(self.item_level_require_line_max)
        item_level_layout.addWidget(QLabel('Character Level Requirement'))
        item_level_layout.addSpacing(200)
        # level
        self.item_level_min_line = QLineEdit()
        self.item_level_min_line.setFixedWidth(50)
        self.item_level_max_line = QLineEdit()
        self.item_level_max_line.setFixedWidth(50)
        item_level_layout.addWidget(self.item_level_min_line)
        toLabel2 = QLabel('-')
        toLabel2.setFixedWidth(10)
        item_level_layout.addWidget(toLabel2)
        item_level_layout.addWidget(self.item_level_max_line)
        item_level_layout.addWidget(QLabel('Item Level'))

        # tier
        item_tier_type_layout = QHBoxLayout()
        self.item_tier_combox = QComboBox()
        self.item_tier_combox.setFixedWidth(160)
        for e in sub_options[0].split(','):
            self.item_tier_combox.addItem(e)
        item_tier_type_layout.addWidget(self.item_tier_combox)
        item_tier_type_layout.addWidget(QLabel('Tier'))
        item_tier_type_layout.addSpacing(234)

        # type
        self.item_type_combox = QComboBox()
        self.item_type_combox.setFixedWidth(160)
        self.item_type_sub_combox = QComboBox()
        for e in sub_options[1].split(','):
            self.item_type_combox.addItem(e.capitalize())
        item_tier_type_layout.addWidget(self.item_type_combox)
        item_tier_type_layout.addWidget(QLabel('Item Type'))

        # class
        classLayout = QHBoxLayout()
        self.classCombox = QComboBox()
        self.classCombox.setFixedWidth(160)
        for e in sub_options[2].split(','):
            self.classCombox.addItem(e)
        classLayout.addWidget(self.classCombox)
        classLayout.addWidget(QLabel('Classes'))
        classLayout.addSpacing(233)
        # slot
        self.slotCombox = QComboBox()
        self.slotCombox.setFixedWidth(160)
        for e in sub_options[4].split(','):
            self.slotCombox.addItem(e)
        classLayout.addWidget(self.slotCombox)
        classLayout.addWidget(QLabel('Slot'))

        # adornment
        adornLayout = QHBoxLayout()
        self.adornCombox = QComboBox()
        self.adornCombox.setFixedWidth(160)
        for e in ['', 'blue', 'cyan', 'green', 'purple', 'red', 'white', 'yellow']:
            self.adornCombox.addItem(e.capitalize())
        adornLayout.addWidget(self.adornCombox)
        adornLayout.addWidget(QLabel('Adornment Slot'))
        # effect
        adornLayout.addSpacing(230)
        self.effectLine = QLineEdit()
        self.effectLine.setFixedWidth(160)
        effectLabel = QLabel('Effect Name')
        adornLayout.addWidget(self.effectLine)
        adornLayout.addWidget(effectLabel)
        # flag
        item_flag_layout = QVBoxLayout()
        item_flag_layout.addWidget(QLabel('Item Flag'))
        self.item_flags = []
        item_flag_sub_layout = QGridLayout()
        r, c = 0, 0
        for e in sub_options[3].split(','):
            flag = QCheckBox(e.capitalize())
            flag.setObjectName(e)
            item_flag_sub_layout.addWidget(flag, r, c)
            if c < 5:
                c += 1
            else:
                c = 0
                r += 1
            self.item_flags.append(flag)
        item_flag_layout.addLayout(item_flag_sub_layout)

        # discovery time
        discoLayout = QHBoxLayout()
        discoLayout.addWidget(QLabel('Discovery Time: (yyyy-mm-dd) '))
        self.discoStartDate = QLineEdit()
        self.discoStartDate.setFixedWidth(100)
        self.discoEndDate = QLineEdit()
        self.discoEndDate.setFixedWidth(100)
        discoLayout.addWidget(self.discoStartDate)
        toLabel3 = QLabel('between')
        toLabel3.setFixedWidth(45)
        discoLayout.addWidget(toLabel3)
        discoLayout.addWidget(self.discoEndDate)
        discoLayout.addSpacing(330)
        # build find button
        find_btn_layout = QHBoxLayout()
        self.item_find_btn = QPushButton('Find')
        self.item_find_btn.clicked.connect(self.send_item_query_to_thread)
        find_btn_layout.addSpacing(700)
        find_btn_layout.addWidget(self.item_find_btn)
        # combine item option pieces together
        item_option_layout.addLayout(item_name_layout)
        item_option_layout.addLayout(allStatusLayout)
        item_option_layout.addLayout(item_level_layout)
        item_option_layout.addLayout(item_tier_type_layout)
        item_option_layout.addLayout(classLayout)
        item_option_layout.addLayout(adornLayout)
        item_option_layout.addLayout(item_flag_layout)
        item_option_layout.addLayout(discoLayout)
        item_option_layout.addLayout(find_btn_layout)

        # build search result area
        item_result_layout = QVBoxLayout()
        self.item_result_table = QTableWidget()
        self.item_result_table.setIconSize(QSize(24, 24))
        self.item_result_table.setColumnCount(6)
        self.item_result_table.setHorizontalHeaderLabels(['', 'Item Name', 'Lv.', 'Tier', 'Type', 'Slot'])
        self.item_result_table.itemClicked.connect(self.display_selected_item)
        self.item_result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.item_result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.item_result_table.setSelectionMode(QTableWidget.SingleSelection)
        self.item_result_table.setSortingEnabled(True)
        item_result_layout.addWidget(self.item_result_table)

        self.itemlayout.addLayout(item_option_layout)
        self.itemlayout.addLayout(item_result_layout)

    def send_item_query_to_thread(self):
        self.item_find_btn.setEnabled(False)
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/item?'
        # logic for making query
        cmd = ''
        if self.item_name_input.text() is not '':
            cmd += 'displayname_lower=*{}'.format(self.item_name_input.text().lower().strip())
        if self.statusLine.text() is not '':
            cmd += self.cook_status_query()
        if self.item_level_require_line_min.text() is not '':
            cmd += '&leveltouse=]{}'.format(self.item_level_require_line_min.text())
        if self.item_level_require_line_max.text() is not '':
            cmd += '&leveltouse=[{}'.format(self.item_level_require_line_max.text())
        if self.item_level_min_line.text() is not '':
            cmd += '&itemlevel=]{}'.format(self.item_level_min_line.text())
        if self.item_level_max_line.text() is not '':
            cmd += '&itemlevel=[{}'.format(self.item_level_min_line.text())
        if self.item_tier_combox.currentText() is not '':
            cmd += '&tier={}'.format(self.item_tier_combox.currentText())
        if self.item_type_combox.currentText() is not '':
            t = self.item_type_combox.currentText().lower().split(' ')[-1]
            if t == '*':
                cmd += '&type=Item'
            else:
                cmd += '&typeinfo.name={}'.format(t)
        if self.classCombox.currentText() is not '':
            cmd += '&c:has=typeinfo.classes.{}'.format(self.classCombox.currentText().lower())
        if self.slotCombox.currentText() is not '':
            cmd += '&slot_list.name={}'.format(self.slotCombox.currentText())
        if self.adornCombox.currentText() is not '':
            cmd += '&adornmentslot_list.color={}'.format(self.adornCombox.currentText())
        if self.effectLine.text() is not '':
            cmd += '&adornment_list.name=*{}&c:case=false'.format(self.effectLine.text())
        for e in self.item_flags:
            if e.isChecked():
                cmd += '&flags.{}.value=1'.format(e.objectName())
        if self.discoStartDate.text() is not '':
            try:
                stamp = datetime.strptime(self.discoStartDate.text(), '%Y-%m-%d').timestamp()
                cmd += '&_extended.discovered.timestamp=]{}'.format(stamp)
            except BaseException:
                QMessageBox().critical(self, 'Date error', 'Bad date input, check again.')
                self.item_find_btn.setEnabled(True)
                return
        if self.discoEndDate.text() is not '':
            try:
                stamp = datetime.strptime(self.discoEndDate.text(), '%Y-%m-%d').timestamp()
                cmd += '&_extended.discovered.timestamp=[{}'.format(stamp)
            except BaseException:
                QMessageBox().critical(self, 'Date error', 'Bad date input, check again.')
                self.item_find_btn.setEnabled(True)
                return

        cmd += '&c:limit=10000&c:show=type,displayname,leveltouse,iconid,tier,slot_list'
        self.qy = eq2s_quary.Queries(url+cmd, 'item')
        self.qy.rst_sent_items_to_main.connect(self.item_result_received)
        self.qy.start()

    def item_result_received(self, rst):
        try:
            rows = len(rst['item_list'])
            # display the result into table
            if rows == 0:
                QMessageBox().warning(self, 'Loading Error', 'Time out or Data did not exists\nTry again.')
                self.item_find_btn.setEnabled(True)
                return
        except KeyError:
            QMessageBox().warning(self, 'Loading Error', 'Time out or Data did not exists\nTry again.')
            self.item_find_btn.setEnabled(True)
            return
        # set the table rows
        self.item_result_table.setRowCount(rows)
        # connect the table items to a function

        try:
            for r, t in enumerate(rst['item_list']):
                icon = QTableWidgetItem()
                ticon = QIcon()
                ticon.addPixmap(eq2s_func.get_pixmap_in_db(t['iconid']))
                icon.setIcon(ticon)
                nm = QTableWidgetItem(t['displayname'])
                nm.setTextAlignment(Qt.AlignCenter)
                nm.setData(1001, t['id'])
                nm.setToolTip('Click for detail.')
                rlv = QTableWidgetItem(t['leveltouse'])
                rlv.setTextAlignment(Qt.AlignCenter)
                tier = QTableWidgetItem(t['tier'])
                tier.setTextAlignment(Qt.AlignCenter)
                tp = QTableWidgetItem(t['type'])
                tp.setTextAlignment(Qt.AlignCenter)
                slot_text = ''
                try:
                    for s in t['slot_list']:
                        slot_text += s['name']+' '
                except KeyError:
                    pass
                slot = QTableWidgetItem(slot_text)
                self.item_result_table.setItem(r, 0, icon)
                self.item_result_table.setItem(r, 1, nm)
                self.item_result_table.setItem(r, 2, rlv)
                self.item_result_table.setItem(r, 3, tier)
                self.item_result_table.setItem(r, 4, tp)
                self.item_result_table.setItem(r, 5, slot)
            self.item_result_table.resizeColumnsToContents()
        except BaseException as err:
            QMessageBox().critical(self, 'Result Error', 'Try again.\n{}'.format(err))
            self.item_find_btn.setEnabled(True)
            return
        self.item_find_btn.setEnabled(True)

    def display_selected_item(self, item):
        if item.data(1001) is not None:
            item_win = eq2s_item.Eq2db_itemw(item.data(1001), self)
            item_win.show()

    def build_status_queries(self):
        query = self.statusLine.text()
        query += '&{}{}{}'\
            .format(self.statusCombox.currentText(), self.statusCompare.currentText(), self.statusValue.text())
        if query[0] == '&':
            query = query[1:]
        self.statusLine.setText(query)

    def del_last_status_query(self):
        query = self.statusLine.text()
        last_pos = query.rfind('&')
        query = query[:last_pos]
        if last_pos == -1:
            self.statusLine.clear()
            return
        self.statusLine.setText(query)

    def cook_status_query(self):
        ret = ''
        q = self.statusLine.text().split('&')
        for e in q:
            if '>' in e:
                t = e.split('>')
                t[0] = self.statusDict[t[0]]
                ret += '&modifiers.{}.value=>{}'.format(t[0], t[1])
            elif '=' in e:
                t = e.split('>')
                t[0] = self.statusDict[t[0]]
                ret += '&modifiers.{}.value={}'.format(t[0], t[1])
            elif '<' in e:
                t = e.split('>')
                t[0] = self.statusDict[t[0]]
                ret += '&modifiers.{}.value=<{}'.format(t[0], t[1])
        return ret

    def adjust_win_size(self, n_tab):
        if n_tab == 0:
            self.setFixedSize(750, 700)
        elif n_tab == 1:
            self.setFixedSize(750, 350)
        elif n_tab == 2:
            self.setFixedSize(600, 350)

