import json
def sortdict(name):
# Открытие JSON-файла и чтение его содержимого
    with open(name) as json_file:
        data = json.load(json_file)

    # Сортировка объекта Python по значению
    sorted_data = sorted(data.items(), key=lambda x: x[1])

    # Запись отсортированного JSON-строки обратно в файл
    with open(name, 'w') as json_file:
        json_file.write(json.dumps(dict(sorted_data),indent=4,ensure_ascii=False))
