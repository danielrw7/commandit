#!/usr/bin/python

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication, QCompleter, QLineEdit, QStringListModel, QWidget

from run_command import run_command

class CommandWindow(QWidget):
    def __init__(self, parent=None, settings={}, commands={}):
        super(CommandWindow, self).__init__(parent)

        self.settings = settings
        self.commands = commands

        self.push_button_run = QtGui.QPushButton(self)
        self.push_button_run.setText("Run")
        self.push_button_run.clicked.connect(self.on_push_button_run_clicked)
        self.push_button_run.setAutoDefault(True)

        self.line_edit_command = QtGui.QLineEdit(self)
        self.line_edit_command.returnPressed.connect(self.push_button_run.click)

        completer = QCompleter()
        self.line_edit_command.setCompleter(completer)
        self.line_edit_command.setFocus()

        model = QStringListModel()
        completer.setModel(model)

        model.setStringList(self.commands.keys())

        self.message_label = QtGui.QLabel()
        self.message_label.setText("<i>please enter command</i>")
        self.message_label.setStyleSheet("color: #333333")

        self.error_label = QtGui.QLabel()
        self.error_label.setStyleSheet("color: red")
        self.error_label.hide()

        self.output_label = QtGui.QLabel()
        self.output_label.setStyleSheet("font-family: monospace; background-color: #eeeeee; color: green")
        self.output_label.hide()

        self.layoutHorizontal = QtGui.QHBoxLayout()
        self.layoutHorizontal.addWidget(self.line_edit_command)
        self.layoutHorizontal.addWidget(self.push_button_run)

        self.layout_vertical = QtGui.QVBoxLayout(self)
        self.layout_vertical.addWidget(self.message_label)
        self.layout_vertical.addLayout(self.layoutHorizontal)
        self.layout_vertical.addWidget(self.error_label)
        self.layout_vertical.addWidget(self.output_label)

        self.installEventFilter(self)

        # self.resize(640, 480)
        self.center()

    def center(self):
        frame = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())

    def show_error(self, msg=""):
        self.error_label.setText("<br />".join(msg.split("\n")))
        self.error_label.show()

    def show_output(self, msg):
        self.output_label.setText("<br />".join(msg.split("\n")))
        self.output_label.show()

    @QtCore.pyqtSlot()
    def on_push_button_run_clicked(self):
        command = str(self.line_edit_command.text())
        output = None
        command_config = {}
        try:
            output, command_config = run_command(command, self.commands, self.setting("defaultCommandSettings"))
        except Exception as e:
            print e
            return self.show_error(str(e))
        finally:
            if command_config["closeOnSuccess"]:
                self.close()
            else:
                self.show_output(str(output))

    def setting(self, key=None, settings=None):
        if not isinstance(settings, dict):
            settings = self.settings
        try:
            return settings[key]
        except:
            pass

    def keyPressEvent(self, event):
        if self.setting("closeOnEsc") and event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def eventFilter(self, object, event):
        if self.setting("closeOnFocusOut") and event.type() == QtCore.QEvent.WindowDeactivate:
            self.close()

        return False


if __name__ == "__main__":
    import os.path
    from JSONConfig import JSONConfig

    project = "commandit"

    defaults_config_dir = os.path.dirname(os.path.realpath(__file__)) + "/default-settings"
    user_config_dir = os.path.expanduser("~/." + project)

    settings = JSONConfig([
        defaults_config_dir + "/settings.json",
        user_config_dir + "/settings.json"
    ], True)

    commands = JSONConfig([
        defaults_config_dir + "/commands.json",
        user_config_dir + "/commands.json"
    ], True)

    if not os.path.exists(user_config_dir):
        print "Creating default configuration setup at {0}".format(user_config_dir)
        from shutil import copytree
        copytree(defaults_config_dir, user_config_dir)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('CommandWindow')
    main = CommandWindow(None, settings.config, commands.config)
    main.show()

    sys.exit(app.exec_())

