from PyQt5.QtWidgets import QApplication
import eq2s_main
import sys

app = QApplication(sys.argv)
w = eq2s_main.EQ2DB_MainW()
app.exec_()