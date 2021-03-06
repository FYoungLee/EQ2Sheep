from PyQt5.QtWidgets import QDialog, QWidget, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QLabel,\
    QMessageBox, QComboBox
from PyQt5.Qt import QIcon, QSize, QFont
from PyQt5.QtCore import Qt
import eq2s_func

class Eq2db_aas(QDialog):
    def __init__(self, aa_pak, parent=None):
        self.aa_pak = aa_pak
        super(QDialog, self).__init__(parent)
        self.setFixedWidth(900)
        self.setFixedHeight(620)
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.stored_aas_combox = QComboBox()
        self.stored_aas_combox.setFixedWidth(100)
        self.stored_aas_combox.addItem('Current')
        for each in self.aa_pak:
            if 'Current' not in each:
                self.stored_aas_combox.addItem(each)
        self.stored_aas_combox.setCurrentIndex(0)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.stored_aas_combox)
        self.setLayout(main_layout)
        self.build_aa_layout(self.aa_pak['Current'])
        self.stored_aas_combox.currentIndexChanged.connect(self.aaSwitch)

    def build_aa_layout(self, pak):
        trees_id = self.get_tree_tabs(pak)
        trees_info = eq2s_func.get_db_content('aatree', 'id', trees_id)
        self.aa_maxpoints = {}
        self.aa_clickedpoints = {}
        self.aa_points_display = {}
        # store aa tabs
        self.aa_tables = {}
        tradeskilltabs = []
        # adventure tabs
        for each in sorted(trees_id):
            name = trees_info[each]['name']
            # store all tradeskill aa tab into a list, and make all of them next to adventure tabs.
            if name in ['Tradeskill', 'General', 'Far Seas']:
                tradeskilltabs.append(each)
                continue
            # jumping to tabs creating function
            tab = self.create_tabs(each)
            self.aa_maxpoints[each] = trees_info[each]['maxpointsperlevelnode_list'][-1]['maxpoints']
            self.aa_clickedpoints[each] = 0
            self.aa_points_display[each].setText('{} / {}'.format(self.aa_clickedpoints[each], self.aa_maxpoints[each]))
            self.tab_widget.addTab(tab, name)
        # tradeskill tabs
        for each in tradeskilltabs:
            tab = self.create_tabs(each)
            self.aa_maxpoints[each] = trees_info[each]['maxpointsperlevelnode_list'][-1]['maxpoints']
            self.aa_clickedpoints[each] = 0
            self.aa_points_display[each].setText('{} / {}'
                                                 .format(self.aa_clickedpoints[each], self.aa_maxpoints[each]))
            self.tab_widget.addTab(tab, trees_info[each]['name'])

        self.splnodes = {}
        # construct the aa layout
        try:
            for e1 in trees_info:
                grid_n = eq2s_func.get_aa_tree_grid_modifier(trees_info[e1]['name'])
                for e2 in trees_info[e1]['alternateadvancementnode_list']:
                    epicon = QTableWidgetItem()
                    epicon.setFont(QFont("Times", 15, QFont.Black))
                    # get the crc group spells from local databases, cuz only one target provide,
                    # so I just extract the only list from the returned dict.
                    crcs = eq2s_func.get_db_content('crcspl', 'crc', (e2['spellcrc'],))[e2['spellcrc']]
                    # this dict intend to save ordered level(tier) crc spells, the keys means tier of this spell.
                    crcdict = {}
                    for each in crcs:
                        crcdict[each['tier']] = each
                    epicon.setData(1000, crcdict)
                    self.splnodes[e2['nodeid']] = epicon
                    epicon.setToolTip(eq2s_func.CookSpellText(crcs[0]))
                    icon = QIcon()
                    iconid = epicon.data(1000)[1]['icon']['id']
                    # backiconid = epicon.data(1000)[0]['icon']['backdrop']
                    icon.addPixmap(eq2s_func.get_pixmap_in_db(iconid, 'spellicons'))
                    # epicon.setBackground(QBrush(eq2s_func.get_pixmap_in_db(backiconid, 'spellicons')))
                    epicon.setIcon(icon)
                    self.aa_tables[e1].setItem(int(e2['ycoord']*grid_n['y']+1), int(e2['xcoord']*grid_n['x']+1), epicon)
        except BaseException as err:
            QMessageBox().critical(self, 'Loading Error', 'Something Bad Happen:\n{}'.format(err))
            print(err)
            return

        self.fresh_tables()
        self.throw_aas(pak)

    def get_tree_tabs(self, aas):
        unique_tree_id = {}
        for t in aas:
            unique_tree_id[t['treeID']] = 1
        return tuple(unique_tree_id.keys())

    def create_tabs(self, each):
        tab = QWidget()
        layout = QVBoxLayout()
        # create a table inside each tab
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setShowGrid(False)
        # do not display headers
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setIconSize(QSize(42, 42))
        table.setColumnCount(17)
        for n in range(17):
            table.setColumnWidth(n, 1)
        table.setRowCount(15)
        for n in range(15):
            table.setRowHeight(n, 1)
        # the key of each table is the tree id
        self.aa_tables[each] = table
        # creating label for displaying aa points already applied, also the key of this dict is the tree id.
        self.aa_points_display[each] = QLabel()
        layout.addWidget(table)
        layout.addWidget(self.aa_points_display[each])
        tab.setLayout(layout)
        return tab

    def throw_aas(self, tree_packet):
        for each in tree_packet:
            try:
                if 'tier' in each.keys():
                    self.click_aa(each['id'], each['tier'])
                    self.aa_clickedpoints[each['treeID']] += each['tier']
                elif 'order' in each.keys():
                    self.click_aa(each['id'], 1)
                    self.aa_clickedpoints[each['treeID']] += 1
                self.aa_points_display[each['treeID']].setText('{} / {}'
                                                               .format(self.aa_clickedpoints[each['treeID']],
                                                                       self.aa_maxpoints[each['treeID']]))
            except BaseException as err:
                print(err)
        self.fresh_tables()

    def fresh_tables(self):
        for each in self.aa_tables:
            self.aa_tables[each].resizeColumnsToContents()
            self.aa_tables[each].resizeRowsToContents()

    # aa clicking function that takes nodeid and the points will be clicked.
    # nodeid means itself, n means how many times this node clicked.
    def click_aa(self, nodeid, n):
        # trying to acquire current node level(tier)
        try:
            cur_n = int(self.splnodes[nodeid].text())
        except ValueError:
            cur_n = 0
        # plus the given n.
        cur_n += n
        self.splnodes[nodeid].setText(str(cur_n))
        self.splnodes[nodeid].setTextAlignment(Qt.AlignBottom)
        # get spell detail from the item data
        spell = self.splnodes[nodeid].data(1000)[cur_n]
        # cook spell rich text
        curlv = eq2s_func.CookSpellText(spell)
        nextlv = '<br>'
        # trying to get next level if possible.
        try:
            nextlv += 'Next Level: <br>{}' \
                .format(eq2s_func.CookSpellText(self.splnodes[nodeid].data(1000)[cur_n + 1]))
        except KeyError:
            pass
        # renew the tooltips.
        self.splnodes[nodeid].setToolTip(curlv + nextlv)

    def clear_aas(self):
        n = 0
        for each in self.splnodes:
            if self.splnodes[each].text() is not '':
                n += int(self.splnodes[each].text())
            self.splnodes[each].setText('')
        for each in self.aa_clickedpoints:
            self.aa_clickedpoints[each] = 0
        self.fresh_tables()
        return n

    def aaSwitch(self):
        print(self.clear_aas())
        self.throw_aas(self.aa_pak[self.stored_aas_combox.currentText()])