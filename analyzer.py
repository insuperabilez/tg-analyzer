from transformers import BertTokenizer, BertForSequenceClassification
import json
import torch
import os
import io
import psutil
def analys():
    tokenizer = BertTokenizer.from_pretrained('SkolkovoInstitute/russian_toxicity_classifier')
    model = BertForSequenceClassification.from_pretrained('SkolkovoInstitute/russian_toxicity_classifier')
    model.eval()
    process = psutil.Process()
    sm = torch.nn.Softmax(dim=0)
    users_otpravka={}
    users_priemka={}
    directory = './data/'
    with torch.no_grad():
        for filename in os.listdir(directory):

            if filename.endswith('.json'):
                # Откройте файл и загрузите его содержимое
                with io.open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                    out_false_messages = []
                    out_true_messages = []
                    data = json.load(f)
                # Создайте пустой список для хранения сообщений с out=True
                # Пройдитесь по каждому сообщению в массиве
                for message in data:
                    if message.get('out') == False:
                        # Если да, добавьте сообщение в список
                        out_false_messages.append(message['message'])
                    else:
                        out_true_messages.append(message['message'])
                del data
                avg=1
                sumout = 0
                sumin = 0
                countout = 0
                countin = 0
                for message in out_false_messages:
                    batch = tokenizer.encode(message, return_tensors='pt')
                    # inference
                    if batch.size()[1] > 512:
                        break
                    res = model(batch)['logits'][0]
                    output = sm(res)
                    sumin = sumin + (1 * output[0]) - (1 * output[1])
                    countin = countin + 1
                try:
                    avg = (sumin / countin).item()
                except:
                    avg=1
                print(f'Общее значение полученных сообщений от пользователя {filename} = {sumin}, среднее ={avg}')
                users_priemka[f'{filename}']=avg
                for message in out_true_messages:
                    batch = tokenizer.encode(message, return_tensors='pt')
                    # inference
                    if batch.size()[1] > 512:
                        break
                    res = model(batch)['logits'][0]

                    output = sm(res)
                    sumout = sumout + (1 * output[0]) - (1 * output[1])
                    countout = countout + 1

                try:
                    avg = (sumout / countout).item()
                except:
                    avg=1
                users_otpravka[f'{filename}'] = avg
                print(f'Общее значение отправленных сообщений для пользователя {filename} = {sumout}, среднее ={avg}')
                memory_usage = process.memory_info().rss

                # Преобразование в мегабайты
                memory_usage_mb = memory_usage / (1024 * 1024)

                # Вывод информации о потреблении памяти
                print(f"Потребление памяти: {memory_usage_mb} МБ")
                print()
    print('Выполнение завершено')
    with open('out.json', 'w') as file:
        # Convert the dictionary to a JSON string and write it to the file
        file.write(json.dumps(users_otpravka,indent=4,ensure_ascii=False))
    with open('in.json', 'w') as file:
            # Convert the dictionary to a JSON string and write it to the file
        file.write(json.dumps(users_priemka, indent=4, ensure_ascii=False))
