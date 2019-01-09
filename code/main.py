import sys
import PySide2
from form import Form
from PySide2.QtWidgets import QApplication

app = QApplication(sys.argv)
form = Form('GMC320PlusRadiationMapGenerator.ui', app)
sys.exit(app.exec_())
sys.exit()

