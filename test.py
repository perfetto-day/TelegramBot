import json
import config
from datetime import datetime

data_file = config.data


def get_data(data_file):
    with open(data_file, 'r') as f:
        raw_data = f.read()
        if raw_data:
            return json.loads(raw_data)
        return {}


data = get_data(data_file)
# print('Упражнение "{0[name]}" с целью {0[goal]} повторений до {0[finish_date]} установлено'.format(exercise))

current_time = datetime.now()
n = [1, 2, 3]
text = "Длинный текст\n{0[0]} - нет\n{0[1]} - да".format(n)
n = [2, 3, 4]
text = text + "\n{0[1]} - нет".format(n)
for n in data["307928327"]["users"]["307928327"]["exercises"]:
    if n != "quantity":
        print(data["307928327"]["users"]["307928327"]["exercises"][n]["name"])
text1 = '/3'
text2 = text1[1]
print(text2)
