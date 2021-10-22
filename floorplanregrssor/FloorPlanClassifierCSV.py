import os
import shutil

import pandas as pd

from floorplanregrssor.testingScript import get_sqf_from_image_str

path = '/Users/asaflev/Downloads/floorplan/train'
entries = os.listdir(path)
print(len(entries))

counts = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0}


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


def get_class_from_string_and_add_to_df(string_input, df_list):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found + 1: num_of_room_index_found + 2]
    if num_of_room in ['0', '1']:
        sqft = get_sqf_from_image_str(string_input)
        class_found = get_class_from_sqft(sqft)
        if type(class_found) == str:
            if counts[class_found] < 3000:
                counts[class_found] = counts[class_found] + 1
                df_list.append({'url': string_input, 'label': class_found})
                shutil.copyfile(src=f'{path}/{string_input}',
                                dst=f'/Users/asaflev/Desktop/imageEnhanceDebugging/floorPlanClassOneAndStudioCSV/{string_input}')


def split_to_test_and_val(data, size_of_train):
    shuffle_df = data.sample(frac=1)
    train_size = int(size_of_train * len(data))
    train_set = shuffle_df[:train_size]
    test_set = shuffle_df[train_size:]
    return train_set, test_set


#
# df = list()
# for string in entries:
#     get_class_from_string_and_add_to_df(string, df)
# df = pd.DataFrame(df)
# df['set'] = 'train'
# df.to_csv('train_data.csv')
bucket_url = 'gs://imagerecognition-277908-vcm/floorPlanSize/csv_created/floorPlanClassOneAndStudioCSV'
df_train = pd.read_csv('train_data.csv')
df_test_val = pd.read_csv('test_data.csv')
df_test, df_validation = split_to_test_and_val(df_test_val, 0.5)
df_validation['set'] = 'validation'
df_ = pd.concat([df_train, df_validation, df_test], ignore_index=True)
df_ = df_[['set', 'url', 'label']]
df_['set'] = df_['set'].apply(lambda x: x.upper())
df_['url'] = df_['url'].apply(lambda x: f'{bucket_url}/{x}')
df_.to_csv('final_csv.csv', index=False, header=False)
