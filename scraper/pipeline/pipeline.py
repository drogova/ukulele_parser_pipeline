import sys
import csv
import json
import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient, errors
from abc import ABC, abstractmethod
from typing import Callable, NoReturn, Dict, IO


class WriterPipeline(ABC):
    @abstractmethod
    def open_spider(self):
        pass

    @abstractmethod
    def process_item(self, item):
        pass

    @abstractmethod
    def close_spider(self):
        pass


class JSONWriterPipeline(WriterPipeline):

    def __init__(self, out_path: str, sign_stdout: str) -> NoReturn:
        """
        JSONWriter Initialization
        :param out_path:
        """
        self.out_path = out_path
        self.sign_stdout = sign_stdout

    def open_spider(self) -> NoReturn:
        """
        Open file
        :return:
        """
        self.file = sys.stdout if self.out_path == self.sign_stdout else open(self.out_path, 'w+', buffering=1)

    def process_item(self, item: Dict[str, str]) -> NoReturn:
        """
        Process item and write it to file
        :param item:
        :return:
        """
        line = json.dumps(item) + '\n'
        self.file.write(line)

    def close_spider(self) -> NoReturn:
        """
        Close file
        :return:
        """
        self.file.close()


class CSVWriterPipeline(WriterPipeline):

    def __init__(self, out_path: str, sign_stdout: str) -> NoReturn:
        """
        JSONWriter Initialization
        :param out_path:
        """
        self.out_path = out_path
        self.sign_stdout = sign_stdout
        self.first_row = False

    def open_spider(self) -> NoReturn:
        """
        Open file
        :return:
        """
        self.file = sys.stdout if self.out_path == self.sign_stdout else open(self.out_path, 'w+', buffering=1)
        self.writer = csv.writer(self.file, delimiter=',')

    def process_item(self, item: Dict[str, str]) -> NoReturn:
        """
        Process item and write it to file
        :param item:
        :return:
        """
        if not self.first_row:
            fieldnames = item.keys()
            self.writer.writerow(fieldnames)
            self.first_row = True
        self.writer.writerow(item.values())

    def close_spider(self) -> NoReturn:
        """
        Close file
        :return:
        """
        self.file.close()


class PostgresWriterPipeline(WriterPipeline):

    def open_spider(self) -> NoReturn:
        """
        Open database connection and create table
        :return:
        """
        self.connection = psycopg2.connect(host='localhost', port=54320, user='postgres', password='pass')
        create_table_sql = '''
            CREATE TABLE IF NOT EXISTS product
            (
                id SERIAL PRIMARY KEY,
                item_name TEXT NOT NULL,
                price TEXT,
                availability TEXT,
                color TEXT,
                type TEXT,
                ukulele_case TEXT,
                range TEXT,
                frets TEXT,
                body_material TEXT,
                ukulele_type TEXT,
                fretboard_material TEXT,
                fingerboard_material TEXT,
                url TEXT NOT NULL
            );
        '''
        with self.connection, self.connection.cursor() as cur:
            cur.execute(create_table_sql)

    def process_item(self, item: Dict[str, str]) -> NoReturn:
        """
        Process item and write it to database
        :param item:
        :return:
        """
        with self.connection, self.connection.cursor() as cur:
            column_names = ','.join(item.keys())
            execute_values(
                cur,
                f'INSERT INTO product ({column_names}) VALUES %s',
                [tuple(item.values(),)]
            )

    def close_spider(self) -> NoReturn:
        """
        Close database connection
        :return:
        """
        self.connection.close()


class MongoWriterPipeline(WriterPipeline):

    def open_spider(self) -> NoReturn:
        """
        Open database connection and create table
        :return:
        """
        self.client = MongoClient('mongodb://702a6083e649:27017/')
        self.db = self.client.products
        print(self.client.admin.command('ping'))

    def process_item(self, item: Dict[str, str]) -> NoReturn:
        """
        Process item and write it to database
        :param item:
        :return:
        """
        self.db.product.insert_many([item])

    def close_spider(self) -> NoReturn:
        """
        Close database connection
        :return:
        """
        self.client.close()

