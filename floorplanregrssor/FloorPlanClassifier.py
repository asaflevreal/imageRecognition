import os
import shutil

path = '/Users/asaflev/Downloads/floorplan/train'
entries = os.listdir(path)
print(len(entries))

counts = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0}


def get_class_from_string_and_move_to_directory(string_input):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found+1: num_of_room_index_found+2]
    if num_of_room == '1':
        class_index_found = string_input.find('.png')
        class_of_floor_plan = string_input[class_index_found - 1: class_index_found]
        if counts[class_of_floor_plan] < 1200:
            counts[class_of_floor_plan] = counts[class_of_floor_plan] + 1
            shutil.copyfile(src=f'{path}/{string_input}',
                        dst=f'/Users/asaflev/Desktop/imageEnhanceDebugging/floorPlanClassOneBD/{class_of_floor_plan}/{string_input}')


num_transformed = 0
for string in entries:
    num_transformed += 1
    if num_transformed % 100 == 0:
        print(f'Finished moving {num_transformed}')
    get_class_from_string_and_move_to_directory(string)
