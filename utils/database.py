import psycopg
from config import DB_USER, DB_HOST, DB_PASS
from datetime import datetime, timedelta


class Database:
    def __init__(self, db_name):
        self.dsn = {
            "dbname": db_name,
            "user": DB_USER,
            "password": DB_PASS,
            "host": DB_HOST,
            "port": "5432"
        }
        self.conn = psycopg.connect(**self.dsn)

    def get_categories(self):
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT * FROM "categories"')
            return cursor.fetchall()

    def get_category_name(self, id):
        with self.conn.cursor() as cursor:
            name = cursor.execute(
                'SELECT category_name FROM "categories" WHERE id=%s;', (id,)
            )
            return name.fetchone()[0].upper()

    def add_category(self, new):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "categories" (category_name) VALUES (%s);',
                    (new,)
                )
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def check_category(self, name):
        with self.conn.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM "categories" WHERE category_name = %s;',
                (name,)
            )
            result = cursor.fetchall()
            return not result

    def edit_category(self, old, new):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE "categories" SET category_name = %s WHERE category_name = %s;',
                    (new, old)
                )
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete_category(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM categories WHERE category_name = %s;",
                    (name,)
                )
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_words_category(self, category_id):
        try:
            with self.conn.cursor() as cursor:
                words = cursor.execute(
                    'SELECT word_uz, word_ru, word_en FROM "words" WHERE category_id=%s;', (category_id,)
                )
                words = words.fetchall()
            return words
        except:
            return False

    def word_add(self, uz, ru, en, id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "words" (word_uz, word_ru, word_en, category_id) VALUES (%s, %s, %s, %s);', (uz, ru, en, id)
                )
                self.conn.commit()
            return True
        except:
            return False

    def get_uz_words(self, id):
        with self.conn.cursor() as cursor:
            uz = cursor.execute(
                'SELECT word_uz FROM "words" WHERE category_id=%s;', (id,)
            )
            return uz.fetchall()

    def get_en_words(self, id):
        with self.conn.cursor() as cursor:
            uz = cursor.execute(
                'SELECT word_en FROM "words" WHERE category_id=%s;', (id,)
            )
            return uz.fetchall()

    def get_ru_words(self, id):
        with self.conn.cursor() as cursor:
            ru = cursor.execute(
                'SELECT word_ru FROM "words" WHERE category_id=%s;', (id,)
            )
            return ru.fetchall()

    def get_uz_all(self):
        with self.conn.cursor() as cursor:
            uz = cursor.execute(
                'SELECT word_uz FROM "words"'
            )
            return uz.fetchall()

    def get_en_all(self):
        with self.conn.cursor() as cursor:
            en = cursor.execute(
                'SELECT word_en FROM "words"'
            )
            return en.fetchall()

    def get_ru_all(self):
        with self.conn.cursor() as cursor:
            ru = cursor.execute(
                'SELECT word_ru FROM "words"'
            )
            return ru.fetchall()

    def get_ru_from_uz(self, uz):
        with self.conn.cursor() as cursor:
            ru = cursor.execute(
                'SELECT word_ru FROM "words" WHERE word_uz=%s;', (uz,)
            )
            return ru.fetchone()

    def get_en_from_uz(self, uz):
        with self.conn.cursor() as cursor:
            ru = cursor.execute(
                'SELECT word_en FROM "words" WHERE word_uz=%s;', (uz,)
            )
            return ru.fetchone()

    def get_uz_from_en(self, en):
        with self.conn.cursor() as cursor:
            ru = cursor.execute(
                'SELECT word_uz FROM "words" WHERE word_en=%s;', (en,)
            )
            return ru.fetchone()

    def get_uz_from_ru(self, ru):
        with self.conn.cursor() as cursor:
            uz = cursor.execute(
                'SELECT word_uz FROM "words" WHERE word_ru=%s;', (ru,)
            )
            return uz.fetchone()

    def bot_members(self, tg_id, username, full_name, add_date=None):
        if add_date is None:
            add_date = (datetime.now() + timedelta(hours=5)).strftime("%d.%m.%Y/%H:%M")
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    '''INSERT INTO "users" (tg_id, username, full_name, add_date) 
                       VALUES (%s, %s, %s, %s) 
                       ON CONFLICT (tg_id) DO NOTHING''',
                    (tg_id, username, full_name, add_date)
                )
                self.conn.commit()
            return True
        except Exception:
            return False

    # def bot_members(self, tg_id, username, full_name, add_date=datetime.now().strftime("%d.%m.%Y/%H:%M")):
    #     try:
    #         with self.conn.cursor() as cursor:
    #             cursor.execute(
    #                 'INSERT INTO "users" (tg_id, username, full_name, add_date) VALUES (%s, %s, %s, %s) ON CONFLICT (tg_id) DO NOTHING', (tg_id, username, full_name, add_date)
    #             )
    #             self.conn.commit()
    #         return True
    #     except:
    #         return False

    def get_users(self):
        with self.conn.cursor() as cursor:
            users = cursor.execute(
                'SELECT tg_id, username, full_name, add_date FROM "users";'
            )
            return users.fetchall()
