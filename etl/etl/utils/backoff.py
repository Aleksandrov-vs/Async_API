import logging
import time
from functools import wraps


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, mode='func'):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param mode: тип функции для которой декоратор
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            while True:
                try:
                    if mode == 'func':
                        return func(*args, **kwargs)
                    elif mode == 'gen':
                        yield from func(*args, **kwargs)
                        break
                    else:
                        raise ValueError('Mode is not correct')
                except Exception as ex:
                    sleep_time = start_sleep_time * (factor ** n) if start_sleep_time * (
                            factor ** n) < border_sleep_time else border_sleep_time
                    time.sleep(sleep_time)
                    logging.info(f'Sleeping {sleep_time} sec while {ex}')
                    n += 1

        return inner

    return func_wrapper
