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
        cursor.execute('''CREATE TABLE "{}" (id TEXT ,
                                            type TEXT NOT NULL ,
                                            name TEXT ,
                                            path TEXT,
                                            fpath TEXT UNIQUE)'''.format(str(user_id)))
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
        try:
            cursor.execute('''INSERT INTO "{}" (id, type, name, path, fpath)
                                VALUES (%s, %s, %s, %s, %s)'''.format(str(user_id)),
                           (file_id, 'file', file_name, path, fpath, ))
            connection.commit()
        except psycopg2.Error as e:
            return 'EXISTS'
        return 'OK'

    def create_folder(self, user_id, name, path):
        connection = self.connection
        cursor = connection.cursor()
        fpath = path + name + '/'
        try:
            cursor.execute('''INSERT INTO "{}" (type, name, path, fpath)
                                VALUES (%s, %s, %s, %s)'''.format(str(user_id)),
                           ('folder', name, path, fpath, ))
            connection.commit()
        except psycopg2.Error as e:
            print(e.pgerror)
            return 'EXISTS'
        return 'OK'

    def get(self, user_id, fpath):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM "{}" WHERE fpath=%s'''.format(str(user_id)), (fpath, ))
        file = cursor.fetchone()
        return file

    def get_path_folders(self, user_id, path):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM "{}" WHERE path="%s"'''.format(str(user_id)), (path, ))
        folders = cursor.fetchall()
        return folders

    def get_parent_directory(self, user_id, path):
        if path == '/':
            return '/'
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM "{}" WHERE fpath='{}' '''.format(str(user_id), path))
        parent = cursor.fetchall()
        print(parent)
        return parent[0][3]

    def delete_file(self, user_id, fpath):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''DELETE FROM "{}" WHERE fpath='{}' '''.format(str(user_id), fpath))
        connection.commit()

    def delete_folder(self, user_id, fpath):
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''DELETE FROM "{}" WHERE fpath='{}' '''.format(str(user_id), fpath))
        cursor.execute('''DELETE FROM "{}" WHERE path='{}' '''.format(str(user_id), fpath))
        connection.commit()
