import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QMainWindow,
                             QTableWidget, QTableWidgetItem, QComboBox, QDialog, QVBoxLayout, QToolBar, QStatusBar,
                             QMessageBox)
from PyQt6.QtGui import QAction, QIcon
import mysql.connector


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="9898250808", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add New Student", self)
        file_menu_item.addAction(add_student_action)
        add_student_action.triggered.connect(self.insert)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Add table and table header
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Add toolbar and toolbar items
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Add Statusbar and statusbar items
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect the selected cell
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)

        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)


    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About the app")
        content = """
        This app is for student record management and it has the add, edit, search and delete functionalities.
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Update Student Records")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get the selected row index
        index = main_window.table.currentRow()

        # Get the selected id
        self.student_id = main_window.table.item(index, 0).text()

        # Get the current selected student name
        selected_student_name = main_window.table.item(index, 1).text()

        self.student_name = QLineEdit(selected_student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Get the current selected course name
        selected_course_name = main_window.table.item(index, 2).text()

        self.course_name = QComboBox()
        courses = ["Biology", "Maths", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(selected_course_name)
        layout.addWidget(self.course_name)

        # Get the selected mobile
        selected_mobile = main_window.table.item(index, 3).text()

        self.mobile = QLineEdit(selected_mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        register_button = QPushButton("Update")
        register_button.clicked.connect(self.update)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def update(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        confirmation_message = QLabel("Are you sure want to delete?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        layout.addWidget(confirmation_message, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)

        self.setLayout(layout)

        yes_button.clicked.connect(self.delete_record)

    def delete_record(self):
        # Get the current selected index and student id
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success Message")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ["Biology", "Maths", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.add_student)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search from the records")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Search with student name")
        layout.addWidget(self.student_name)

        search_button = QPushButton("Submit")
        search_button.clicked.connect(self.search_records)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search_records(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name, ))
        result = cursor.fetchall()
        rows = list(result)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())