class QtWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(DRAGGED_WINDOW_SIZE, DRAGGED_WINDOW_SIZE)
        self.setWindowTitle("meow")
        
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap("assets/images/1.png").scaled(DRAGGED_WINDOW_SIZE, DRAGGED_WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        random_number = random.randint(1, 7)
        image_path = f"assets/images/{random_number}.png"
        self.label.setPixmap(QPixmap(image_path).scaled(DRAGGED_WINDOW_SIZE, DRAGGED_WINDOW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

class QtApp(QApplication):
    def __init__(self, *args, **kwargs):
        super(QtApp, self).__init__(*args, **kwargs)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.quit()
        return super(QtApp, self).eventFilter(obj, event)