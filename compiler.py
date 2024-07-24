import sys
import time
import os

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPlainTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QShortcut, QMessageBox
from PyQt5.QtGui import QFontMetrics, QColor, QSyntaxHighlighter, QTextCharFormat, QKeySequence
from PyQt5.QtCore import QRegExp

from QCodeEditor import QCodeEditor
from assembler import Assembler

class AsmHighLighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

    def highlightBlock(self, text):
        pass

class SimpleEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.code_file_path = None
        self.code_needs_save = False
        self.assembler = Assembler()
        self.initUI()

    def getTips(self):
        tips_str = ''
        tips_str += '操作码：'
        for op_code in self.assembler.op_codes.keys():
            tips_str += '{} '.format(op_code)
        tips_str += '\n寄存器：'
        for reg in self.assembler.registers.keys():
            tips_str += '{} '.format(reg)
        return tips_str

    def initUI(self):
        # 创建主布局（垂直布局）
        main_layout = QVBoxLayout()

        # 创建左侧布局（左右布局）
        left_layout = QHBoxLayout()

        # 创建提示
        self.tips = QPlainTextEdit()
        font = self.tips.font()
        font.setPointSize(12)  # 设置字体大小
        self.tips.setFont(font)
        font_metrics = QFontMetrics(self.tips.font())
        line_height = font_metrics.height()
        self.tips.setMinimumHeight(line_height * 3)
        self.tips.setMaximumHeight(line_height * 4)
        self.tips.setReadOnly(True)
        self.tips.setPlainText(self.getTips())

        # 创建输入框（多行文本编辑器）
        self.code_editor = QCodeEditor(True, True)
        font = self.code_editor.font()
        font.setPointSize(16)  # 设置字体大小
        self.code_editor.setFont(font)
        font_metrics = QFontMetrics(self.code_editor.font())
        line_height = font_metrics.height()
        self.code_editor.setMinimumHeight(line_height * 25)
        self.code_editor.textChanged.connect(self.onCodeEditorChanged)

        # 创建编译按钮
        self.compile_button = QPushButton('编译🔧', self)
        self.compile_button.clicked.connect(self.compile_code)

        # 创建一个按钮，用于打开文件选择对话框
        self.load_code_button = QPushButton('打开源码', self)
        self.load_code_button.clicked.connect(self.loadSourceCode)

        # 保存文件快捷键
        shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        shortcut.activated.connect(self.saveSourceCode)

        # 创建显示框
        self.display_box = QCodeEditor(True, True, AsmHighLighter)
        font = self.code_editor.font()
        font.setPointSize(16)  # 设置字体大小
        self.display_box.setFont(font)
        font_metrics = QFontMetrics(self.display_box.font())
        line_height = font_metrics.height()
        self.display_box.setMinimumHeight(line_height * 25)
        self.display_box.setReadOnly(True)

        # 将输入框和按钮添加到左侧布局
        left_layout.addWidget(self.code_editor)
        left_layout.addWidget(self.display_box)

        # 将左侧布局和显示框添加到主布局
        main_layout.addWidget(self.load_code_button)
        main_layout.addWidget(self.tips)
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.compile_button)

        # 设置布局
        self.setLayout(main_layout)

        # 设置窗口属性
        self.setGeometry(900, 600, 2000, 600)
        self.setWindowTitle('赛博缺氧手搓 CPU 编译器')
        self.show()

    def closeEvent(self, event):
        if self.code_needs_save:
            # 弹出保存文件的提示对话框
            reply = QMessageBox.question(self, '保存文件',
                                        "您想要保存当前的代码吗?", QMessageBox.Yes |
                                        QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                # 如果用户选择保存，则可以在这里添加保存文件的代码
                self.saveSourceCode()

        # 不管用户的选择如何，都关闭窗口
        event.accept()

    def compile_code(self):
        # 当按钮被点击时，获取输入框的文本并显示在显示框中
        code = self.code_editor.toPlainText()
        try:
            self.display_box.setPlainText('正在编译...')
            self.repaint()
            asm = self.assembler.assemble(code)
            time.sleep(0.5)
            self.display_box.setPlainText(asm)
        except Exception as e:
            self.display_box.setPlainText(str(e))

    def onCodeEditorChanged(self):
        self.code_needs_save = True

    def loadSourceCode(self):
        # 打开文件选择对话框
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '',
                                                   'All Files (*);;Source Code (*.asm)', options=options)

        # 检查用户是否选择了文件
        if file_path:
            self.code_file_path = file_path
        if self.code_file_path is None:
            return
        with open(self.code_file_path) as f:
            codes = f.read()
            self.code_editor.setPlainText(codes)
            print('加载文件成功！')
            self.code_needs_save = False

    def saveSourceCode(self):
        if not self.code_needs_save:
            return
        if self.code_file_path is None:
            # 打开文件选择对话框
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, '新建文件', '',
                                                    'All Files (*);;Source Code (*.asm)', options=options)
            if file_path:
                self.code_file_path = file_path
        with open(self.code_file_path, 'w+') as f:
            codes = self.code_editor.toPlainText()
            f.write(codes)
            print('文件保存成功！')
            self.code_needs_save = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = SimpleEditor()
    sys.exit(app.exec_())
