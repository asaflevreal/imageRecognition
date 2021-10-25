import pandas as pd
from catboost import CatBoostRegressor

from importantDates import last_year
from mongoConnect import property_collection

columns_dict = {'_id': 0, 'kitchen': 1, 'bathroom': 1,
                'listingAmenities': 1, 'numOfRooms': 1, 'numOfBaths': 1, 'numOfBeds': 1, 'squareFt': 1, 'salePrice': 1,
                'isRenovated': 1, 'ourRank': 1}  # can add areas, building kind

property_with_sqft = list(
    property_collection.find(
        {'squareFt':
             {'$exists': True},
         'enhancedYN': True,
         'numOfBeds': {'$in':[0, 1]},
         'isRenovated': {'$exists': True},
         'createdAt': {'$gte': last_year},
         'isSquareFtApproximate': {'$ne': True},
         'category': 'APT_SALE',
         }, columns_dict).limit(100000))


def feature_engeneering(property_with_sqft):
    property_with_sqft['washerInUnit'] = property_with_sqft['listingAmenities'].apply(
        lambda x: x.get('washerOrDrier', {}).get('washerOrDrierInUnit'))

    property_with_sqft['hasCourtyard'] = property_with_sqft['listingAmenities'].apply(lambda x: x.get('courtyardYN'))
    property_with_sqft['hasTerrace'] = property_with_sqft['listingAmenities'].apply(lambda x: x.get('courtyardYN'))
    property_with_sqft['hasPrivateOutDoor'] = property_with_sqft['listingAmenities'].apply(
        lambda x: x.get('privateOutdoorSpace'))
    property_with_sqft['hasBathtub'] = property_with_sqft['bathroom'].apply(lambda x: x.get('hasBathtub'))
    property_with_sqft['isOpenKitchen'] = property_with_sqft['kitchen'].apply(lambda x: x.get('isOpenKitchen'))
    for col in ['washerInUnit', 'hasCourtyard', 'hasTerrace', 'hasPrivateOutDoor', 'hasBathtub', 'isOpenKitchen']:
        property_with_sqft[col] = property_with_sqft[col].fillna(value=0)
    property_with_sqft.drop(columns=['listingAmenities', 'kitchen', 'bathroom', 'salePrice'], inplace=True)


def map_to_numbers(x):
    if x == 'YES_LARGE':
        return 2
    if x in ['YES', True]:
        return 1
    if x == 'YES_SMALL':
        return 0.75
    if x == 'MAYBE':
        return 0.5
    if x in ['NO', False]:
        return 0
    else:
        return x


property_with_sqft = pd.DataFrame(property_with_sqft)
feature_engeneering(property_with_sqft)
property_with_sqft = property_with_sqft.applymap(lambda x: map_to_numbers(x))


def split_to_train_and_test(data, size_of_train):
    shuffle_df = data.sample(frac=1)
    train_size = int(size_of_train * len(data))
    train_set = shuffle_df[:train_size]
    test_set = shuffle_df[train_size:]
    return train_set, test_set


train_set, test_set = split_to_train_and_test(property_with_sqft, size_of_train=0.8)
X_train = train_set.drop(columns=['squareFt'])
y_train = train_set['squareFt']

X_test = test_set.drop(columns=['squareFt'])
y_test = test_set['squareFt']
model = CatBoostRegressor()
model.fit(X_train, y_train)
test_set['pred'] = model.predict(X_test)
test_set['Error'] = abs(test_set['pred'] - test_set['squareFt'])
print(test_set['Error'].median())
