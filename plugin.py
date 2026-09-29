# -*- coding: utf-8 -*-
"""QGIS entry point for TA Analysis Suite Lite.

The analysis window is imported lazily so QGIS can load the plugin entry
point independently from the heavier analysis/UI module.
"""
import os
from qgis.PyQt.QtGui import QIcon
try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

APP_NAME = "TA Analysis Suite Lite"
VERSION = "1.0.0"

class TASuiteAnalysisLitePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.window = None
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.action = QAction(QIcon(icon_path), APP_NAME, self.iface.mainWindow())
        self.action.setToolTip(f"{APP_NAME} v{VERSION}")
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&TA Analysis Suite Lite", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action is not None:
            try:
                self.iface.removePluginMenu("&TA Analysis Suite Lite", self.action)
            except Exception:
                pass
            try:
                self.iface.removeToolBarIcon(self.action)
            except Exception:
                pass
            self.action = None
        if self.window is not None:
            try:
                self.window.close()
                self.window.deleteLater()
            except Exception:
                pass
            self.window = None

    def run(self):
        # Import the heavy analysis module only when the user opens the plugin.
        from .ta_suite import TASuiteWindow
        if self.window is None:
            self.window = TASuiteWindow(self)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
