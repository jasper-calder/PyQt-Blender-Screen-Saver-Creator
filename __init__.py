import bpy
import sys
from bpy.types import Operator
 
from PyQt5.QtWidgets import QApplication

from . import Screen_Saver_Generator


class ScreenSaverOP(Operator):

    bl_idname = "jasper.screen_savers"
    bl_label = "Screen Saver Creator"

    def execute(self, context):
        
        self.app = QApplication.instance()

        if not self.app:
            self.app = QApplication(sys.argv)

        self.widget = Screen_Saver_Generator.MainWindow()
        self.widget.show()

        return {"RUNNING_MODAL"}