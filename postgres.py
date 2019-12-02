# -*- coding: utf-8 -*-

import psycopg2


class Postgres:

    def __init__(self, database):
        self.connection = psycopg2.connect(dbname=database)
        self.cursor = self.connection.cursor()

    def insert(self, date, sum, category, category_2, category_3):
        with self.connection:
            query = 'INSERT INTO analytics (date, price, category, category_2, category_3)' \
                    ' VALUES (%s, %s, %s, %s, %s)'
            data_tuple = (date, sum, category, category_2, category_3)
            self.cursor.execute(query, data_tuple)
            self.connection.commit()
            self.cursor.close()

    def select_weekly_spends(self, start_date):
        with self.connection:
            query = """SELECT sum(price), category_3 FROM analytics 
                    WHERE date >=  date_trunc('week', %s::date)::date 
                    AND date <= (date_trunc('week', %s::date) + '6 days'::interval)::date
                    GROUP BY category_3"""
            self.cursor.execute(query, (start_date, start_date))
            data = self.cursor.fetchall()
            return data

    def select_all(self):
        with self.connection:
            self.cursor.execute('SELECT * FROM analytics')
            rows = self.cursor.fetchall()
            return rows

    def close(self):
        self.connection.close()
