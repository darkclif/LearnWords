# Python
import sys
from typing import List

# PySide6
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PySide6.QtCore import QEventLoop, Qt, Signal

# App
import learn


class MiniConsole(QWidget):
    # On enter clicked
    on_line_ready = Signal(str)
    # On single key clicked
    on_char_ready = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mini Console")
        self.setStyleSheet("background: black; color: white; font-family: Consolas;")

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output.setStyleSheet("background: black; color: white; font-family: Consolas;")

        self.input = QLineEdit()
        self.input.setFocus()
        self.input.setStyleSheet("background: #222; color: white; font-family: Consolas;")

        self.input.returnPressed.connect(self._on_line_entered)
        self.input.textEdited.connect(self._on_text_edited)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 5, 5)
        layout.addWidget(self.output)
        layout.addWidget(self.input)
        self.setLayout(layout)

    #region Console API
    def print(self, *args: str):
        self.output.append("".join(args))
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def cls(self):
        self.output.clear()

    def get_input(self) -> learn.cl_input:
        """Waits for a full line, like input()."""
        loop = QEventLoop()
        result: List[str] = [""]

        def on_line(text: str):
            result[0] = text
            loop.quit()

        self.on_line_ready.connect(on_line)
        loop.exec()
        self.on_line_ready.disconnect(on_line)

        return learn.cl_input(result[0])

    def get_input_ch(self) -> learn.cl_input:
        """Returns a single character immediately."""
        loop = QEventLoop()
        result: List[str] = [""]

        def on_char(ch: str):
            result[0] = ch
            self.input.clear()
            loop.quit()

        self.on_char_ready.connect(on_char)
        loop.exec()
        self.on_char_ready.disconnect(on_char)

        return learn.cl_input(result[0])
    
    def exit(self):
        self.close()
    #endregion

    # Internal event handlers
    def closeEvent(self, event):
        exit()
        
    def _on_line_entered(self):
        text = self.input.text()
        self.input.clear()
        self.on_line_ready.emit(text)

    def _on_text_edited(self, text: str):
        # detect last typed character
        if text:
            ch = text[-1]
            self.on_char_ready.emit(ch)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qt_console = MiniConsole()
    qt_console.resize(600, 400)
    qt_console.show()

    learn.run(qt_console)
