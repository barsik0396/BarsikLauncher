from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor, QPalette


TAG_COLORS = {
    "Релиз":         ("#155724", "#c3e6cb"),
    "Снапшот":       ("#856404", "#ffeeba"),
    "Бета":          ("#7a3a00", "#ffd0a0"),
    "Альфа":         ("#721c24", "#f5c6cb"),
    "Fabric":        ("#333333", "#e8e8e8"),
    "Forge":         ("#721c24", "#f5c6cb"),
    "latest":        ("#155724", "#c3e6cb"),
    "Не установлена":("#856404", "#ffeeba"),
    "Установлена":   ("#0d4a1a", "#a8dab5"),
}

TYPE_LABELS = {
    "release":   "Релиз",
    "snapshot":  "Снапшот",
    "old_beta":  "Бета",
    "old_alpha": "Альфа",
}

FILTER_ALL      = "Все"
FILTER_RELEASE  = "Релизы"
FILTER_SNAPSHOT = "Снапшоты"
FILTER_BETA     = "Бета"
FILTER_ALPHA    = "Альфа"
FILTER_FABRIC   = "Fabric"
FILTER_FORGE    = "Forge"
FILTERS = [FILTER_ALL, FILTER_RELEASE, FILTER_SNAPSHOT, FILTER_BETA, FILTER_ALPHA, FILTER_FABRIC, FILTER_FORGE]


def _tag_label(text: str) -> QLabel:
    fg, bg = TAG_COLORS.get(text, ("#333", "#e0e0e0"))
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius:3px;"
        f"padding:1px 4px; font-size:10px;"
    )
    return lbl


class BuildRowsWorker(QThread):
    done = Signal(list)

    def __init__(self, by_type, fabric, forge, installed, latest,
                 current_ver, current_loader, active_filter, search_text):
        super().__init__()
        self.by_type        = by_type
        self.fabric         = set(fabric)
        self.forge          = set(forge)
        self.installed      = set(installed)
        self.latest         = latest
        self.current_ver    = current_ver
        self.current_loader = current_loader
        self.active_filter  = active_filter
        self.search_text    = search_text.lower()

    def _matches(self, vid, loader, type_key):
        f = self.active_filter
        if f == FILTER_ALL:      return True
        if f == FILTER_RELEASE:  return type_key == "release"   and loader is None
        if f == FILTER_SNAPSHOT: return type_key == "snapshot"  and loader is None
        if f == FILTER_BETA:     return type_key == "old_beta"  and loader is None
        if f == FILTER_ALPHA:    return type_key == "old_alpha" and loader is None
        if f == FILTER_FABRIC:   return loader == "fabric"
        if f == FILTER_FORGE:    return loader == "forge"
        return True

    def run(self):
        rows = []
        for type_key, ids in self.by_type.items():
            for vid in ids:
                if self.search_text and self.search_text not in vid.lower():
                    continue
                for loader in ([None]
                               + (["fabric"] if vid in self.fabric else [])
                               + (["forge"]  if vid in self.forge  else [])):
                    if not self._matches(vid, loader, type_key):
                        continue
                    tags = []
                    if loader == "fabric":
                        tags.append("Fabric")
                    elif loader == "forge":
                        tags.append("Forge")
                    tags.append(TYPE_LABELS.get(type_key, type_key))
                    if vid in self.installed:
                        tags.append("Установлена")
                    else:
                        tags.append("Не установлена")
                    if self.latest.get("release") == vid and loader is None:
                        tags.append("latest")
                    elif self.latest.get("snapshot") == vid and loader is None:
                        tags.append("latest")
                    is_cur = (vid == self.current_ver and loader == self.current_loader)
                    rows.append((vid, loader, tags, is_cur))
        self.done.emit(rows)


class VersionRow(QWidget):
    selected = Signal(str, object)

    def __init__(self, version_id, loader, tags, is_current):
        super().__init__()
        self.version_id = version_id
        self.loader     = loader
        self.setFixedHeight(28)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(5)

        arrow = QLabel("👉" if is_current else "")
        arrow.setFixedWidth(20)
        layout.addWidget(arrow)

        display = (f"{version_id} с Fabric" if loader == "fabric"
                   else f"{version_id} с Forge" if loader == "forge"
                   else version_id)
        name = QLabel(display)
        name.setFixedWidth(170)
        layout.addWidget(name)

        for t in tags:
            layout.addWidget(_tag_label(t))

        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.version_id, self.loader)

    def enterEvent(self, event):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.Window, p.color(QPalette.Midlight))
        self.setPalette(p)

    def leaveEvent(self, event):
        self.setAutoFillBackground(False)


class VersionPickerWindow(QWidget):
    version_chosen = Signal(str, object)

    def __init__(self, by_type, fabric_versions, forge_versions,
                 latest, installed, current_version, current_loader):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self._by_type        = by_type
        self._fabric         = fabric_versions
        self._forge          = forge_versions
        self._latest         = latest
        self._installed      = installed
        self._current_ver    = current_version
        self._current_loader = current_loader
        self._active_filter  = FILTER_ALL
        self._worker         = None

        self.setFixedWidth(560)
        self.setFixedHeight(380)
        self.setFrameStyle = lambda *a: None

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Поиск
        self._search = QLineEdit()
        self._search.setPlaceholderText("Найти версию")
        self._search.setFixedHeight(28)
        self._search.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search)

        # Фильтры
        filter_row = QHBoxLayout()
        filter_row.setSpacing(3)
        self._filter_btns = {}
        for f in FILTERS:
            btn = QPushButton(f)
            btn.setFixedHeight(22)
            btn.setCheckable(True)
            btn.setChecked(f == FILTER_ALL)
            btn.setStyleSheet("font-size: 10px; padding: 0 4px;")
            btn.clicked.connect(lambda checked, ff=f: self._set_filter(ff))
            self._filter_btns[f] = btn
            filter_row.addWidget(btn)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Счётчик
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self._count_label)

        # Заголовок
        hdr = QHBoxLayout()
        hdr.setContentsMargins(24, 0, 4, 0)
        hdr.setSpacing(5)
        lbl_v = QLabel("Версия")
        lbl_v.setFixedWidth(170)
        lbl_v.setFont(QFont(lbl_v.font().family(), 9, QFont.Bold))
        lbl_t = QLabel("Теги")
        lbl_t.setFont(QFont(lbl_t.font().family(), 9, QFont.Bold))
        hdr.addWidget(lbl_v)
        hdr.addWidget(lbl_t)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Стек: загрузка / список
        self._loading_label = QLabel("Загрузка...")
        self._loading_label.setAlignment(Qt.AlignCenter)
        self._loading_label.setStyleSheet("color: gray;")
        layout.addWidget(self._loading_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()
        scroll.setWidget(self._list_widget)
        self._scroll = scroll
        self._scroll.setVisible(False)
        layout.addWidget(scroll)

    def _set_filter(self, f):
        self._active_filter = f
        for name, btn in self._filter_btns.items():
            btn.setChecked(name == f)
        self._refresh()

    def _on_search_changed(self):
        self._refresh()

    def _refresh(self):
        # Показываем загрузку, скрываем список
        self._scroll.setVisible(False)
        self._loading_label.setVisible(True)
        self._count_label.setText("")

        # Чистим старые строки
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait()

        self._worker = BuildRowsWorker(
            self._by_type, self._fabric, self._forge,
            self._installed, self._latest,
            self._current_ver, self._current_loader,
            self._active_filter, self._search.text()
        )
        self._worker.done.connect(self._on_rows_ready)
        self._worker.start()

    def _on_rows_ready(self, rows):
        for vid, loader, tags, is_cur in rows:
            row = VersionRow(vid, loader, tags, is_cur)
            row.selected.connect(self._on_chosen)
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)

        self._count_label.setText(f"Найдено {len(rows)} версий")
        self._loading_label.setVisible(False)
        self._scroll.setVisible(True)

    def _on_chosen(self, vid, loader):
        self._current_ver    = vid
        self._current_loader = loader
        self.version_chosen.emit(vid, loader)
        self.hide()

    def focusOutEvent(self, event):
        self.hide()