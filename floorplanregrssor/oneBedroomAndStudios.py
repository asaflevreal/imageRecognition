import os
import shutil
import pandas as pd

path = '/Users/asaflev/Downloads/floorplan/train'
entries = os.listdir(path)
print(len(entries))

counts = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0}
class_sqfts = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}


def get_class_from_sqft(sqft):
    if type(sqft) != int:
        return None
    if sqft < 600:
        return '0'
    if sqft < 750:
        return '1'
    if sqft < 900:
        return '2'
    if sqft < 1100:
        return '3'
    if sqft < 1300:
        return '4'
    if sqft < 1500:
        return '5'
    else:
        return '6'


def find_nth(string_input, subset, n):
    start_index = string_input.find(subset)
    while start_index >= 0 and n > 1:
        start_index = string_input.find(subset, start_index + len(subset))
        n -= 1
    start_index += 1
    end_index = string_input.find(subset, start_index)
    return int(string_input[start_index:end_index])


def get_sqf_from_image_str(string_input):
    try:
        sqf = find_nth(string_input, '_', 3)
        return sqf
    except:
        return None


def add_bedroom_sqf_to_class(string_input):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found + 1: num_of_room_index_found + 2]
    if num_of_room in ['0', '1']:
        sqft = get_sqf_from_image_str(string_input)
        class_found = get_class_from_sqft(sqft)
        if type(class_found) == str:
            class_sqfts[class_found].append(sqft)


def get_class_from_string_and_move_to_directory(string_input):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found + 1: num_of_room_index_found + 2]
    if num_of_room in ['0', '1']:
        sqft = get_sqf_from_image_str(string_input)
        class_found = get_class_from_sqft(sqft)
        if type(class_found) == str:
            if counts[class_found] < 2000:
                counts[class_found] = counts[class_found] + 1
                shutil.copyfile(src=f'{path}/{string_input}',
                                dst=f'/Users/asaflev/Desktop/imageEnhanceDebugging/floorPlanClassOneAndStudio/{class_found}/{string_input}')


for string in entries:
    add_bedroom_sqf_to_class(string)

for key in class_sqfts.keys():
    print(f'{key} Mean Value is:{pd.Series(class_sqfts[key]).mean()}')
