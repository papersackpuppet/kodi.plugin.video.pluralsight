import sqlite3
import os


class Course:
    def __init__(self, name, title, description, modules, category):
        self.category = category
        self.description = description
        self.title = title
        self.name = name
        self.modules = modules


class Module:
    def __init__(self, name, tile, clips, author, duration):
        self.duration = duration
        self.author = author
        self.name = name
        self.title = tile
        self.clips = clips


class Author:
    def __init__(self, display_name, handle):
        self.handle = handle
        self.display_name = display_name


class Clip:
    def __init__(self, title, duration, index, course_name, author_handle, module_name):
        self.module_name = module_name
        self.author_handle = author_handle
        self.course_name = course_name
        self.index = index
        self.duration = duration
        self.title = title

    def get_url(self, username):
        return "http://www.pluralsight.com/metadata/live/users/{username}/" \
               "viewclip/{courseName}/{authorHandle}/{moduleName}/{clipIndex}" \
               "/1024x768mp4".format(username=username, courseName=self.course_name, authorHandle=self.author_handle,
                                     moduleName=self.module_name, clipIndex=self.index)


class Catalog:
    def __init__(self, database_path, data=None):
        if not os.path.exists(database_path):
            database = sqlite3.connect(database_path)
            cursor = database.cursor()

            cursor.execute('''CREATE TABLE author   (id INTEGER PRIMARY KEY ASC, handle TEXT, displayname TEXT) ''')

            cursor.execute('''CREATE TABLE course   (id INTEGER PRIMARY KEY ASC, name TEXT, description TEXT, category_id INTEGER) ''')
            cursor.execute('''CREATE TABLE category (id INTEGER PRIMARY KEY ASC, name TEXT) ''')
            cursor.execute('''CREATE TABLE module   (id INTEGER PRIMARY KEY ASC, author INT, name TEXT, title TEXT, duration INT) ''')
            cursor.execute('''CREATE TABLE clip     (id INTEGER PRIMARY KEY ASC, module_id INT, title TEXT, duration TEXT) ''')

            database.commit()
        else:
            database = sqlite3.connect(database_path)

        if data is not None:
            raw_courses = data["Courses"]
            raw_modules = data["Modules"]
            raw_authors = data["Authors"]
            raw_categories = data["Categories"]
            cursor = database.cursor()

            cursor.execute('DELETE FROM category')
            cursor.execute('DELETE FROM course')
            cursor.execute('DELETE FROM clip')
            cursor.execute('DELETE FROM module')
            cursor.execute('DELETE FROM author')

            for author in raw_authors:
                cursor.execute('INSERT INTO author(handle, displayname) VALUES(?,?)',
                               author["Handle"], author["DisplayName"])

            for category in raw_categories:
                cursor.execute('INSERT INTO category(name) VALUES(?)', category)

            for module in raw_modules:
                cursor.execute('INSERT INTO module(author, name, title, duration) VALUES(?,?,?,?)',
                               int(module["Author"]), module["Name"], module["Title"], module["Duration"])
                module_id = cursor.lastrowid
                for clip in module["Clips"]:
                    cursor.execute('INSERT INTO clip (module_id, title, duration) VALUES(?,?,?)',
                                   module_id, clip["Title"], clip["Duration"])

            for course in raw_courses:
                cursor.execute('INSERT INTO course(name, description, category_id) VALUES (?,?,?)',
                               course["Title"], course["Description"], int(course["Category"]))

            database.commit()

        self.database = database

    def get_courses(self):
        return self.database.cursor().execute('SELECT * FROM course').fetchall()

    def get_course_by_name(self, name):
        return self.database.cursor().execute('SELECT * FROM course WHERE name=?',name).fetchall()[0]

    def get_course_by_title(self, title):
        return self.database.cursor().execute('SELECT * FROM course WHERE title=?', title).fetchall()[0]

    def get_courses_by_category(self, category):
        return self.database.cursor().execute('SELECT * FROM course WHERE category_id=?', int(category)).fetchall()

    def close_db(self):
        self.database.close()