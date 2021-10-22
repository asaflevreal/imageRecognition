import os
from multiprocessing.pool import ThreadPool

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from google.cloud import automl_v1beta1
# 'content' is base-64-encoded image data.
from sklearn.metrics import confusion_matrix, accuracy_score

class_sizes = {
    '0': {'min': 0, 'actualMean': 500, 'max': 600},
    '1': {'min': 601, 'actualMean': 672, 'max': 750},
    '2': {'min': 751, 'actualMean': 806, 'max': 900},
    '3': {'min': 901, 'actualMean': 966, 'max': 1100},
    '4': {'min': 1101, 'actualMean': 1175, 'max': 1300},
    '5': {'min': 1301, 'actualMean': 1387, 'max': 1500},
    '6': {'min': 1501, 'actualMean': 2469, 'max': 35000},
}
model_id_names = {'ICN8969778476001263616': 'reg', 'ICN2123603354956333056': 'csv'}

scores_df1 = pd.read_csv(f'./final_scores_reg.csv')


def get_prediction(file_path, model_id):
    project_id = "25296097780"
    with open(file_path, 'rb') as ff:
        content = ff.read()
    prediction_client = automl_v1beta1.PredictionServiceClient()

    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {'score_threshold': '0.5'}
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
    try:
        sqf = find_nth(string_input, '_', 3)
        return sqf
    except:
        return None


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


def get_error_from_middle_range(row):
    row_sqf = row['sqft']
    class_actual_mean = class_sizes[str(row['classPred'])]['actualMean']
    return abs(row_sqf - class_actual_mean)


def get_num_of_rooms(string_input):
    num_of_room_index_found = string_input.find('_')
    num_of_room = string_input[num_of_room_index_found + 1: num_of_room_index_found + 2]
    return num_of_room


def get_results_df(model_id):
    path = '/Users/asaflev/Downloads/floorplan/test'
    entries = os.listdir(path)
    entries = entries[:10000]
    entries = list(filter(lambda x: get_num_of_rooms(x) in ['0', '1'], entries))
    entries = entries[:1000]
    pool = ThreadPool(3)
    results_df = pool.map(lambda x: get_prediction(f'{path}/{x}', model_id=model_id), entries)
    results_df = pd.DataFrame(results_df)
    results_df.dropna(inplace=True)
    results_df['sqft'] = results_df['image_str'].apply(lambda x: get_sqf_from_image_str(x))
    results_df['realClass'] = results_df['sqft'].apply(lambda x: get_class_from_sqft(x))
    results_df['error'] = results_df.apply(lambda row: get_error_from_middle_range(row), axis=1)
    results_df['errorSQ'] = results_df['error'].pow(2)
    results_df['errorPercentage'] = 100 * (results_df['error'] / results_df['sqft'])
    results_df.to_csv(f'results_{model_id_names[model_id]}.csv')
    return results_df


def get_metrics_by_score(score, results_df):
    results_df_temp = results_df[results_df['score'] >= score]
    return {'score': score, 'MAE': round(results_df_temp["error"].mean()),
            'MSE': round(results_df_temp["errorSQ"].mean()),
            'RMSE': round((results_df_temp["errorSQ"].mean()) ** 0.5),
            'MAPE': round((results_df_temp["errorPercentage"].mean())),
            'AmountOfPreds': len(results_df_temp.index)}


def get_reports_and_con_matrix(predictions, truth: pd.DataFrame):
    pred_labels = [0, 1, 2, 3, 4, 5, 6]

    cm = confusion_matrix(truth, predictions, labels=pred_labels, normalize='all')
    cm = pd.DataFrame(cm)
    matrix_norm = cm.apply(lambda row: round(row / row.sum(), 2) * 100, axis=1)
    print(f'ACC: {accuracy_score(truth, predictions)}')
    ax = plt.subplot()
    sns.heatmap(matrix_norm, annot=True, ax=ax, fmt='g')
    ax.set_xticklabels(pred_labels)
    ax.set_yticklabels(pred_labels)

    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')

    plt.show()


def main_func(model_id):
    result_df = get_results_df(model_id)
    result_df['errorPercentage'] = result_df['errorPercentage'] * 100
    # get_reports_and_con_matrix(result_df['classPred'], result_df['realClass'])
    scores_df = []
    for score in [0.5, 0.6, 0.7, 0.8, 0.9]:
        scores_df.append(get_metrics_by_score(score, result_df))
    scores_df = pd.DataFrame(scores_df)
    scores_df['totalImages'] = len(result_df.index)
    scores_df.to_csv(f'./final_scores_{model_id_names[model_id]}.csv')
    return scores_df


scores_df_1 = main_func('ICN2123603354956333056')
scores_df_2 = main_func('ICN8969778476001263616')
