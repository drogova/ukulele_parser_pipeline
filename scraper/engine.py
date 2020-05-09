from collections import deque
from requests_html import HTMLSession
from typing import Callable, NoReturn
from scraper.pipeline.pipeline import CSVWriterPipeline, JSONWriterPipeline, PostgresWriterPipeline, MongoWriterPipeline

SIGN_STDOUT = '-'
FORMAT_CSV = 'csv'
FORMAT_JL = 'jl'
FORMAT_POSTGRES = 'postgres'
FORMAT_MONGO = 'mongo'


def start(start_url: str, callback: Callable, out_path: str, out_format: str) -> NoReturn:
    """
    Tasks' handler
    :param start_url:
    :param callback:
    :param out_path:
    :param out_format:
    """
    start_task = (start_url, callback)
    tasks = deque([start_task])

    if out_format == FORMAT_CSV:
        pipeline = CSVWriterPipeline(out_path, SIGN_STDOUT)
    elif out_format == FORMAT_JL:
        pipeline = JSONWriterPipeline(out_path, SIGN_STDOUT)
    elif out_format == FORMAT_POSTGRES:
        pipeline = PostgresWriterPipeline()
    elif out_format == FORMAT_MONGO:
        pipeline = MongoWriterPipeline()
    else:
        raise NotImplementedError('The output format is not implemented.')

    try:
        pipeline.open_spider()
        while tasks:
            url, callback = tasks.popleft()
            print(url)
            session = HTMLSession()
            resp = session.get(url)

            for result in callback(resp):
                if isinstance(result, dict):
                    pipeline.process_item(result)
                else:
                    if result:
                        tasks.append(result)
    finally:
        pipeline.close_spider()
