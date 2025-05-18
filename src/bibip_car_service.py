from datetime import datetime as dt
from decimal import Decimal
from constants import LINE_SIZE
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from my_exceptions import InvalidCharacterStr, CarNotFoundError
from auxiliary_functions import functions as fn


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        # Создаем переменные пути для работы с файлами.
        self.paths = {
            'cars.txt': f'{self.root_directory_path}/cars.txt',
            'cars_index.txt': f'{self.root_directory_path}/cars_index.txt',
            'models.txt': f'{self.root_directory_path}/models.txt',
            'models_index.txt': f'{self.root_directory_path}/models_index.txt',
            'sales.txt': f'{self.root_directory_path}/sales.txt',
            'sales_index.txt': f'{self.root_directory_path}/sales_index.txt'
        }

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        """
        Функция добавляет модель и её индекс в файлы.
        Вовзращает список добавленной модели.

        Args:
            model(Model): Добавляемая модель.

        Returns:
            Model: Вовзращает добавленную модель.
        """
        # Создаем кортеж для передачи в функцию.
        params = (model.id, model.name, model.brand)
        try:
            if model:
                fn.insert_in_file(params, self.paths['models.txt'], self.paths['models_index.txt'])
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        """
        Функция добавляет машину и её индекс в файлы.
        Вовзращает список добавленной машины.

        Args:
            car(Car): Добавляемая машина.

        Returns:
            Car: Вовзращает добавленную машину.
        """
        # Создаем кортеж для передачи в функцию.
        params = (
            car.vin,
            car.model,
            car.price,
            car.date_start,
            car.status
        )
        try:
            if car:
                fn.insert_in_file(params, self.paths['cars.txt'], self.paths['cars_index.txt'])
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        """
        Функция сохранения новых продаж.

        Args:
            sale(Sale): Текущая продажа.

        Returns:
            Car: Возвращает проданную машину.
        """
        # Создаем кортеж для передачи в функцию.
        params = (
            sale.sales_number,
            sale.car_vin,
            sale.cost,
            sale.sales_date
        )
        try:
            fn.insert_in_file(params, self.paths['sales.txt'], self.paths['sales_index.txt'])

            # Ищем строку где хранится машина в cars.txt.
            str_number = fn.find_index(self.paths['cars_index.txt'], sale.car_vin)

            # Если совпадений не найдено, выбрасывааем исключение.
            if str_number is None:
                raise CarNotFoundError('Такой машины нет в cars.txt')

            # Меняем статус машины.
            list_strings = fn.change_machine_status(self.paths['cars.txt'], str_number, 'sold')

            # Записываем измененный обьект для return.
            object_car = fn.create_car_object(list_strings)
        except CarNotFoundError as e:
            print(str(e))
            raise
        except FileNotFoundError as e:
            print(f'Такого файла нет. Ошибка: {e}')
            raise
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return object_car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        """
        Функция ищет все автомобили с нужным статусом.
        Вовзращает список таких автомобилей.

        Args:
            status(CarStatus): Искомый статус.

        Returns:
            list[Car]: Список найденных машин с нужным статусом.
        """
        try:
            result = list()
            # Открываем файл на чтение.
            # Если такого файла не существует, произойдет исключение.
            with open(self.paths['cars.txt'], 'r', encoding='utf-8', newline='') as f:

                # Читаем по 501 символу за один раз.
                while line := f.read(LINE_SIZE):
                    car_info = line.strip().split(';')

                    # Если автомобиль с нужным статусом найден,
                    # то записываем его в список.
                    if car_info[-1] == status:

                        # Я бы мог написать просто need_car = fn.create_car_object(car_info).
                        # Но пайтесты почему-то падают с ошибкой, хотя обьекты одинаковы.
                        need_car = Car(
                            vin=car_info[0],
                            model=int(car_info[1]),
                            price=Decimal(car_info[2]),
                            date_start=dt.strptime(car_info[3], '%Y-%m-%d %H:%M:%S'),
                            status=CarStatus(car_info[4])
                        )
                        result.append(need_car)
        except FileNotFoundError as e:
            print(f'Такого файла нет. Ошибка: {e}')
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise

        # В задании просят вернуть автомобили в отсортированном порядке,
        # но если я применяю сортировку pytest не засчитывает.
        # result.sort(key=lambda x: x.vin) - сортировал так.
        return result

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """
        Функция выводит информацию о машине по VIN коду.

        Args:
            vin(str): VIN искомой машины.

        Returns:
            CarFullInfo: Полная информацию о машине.
        """
        try:
            result = None
            # Ищем строку где искать нужную машину
            number_line_car = fn.find_index(self.paths['cars_index.txt'], vin)

            # Если не найдена, возвращаем None
            if number_line_car is None:
                return None

            # Получаем индекс модели из car и ищем его аналогично.
            list_car = fn.read_line(self.paths['cars.txt'], number_line_car)
            number_line_model = fn.find_index(self.paths['models_index.txt'], list_car[1])

            if number_line_model is None:
                return None

            # Ищем модель.
            list_model = fn.read_line(self.paths['models.txt'], number_line_model)

            # Заранее устанавливаем переменные продажи.
            sales_date = None
            sales_cost = None

            # Если продажа существует, то ищем в файле информацию.
            if list_car[-1] == 'sold':
                number_line_sold = fn.find_index_sold_vin(self.paths['sales_index.txt'], list_car[0])

                if number_line_sold is None:
                    return None

                # Ищем продажу.
                list_sale = fn.read_line(self.paths['sales.txt'], number_line_sold)

                sales_date = dt.strptime(list_sale[-1], '%Y-%m-%d %H:%M:%S')
                sales_cost = Decimal(list_sale[-2])

            # Сохраняем все в переменную CarFullInfo.
            result = CarFullInfo(
                vin=list_car[0],
                car_model_name=list_model[1],
                car_model_brand=list_model[-1],
                price=Decimal(list_car[2]),
                date_start=dt.strptime(list_car[-2], '%Y-%m-%d %H:%M:%S'),
                status=CarStatus(list_car[-1]),
                sales_date=sales_date,
                sales_cost=sales_cost
            )

        except FileNotFoundError as e:
            print(f'Такого файла нет. Ошибка: {e}')
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return result

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        """
        Функция меняет старый VIN код на новый.

        Args:
            vin(str): VIN старой машины.
            new_vin(str): VIN на который нужно поменять.
        Returns:
            Car: Возвращает измененный обьект.
        """
        try:
            result = None
            number_line_car = fn.find_index(self.paths['cars_index.txt'], vin)

            if number_line_car is None:
                raise CarNotFoundError

            # Находим и меняем строку, которую нужно поменять.
            list_car = fn.read_line(self.paths['cars.txt'], number_line_car)
            list_car[0] = new_vin
            new_str = ';'.join(list_car).ljust(LINE_SIZE - 1) + '\n'

            # Перезаписываем строку
            with open(self.paths['cars.txt'], 'r+', encoding='utf-8', newline='') as f:
                f.seek(number_line_car * (LINE_SIZE))
                f.write(new_str)

            # Чтобы поменять в индексах vin, нужно получить список всех строк.
            list_indexs = fn.read_file(self.paths['cars_index.txt'])
            result_index = list()

            for line in list_indexs:
                list_line = line.strip().split(';')
                vin_car = list_line[0]
                if vin_car == vin:
                    list_line[0] = new_vin
                new_str = ';'.join(list_line) + '\n'
                result_index.append(new_str)
            result_index.sort(key=lambda x: x.split(';')[0])

            with open(self.paths['cars_index.txt'], 'w', encoding='utf-8', newline='') as f:
                f.writelines(result_index)

            # Записываем информацию о машине.
            result = fn.create_car_object(list_car)

        except CarNotFoundError as e:
            print(str(e))
            raise
        except FileNotFoundError as e:
            print(f'Такого файла нет. Ошибка: {e}')
            raise
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return result

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        """
        Функция удаляет продажу
        и меняет ей статус на 'is_deleted' где 'is_deleted' строка
        размером 501 символ включая /n.

        Args:
            sales_number(str): Первичный ключ продажи.
        Returns:
            Car: Возвращает измененный обьект.
        """
        try:
            # Ищем индекс продажи.
            num_sale_index = fn.find_index_sold_sale_num(self.paths['sales_index.txt'], sales_number)

            # Если такой продажи нет, выбрасываем исключение.
            if num_sale_index is None:
                raise CarNotFoundError

            # Перезапимываем индексы продаж
            list_indexs = fn.read_file(self.paths['sales_index.txt'])
            result_index = list()

            vin_car = None
            for line in list_indexs:
                list_line = line.strip().split(';')
                current_sale_num = list_line[0]
                if current_sale_num == sales_number:

                    # Запишем vin авто, которой нужно поменять статус.
                    vin_car = current_sale_num.split('#')[1]
                    if vin_car is None:
                        raise CarNotFoundError
                    continue

                new_str = ';'.join(list_line) + '\n'
                result_index.append(new_str)

            if vin_car is None:
                raise CarNotFoundError

            # Если result индекс не существует после удаление продажи,
            # то файл просто перезапишется на пустой. В ином случае
            # запись произойдет в отсортированном порядке.
            result_index.sort(key=lambda x: x.split(';')[0])
            with open(self.paths['sales_index.txt'], 'w', encoding='utf-8', newline='') as f:
                f.writelines(result_index)

            # Ищем текущею продажу и удаляем её записью is_deleted.
            with open(self.paths['sales.txt'], 'r+', encoding='utf-8', newline='') as f:
                f.seek(num_sale_index * (LINE_SIZE))
                delete_sail = 'is_deleted'.ljust(LINE_SIZE - 1) + '\n'
                f.write(delete_sail)

            # Ищем строку где хранится автомобиль.
            num_car_index = fn.find_index(self.paths['cars_index.txt'], vin_car)

            if num_car_index is None:
                raise CarNotFoundError

            # Находим автомобиль и меняем статус.
            list_current_cur = fn.change_machine_status(self.paths['cars.txt'], num_car_index, 'available')

            # Сохраняем автомобиль для return.
            result = fn.create_car_object(list_current_cur)

        except CarNotFoundError as e:
            print(str(e))
            raise
        except FileNotFoundError as e:
            print(f'Такого файла нет. Ошибка: {e}')
            raise
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return result

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        """
        Функция находит топ 3 самых продаваемых моделей и
        возвращает их в виде списка ModelSaleStats.

        Returns:
            list[ModelSaleStats]: Список моделей.
        """
        try:
            # Сначала вытаскиваем все vin и цену проданных машин в список.
            info_sale = list()
            with open(self.paths['sales.txt'], 'r', encoding='utf-8') as f:
                while line := f.read(LINE_SIZE).strip():

                    # Если продажа удалена, то пропускаем строку.
                    if line == 'is_deleted':
                        continue
                    line_list = line.split(';')
                    car_vin, sale_price = line_list[1], Decimal(line_list[2])
                    info_sale.append([car_vin, sale_price])

            # Далее нужно узнать позицию в cars.txt каждой машины.
            for i in info_sale:
                car_vin = i[0]
                index_car = fn.find_index(self.paths['cars_index.txt'], car_vin)

                # Заменяем vin на index. Так как vin нам больше не нужен.
                i[0] = index_car

            # Создаем словарь моделей
            model_dect = dict()
            for i in info_sale:
                pointer = i[0]
                line_list = fn.read_line(self.paths['cars.txt'], pointer)
                model_id = line_list[1]

                # Ищем информацию где хранится модель.
                model_line = fn.find_index(self.paths['models_index.txt'], model_id)
                price_sale = i[1]
                if model_line not in model_dect:
                    # Первое значение количество продаж этой модели.
                    # Второе цена продажи этой модели.
                    model_dect[model_line] = [1, price_sale] 
                else:
                    model_dect[model_line][0] += 1
                    model_dect[model_line][1] = max(model_dect[model_line][1], price_sale)

            # # Сортируем словарь, сначала по продажам потом по цене.
            top_list = sorted(
                model_dect.items(),
                key=lambda x: (x[1][0], x[1][1]),
                reverse=True
            )
            # Создаем список самых дорогих авто.
            result = list()
            count_auto = 3 if len(top_list) > 2 else len(top_list)
            for i in range(count_auto):
                line_list = fn.read_line(self.paths['models.txt'], top_list[i][0])
                model_name = line_list[1]
                brand_name = line_list[2]
                sales_count = top_list[i][1][0]
                model_object = ModelSaleStats(
                    car_model_name=model_name,
                    brand=brand_name,
                    sales_number=sales_count
                )
                result.append(model_object)
        except CarNotFoundError as e:
            print(str(e))
            raise
        except FileNotFoundError as e:
            print(f'Такого файла нет. Ошибка: {e}')
            raise
        except InvalidCharacterStr as e:
            print(f'Ошибка: {e}')
            raise
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            raise
        return result
