import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from ui.dialogs import Dialogs
from utils import get_config_manager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('PDF Tool')
    app.setOrganizationName('PDFTool')

    main_window = MainWindow()
    app.main_window = main_window

    app.setStyle('Fusion')

    def open_export_settings():
        config = get_config_manager()
        current_path = str(config.default_export_path)
        new_path, ok = QInputDialog.getText(
            main_window, '设置默认导出路径',
            '请输入默认导出路径:',
            QLineEdit.EchoMode.Normal,
            current_path
        )
        if ok and new_path:
            new_path_obj = Path(new_path)
            if not new_path_obj.parent.exists():
                Dialogs.show_error(main_window, '错误', '路径无效或上级目录不存在')
                return
            config.default_export_path = new_path_obj
            main_window.split_page.refresh_export_settings()
            main_window.merge_page.refresh_export_settings()
            main_window.compress_page.refresh_export_settings()
            Dialogs.show_success(main_window, '设置成功', f'默认导出路径已设置为:\n{new_path_obj}')

    def open_export_mode_settings():
        from ui.dialogs import Dialogs
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox
        
        config = get_config_manager()
        funcs = ['split', 'merge', 'compress']
        func_names = ['拆分', '合并', '压缩']
        current_modes = [config.get_function_export_mode(func) for func in funcs]
        mode_options = ['使用默认位置', '每次询问']
        mode_map = {'使用默认位置': 'default', '每次询问': 'ask'}
        reverse_mode_map = {'default': '使用默认位置', 'ask': '每次询问'}

        dialog = QDialog(main_window)
        dialog.setWindowTitle('导出模式设置')
        dialog.resize(400, 200)

        layout = QVBoxLayout(dialog)

        group = QGroupBox('选择每个功能的导出模式')
        group_layout = QVBoxLayout()

        combo_boxes = []
        for i, func_name in enumerate(func_names):
            h_layout = QHBoxLayout()
            label = QLabel(f'{func_name}:')
            combo = QComboBox()
            combo.addItems(mode_options)
            current_mode_name = reverse_mode_map[current_modes[i]]
            combo.setCurrentText(current_mode_name)
            combo_boxes.append(combo)
            h_layout.addWidget(label)
            h_layout.addWidget(combo, 1)
            group_layout.addLayout(h_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton('确定')
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.Accepted:
            for i, func in enumerate(funcs):
                selected_mode = mode_map[combo_boxes[i].currentText()]
                config.set_function_export_mode(func, selected_mode)
            
            refresh_all_export_settings()
            Dialogs.show_success(main_window, '设置成功', '导出模式已更新')

    def refresh_all_export_settings():
        main_window.split_page.refresh_export_settings()
        main_window.merge_page.refresh_export_settings()
        main_window.compress_page.refresh_export_settings()

    menu_bar = main_window.menuBar()

    view_menu = menu_bar.addMenu('视图')

    exit_action = view_menu.addAction('退出')
    exit_action.triggered.connect(app.quit)

    settings_menu = menu_bar.addMenu('设置')

    export_path_action = settings_menu.addAction('默认导出路径...')
    export_path_action.triggered.connect(open_export_settings)

    export_mode_action = settings_menu.addAction('导出模式...')
    export_mode_action.triggered.connect(open_export_mode_settings)

    main_window.show()

    refresh_all_export_settings()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
