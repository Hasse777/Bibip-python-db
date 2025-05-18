from datetime import datetime as dt
from decimal import Decimal
from constants import LINE_SIZE
from src.models import Car, CarStatus
from my_exceptions import InvalidCharacterStr


def read_file(path: str) -> list:
    """
    Функция по указанному пути читает полностью файл и
    возвращает список прочитанных строк.
    Если файла не существует, ловим исключение и возвращаем пустой список.

    Args:
        path(str): Путь к файлу.

    Returns:
        list: Список прочитанных строк.
    """
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            result = list()
            for line in f:
                if line.strip() == 'is_deleted':
                    continue
                result.append(line)
    except FileNotFoundError:
        return list()
    return result


def insert_in_file(params: tuple, path_txt: str, path_index_txt: str):
    """
    Функция записывает данные в основной файл и обновляет индекс файл.

    Args:
        params(tuple): Кортеж параметров, которые нужно записать в txt.
        path_txt(str): Путь по которому нужно записать обычный txt файл.
        path_index_txt(str): Путь где нужно записать индексы.
    """
    # Проверяем наличие разделителей в строках.
    for i in params:
        # Проверяем принадлежность элемента к str.
        if isinstance(i, str) and ';' in i:
            raise InvalidCharacterStr

    # Записываем информацию в обычный txt.
    with open(path_txt, 'a+',  encoding='utf-8', newline='') as f:
        f.seek(0, 2)
        # Определяем сколько уже строк.
        line_num = f.tell() // LINE_SIZE

        # Записываем данные в файл.
        info_str = (';'.join(map(str, params)).strip()).ljust(LINE_SIZE - 1) + '\n'
        f.write(info_str)

        # Читаем данные из index.txt.
        list_strings = read_file(path_index_txt)

        index_str = f'{params[0]};{line_num}' + '\n'
        place_insert = 0

        # Ищем место куда вставить информацию.
        insert_id = str(params[0])
        for i in list_strings:
            current_id = i.split(';')[0]
            if current_id > insert_id:
                break
            place_insert += 1
        list_strings.insert(place_insert, index_str)

        # Записываем данные в индекс txt.
        with open(path_index_txt, 'w', encoding='utf-8', newline='') as f:
            f.writelines(list_strings)


def find_index(path, first_key: str) -> int | None:
    """
    Функция по указанному пути читает полностью файл и возвращает
    номер строки где хранится нужная информация.

    Args:
        path(str): Путь к файлу.
        first_key(str): Ключ по которому искать.
    Returns:
        int: номер линии.
        None: Если ничего не найдено
    """
    with open(path, 'r', encoding='utf-8', newline='') as f:
        for line in f:
            list_string = line.strip().split(';')
            if list_string[0] == first_key:
                return int(list_string[-1])
    return None


def find_index_sold_vin(path, vin: str) -> int | None:
    """
    Функция ищет номер строки, в которой хранится продажа по номеру машины.

    Args:
        path(str): Путь к файлу.
        vin(str): Номер проданного cars.
    Returns:
        int: Номер линии.
        None: Если ничего не найдено.
    """
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            list_string = line.strip().split(';')

            # В индексах продажи первое значение хранится с разделителем #.
            # Нам нужно дополнительно расплитить его на номер машины.
            vin_auto = (list_string[0].split('#'))[1]
            if vin_auto == vin:
                return int(list_string[-1])
    return None


def find_index_sold_sale_num(path, num_sale: str) -> int | None:
    """
    Функция ищет номер строки, в которой хранится продажа по номеру продажи.

    Args:
        path(str): Путь к файлу.
        num_sold(str): Номер продажи.
    Returns:
        int: Номер линии.
        None: Если ничего не найдено.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                list_string = line.strip().split(';')

                # В индексах продажи первое значение хранится с разделителем #.
                # Нам нужно дополнительно расплитить его на номер машины.
                current_num_sale = list_string[0]
                if current_num_sale == num_sale:
                    return int(list_string[-1])
    except FileNotFoundError as e:
        raise e
    return None


def change_machine_status(path: str, index: int, new_status: str) -> list:
    """
    Функция ищет номер строки, в которой хранится продажа по номеру продажи.

    Args:
        path(str): Путь к файлу.
        index(int): В какой строке поменять статус.
        new_str(str): Новый статус
    Returns:
        list: Список параметров измененной машины.
    """
    with open(path, 'r+',  encoding='utf-8', newline='') as f:
        f.seek(index * (LINE_SIZE))
        current_cur = f.read(LINE_SIZE - 1).strip()
        list_current_cur = current_cur.split(';')
        list_current_cur[-1] = new_status
        new_str = ';'.join(list_current_cur).ljust(LINE_SIZE - 1) + '\n'

        f.seek(index * (LINE_SIZE))
        f.write(new_str)
    return list_current_cur


def create_car_object(car_list: list) -> Car:
    """
    Функция создает обьект машины из списка параметров.

    Args:
        car_list(list): Список параметров.
    Returns:
        Car: Созданный обьект.
    """
    return Car(
        vin=car_list[0],
        model=int(car_list[1]),
        price=Decimal(car_list[2]),
        date_start=dt.strptime(car_list[3], '%Y-%m-%d %H:%M:%S'),
        status=CarStatus(car_list[4])
    )


def read_line(path: str, line: int) -> list:
    """
    Функция читает строчку по указанной строке.

    Args:
        path(str): Путь к файлу.
        line(int): Строка, которую нужно прочитать.
    Returns:
        list: Возвращает список строк разделенной ;.
    """
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            f.seek(line * (LINE_SIZE))
            return f.read(LINE_SIZE).strip().split(';')
    except FileNotFoundError:
        return list()
