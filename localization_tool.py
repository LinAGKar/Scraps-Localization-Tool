#!/usr/bin/env python3
import sys
import copy
from collections import namedtuple
from PyQt5 import QtWidgets, QtCore


def Section(title):
    '''For the different sections in the language file'''
    return namedtuple('Section', 'title items')(title, [])


def xor(a, b):
    return (a or b) and not (a and b)


class MainWindow (QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.checkerWindow = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Translation File Checker')

        vbox = QtWidgets.QVBoxLayout()

        # Create all the widgets for the main window
        labelOrig = QtWidgets.QLabel("Original")
        labelTrans = QtWidgets.QLabel("Translated")
        pathOrig = QtWidgets.QLineEdit()
        pathTrans = QtWidgets.QLineEdit()
        btnOrig = QtWidgets.QPushButton('Browse…')
        btnTrans = QtWidgets.QPushButton('Browse…')

        # Open file browser
        btnOrig.clicked.connect(lambda: self.getPath(pathOrig))
        btnTrans.clicked.connect(lambda: self.getPath(pathTrans))

        grid = QtWidgets.QGridLayout()
        grid.addWidget(labelOrig, 0, 0)
        grid.addWidget(labelTrans, 1, 0)
        grid.addWidget(pathOrig, 0, 1)
        grid.addWidget(pathTrans, 1, 1)
        grid.addWidget(btnOrig, 0, 2)
        grid.addWidget(btnTrans, 1, 2)

        widget = QtWidgets.QWidget()
        widget.setLayout(grid)
        vbox.addWidget(widget)

        # Buttons at bottom of window
        hbox = QtWidgets.QHBoxLayout()
        btnCheck = QtWidgets.QPushButton('Check')
        btnQuit = QtWidgets.QPushButton('Quit')
        btnCheck.clicked.connect(
            lambda: self.openCheckerWindow(pathOrig.text(), pathTrans.text()))
        btnQuit.clicked.connect(self.close)
        hbox.addWidget(btnCheck)
        hbox.addWidget(btnQuit)

        widget = QtWidgets.QWidget()
        widget.setLayout(hbox)
        vbox.addWidget(widget)

        self.setLayout(vbox)
        self.show()
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() -
                  self.frameGeometry().center())

    def getPath(self, lineEdit):
        '''Opens file browser dialog and set text in lineEdit to path'''
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file', lineEdit.text())
        if fname and fname[0]:
            lineEdit.setText(fname[0])

    def openCheckerWindow(self, pathOrig, pathTrans):
        '''Open window for checking translation'''
        self.checkerWindow = CheckerWindow(pathOrig, pathTrans)


class CheckerWindow (QtWidgets.QWidget):
    def __init__(self, origPath, transPath):
        super(CheckerWindow, self).__init__()

        self.origPath = origPath
        self.transPath = transPath

        self.keyMap = []  # List of sections, each with title of the section and list of keys for strings in section
        self.origDict = {}  # Holds values from file in original language
        self.transDict = {}  # Holds values from file in translated language
        self.boxes = {}  # Holds lineEdits for the translated text

        self.readFiles()
        self.initUI()

    def readFiles(self):
        '''Sets fields based on text in the files'''
        with open(self.origPath, encoding='utf8') as file:
            currSection = Section('')
            for i in file:
                if len(i.strip(chr(0xFEFF) + ' \n')) > 3 and i.strip(chr(0xFEFF) + ' \n')[:3] == '// ':
                    if currSection.items:
                        self.keyMap.append(currSection)
                    currSection = Section(i.strip(chr(0xFEFF) + ' \n')[3:])
                elif ' = ' in i:
                    tmp = i.strip(chr(0xFEFF) + ' \n').split(' = ', 1)
                    currSection.items.append(tmp[0])
                    self.origDict[tmp[0]] = tmp[1]

        if currSection.items:
            self.keyMap.append(currSection)

        with open(self.transPath, encoding='utf8') as file:
            for i in file:
                if ' = ' in i:
                    tmp = i.strip().split(' = ', 1)
                    self.transDict[tmp[0]] = tmp[1]

        for i in self.origDict:
            if i not in self.transDict:
                self.transDict[i] = ''

    def initUI(self):
        self.setWindowTitle('Translation File Checker')

        def get_widget(b):
            '''Create content area'''
            vBox = QtWidgets.QVBoxLayout()
            for i in self.keyMap:
                grid = QtWidgets.QGridLayout()
                grid.addWidget(QtWidgets.QLabel('Original'), 0, 1)
                grid.addWidget(QtWidgets.QLabel('Translated'), 0, 2)
                row = 1

                for j in i.items:
                    if xor(self.transDict[j] in ['', self.origDict[j]], b):
                        grid.addWidget(QtWidgets.QLabel(j), row, 0)
                        lineEdit = QtWidgets.QLineEdit(self.origDict[j])
                        lineEdit.setReadOnly(True)
                        grid.addWidget(lineEdit, row, 1)
                        lineEdit = QtWidgets.QLineEdit(self.transDict[j])
                        grid.addWidget(lineEdit, row, 2)
                        self.boxes[j] = lineEdit
                        row += 1
                if row > 1:
                    vBox.addWidget(QtWidgets.QLabel(i.title))
                    widget = QtWidgets.QWidget()
                    widget.setLayout(grid)
                    vBox.addWidget(widget)

            widget = QtWidgets.QWidget()
            widget.setLayout(vBox)
            scrollArea = QtWidgets.QScrollArea()
            scrollArea.setWidgetResizable(True)
            scrollArea.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff)
            scrollArea.setSizePolicy(
                QtWidgets.QSizePolicy.MinimumExpanding,
                QtWidgets.QSizePolicy.Expanding)
            scrollArea.setWidget(widget)
            return scrollArea

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(
            QtWidgets.QLabel('Missing, empty, or identical to English:'))
        vbox.addWidget(get_widget(False))
        vbox.addWidget(QtWidgets.QLabel('Translated:'))
        vbox.addWidget(get_widget(True))

        # Buttons at bottom of window
        hbox = QtWidgets.QHBoxLayout()
        btn = QtWidgets.QPushButton('Save')
        btn.clicked.connect(self.finish)
        hbox.addWidget(btn)
        btn = QtWidgets.QPushButton('Cancel')
        btn.clicked.connect(self.close)
        hbox.addWidget(btn)
        widget = QtWidgets.QWidget()
        widget.setLayout(hbox)
        vbox.addWidget(widget)

        self.setLayout(vbox)
        self.show()
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() -
                  self.frameGeometry().center())

    def finish(self):
        '''Save translated language file and close window'''
        for i in self.boxes:
            self.transDict[i] = self.boxes[i].text()
        transFile = open(self.transPath, 'w', encoding='utf8')
        for i in self.keyMap:
            transFile.write('// {}\n'.format(i.title))
            for j in i.items:
                if self.transDict[j]:
                    transFile.write('{} = {}\n'.format(j, self.transDict[j]))
            transFile.write('\n')
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
