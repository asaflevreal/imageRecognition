import os
from multiprocessing.pool import ThreadPool

import pandas as pd
from google.cloud import automl_v1beta1

# 'content' is base-64-encoded image data.
class_sizes = {'0': {'min': 0, 'max': 650}, '1': {'min': 651, 'max': 850}, '2': {'min': 851, 'max': 1200},
               '3': {'min': 1201, 'max': 1700}, '4': {'min': 1701, 'max': 2200}, '5': {'min': 2201, 'max': 2700},
               '6': {'min': 2701, 'max': 3500}, '7': {'min': 3501, 'max': 4500}, '8': {'min': 4501, 'max': 5500},
               '9': {'min': 5501, 'max': 1000000}
               }


def get_prediction(file_path, model_id):
    project_id = "25296097780"
    with open(file_path, 'rb') as ff:
        content = ff.read()
    prediction_client = automl_v1beta1.PredictionServiceClient()

    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    response = prediction_client.predict(name=name, payload=payload, params=params)
    res = {}
    for annotation_payload in response.payload:
        print(
            u"Predicted class name: {}".format(annotation_payload.display_name)
        )
        print(
            u"Predicted class score: {}".format(
                annotation_payload.classification.score
            )
        )
        res.update({'image_str': file_path, 'classPred': annotation_payload.display_name,
                    'score': annotation_payload.classification.score})
    return res


def get_real_class_from_image_str(string_input):
    class_index_found = string_input.find('.png')
    class_of_floor_plan = string_input[class_index_found - 1: class_index_found]
    return class_of_floor_plan


def find_nth(string_input, subset, n):
    start_index = string_input.find(subset)
    while start_index >= 0 and n > 1:
        start_index = string_input.find(subset, start_index + len(subset))
        n -= 1
    start_index += 1
    end_index = string_input.find(subset, start_index)
    return int(string_input[start_index:end_index])


def get_sqf_from_image_str(string_input):
    sqf = find_nth(string_input, '_', 3)
    return sqf


def get_error(row):
    if row['realClass'] == row['classPred']:
        return 0
    if row['realClass'] > row['classPred']:
        return row['sqrm'] - class_sizes[row['classPred']]['max']
    return class_sizes[row['classPred']]['min'] - row['sqrm']


def get_num_of_rooms(string_input):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found + 1: num_of_room_index_found + 2]
    return num_of_room


def get_results_df():
    path = '/Users/asaflev/Downloads/floorplan/test'
    model_id = 'ICN77983961711640576'
    entries = os.listdir(path)
    entries = entries[:10000]
    entries = list(filter(lambda x: get_num_of_rooms(x) == '1', entries))
    entries = entries[:1000]
    pool = ThreadPool(2)
    results_df = pool.map(lambda x: get_prediction(f'{path}/{x}', model_id=model_id), entries)
    results_df = pd.DataFrame(results_df)
    results_df.dropna(inplace=True)
    results_df['realClass'] = results_df['image_str'].apply(lambda x: get_real_class_from_image_str(x))
    results_df['sqrm'] = results_df['image_str'].apply(lambda x: get_sqf_from_image_str(x))
    results_df['error'] = results_df.apply(lambda row: get_error(row), axis=1)
    results_df['errorSQ'] = results_df['error'].pow(2)
    results_df.to_csv(f'results_{model_id}.csv')
    return results_df


def get_metrics_by_score(score, results_df):
    results_df_temp = results_df[results_df['score'] >= score]
    return {'score': score, 'MAE': round(results_df_temp["error"].mean()),
            'MSE': round(results_df_temp["errorSQ"].mean()),
            'RMSE': round((results_df_temp["errorSQ"].mean()) ** 0.5), 'AmountOfPreds': len(results_df_temp.index)}


def main_func():
    result_df = get_results_df()
    scores_df = []
    for score in [0.5, 0.6, 0.7, 0.8, 0.9]:
        scores_df.append(get_metrics_by_score(score, result_df))
    scores_df = pd.DataFrame(scores_df)
    scores_df['totalImages'] = len(result_df.index)
    return scores_df


scores_df = main_func()
