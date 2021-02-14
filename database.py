import psycopg2
import config_vars


class Database:
    def __init__(self):
        self.connection = psycopg2.connect(database="filemaster", user="postgres",
                                           password=config_vars.DATABASE_PASSWORD,
                                           host="127.0.0.1", port="5432")

    def check_user(self, user_id):
        connection = self.connection
        cursor = connection.cursor()
        user_exists = cursor.execute('''SELECT EXISTS(SELECT 1 FROM information_schema.tables 
                          WHERE table_name=%s)''', (user_id, ))
        exists = cursor.fetchone()[0]
        return exists

    def create_table(self, user_id):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE "{}" (id INT PRIMARY KEY NOT NULL ,
                                            type TEXT NOT NULL ,
                                            name TEXT ,
                                            path TEXT,
                                            fpath TEXT)'''.format(str(user_id)))
        cursor.execute('''INSERT INTO "{}" (id, type, name, path, fpath) 
                            VALUES (0, 'folder', 'root', 'master', '/')'''.format(str(user_id)))
        connection.commit()

    def open_directory(self, user_id, path):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM "%s" WHERE path=%s''', (user_id, path, ))
        files = cursor.fetchall()
        return files

    def touch(self, user_id, file_id, file_name, path):
        connection = self.connection
        cursor = connection.cursor()
        fpath = path + file_name
        cursor.execute('''INSERT INTO "{}" (id, type, name, path, fpath)
                            VALUES (%s, %s, %s, %s, %s)'''.format(str(user_id)),
                       (file_id, 'file', file_name, path, fpath, ))
        connection.commit()
        return 'OK'

    def get_path_folders(self, user_id, path):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM (?) WHERE path=(?) AND type=(?)''', user_id, path, 'folder')
        folders = cursor.fetchall()
        return folders

    def get_parent_directory(self, user_id, path):
        if path == '/':
            return '/'
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM (?) WHERE fpath=(?)''', user_id, path)
        parent = cursor.fetchall()
        return parent[0][3]
