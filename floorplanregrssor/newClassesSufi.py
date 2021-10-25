import os

import pandas as pd

sqfts = []

path = '/Users/asaflev/Downloads/floorplan/train'
entries = os.listdir(path)
print(len(entries))


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


def add_bedroom_sqf_to_list(string_input):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found + 1: num_of_room_index_found + 2]
    if num_of_room in ['0', '1']:
        sqft = get_sqf_from_image_str(string_input)
        sqfts.append(sqft)


for string in entries:
    add_bedroom_sqf_to_list(string)

sqfts_df = pd.DataFrame(columns=['sqft'], data=sqfts)
sqfts_df.sort_values(by='sqft', ascending=True, ignore_index=True, inplace=True)
sqfts_df['sqftClass'] = pd.qcut(sqfts_df['sqft'], 7, labels=['0', '1', '2', '3', '4', '5', '6'])
grouped_by_class = pd.DataFrame(sqfts_df.groupby('sqftClass').agg({'sqft': ['min', 'max', 'count']}).reset_index())
print(grouped_by_class)