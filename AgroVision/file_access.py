import earthaccess

def download_data(short_name, bounding_box, date, download_path):
    # Аутентификация через NASA Earthdata без передачи учетных данных
    auth = earthaccess.login()  # используйте только login без аргументов

    # Поиск данных с начальным диапазоном дат
    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(date, date),
        bounding_box=bounding_box
    )

    # Проверка, найдены ли данные
    if results:
        print(f"Найдено {len(results)} файлов. Загружаем...")
        files = earthaccess.download(results[0], download_path)
        print("Данные успешно загружены.")
        return files

    # Если данные не найдены, попытка расширить поиск
    print("Данные не найдены для указанного диапазона дат. Пытаемся расширить диапазон...")

    # Расширение диапазона дат
    new_start_date = "2024-01-01"  # Установите новую начальную дату (пример)
    new_end_date = "2024-09-30"  # Установите новую конечную дату (пример)

    # Повторный поиск с новым диапазоном дат
    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(new_start_date, new_end_date),
        bounding_box=bounding_box
    )

    # Проверка, найдены ли данные с новым диапазоном дат
    if results:
        print(f"Найдено {len(results)} файлов в новом диапазоне дат. Загружаем...")
        files = earthaccess.download(results, download_path)
        print("Данные успешно загружены.")
        return files

    # Если все еще нет результатов, информируем пользователя
    print("Данные не найдены для расширенного диапазона дат.")
    return None  # Возвращаем None, если файлы не найдены
