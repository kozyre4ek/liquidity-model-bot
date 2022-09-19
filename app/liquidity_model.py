from io import BytesIO
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import matplotlib.pyplot as plt


_means: np.ndarray = np.array([
    0.4941440511815086, 9703.259364358682, 0,
    0, 0, 0, 230534.13597966195, 0.12546413346787122,
    1.8618563615725932, 52.13388298421216, 0
])

_scales: np.ndarray = np.array([
    0.6142109341696292, 5090.8411462060185, 1,
    1, 1, 1, 80712.97587359276, 0.1554743064414065,
    0.9055493508782385, 19.92122528392386, 1
])

_coefs: np.ndarray = np.array([
    -0.5248492071469213, -0.09023562086498407, -0.29678954404102603,
    0.37385186157300837, 0.5650289765469102, -0.448030002900798,
    0.22414266411454462, 0.3252123014984028, 0.18388557099238484,
    0.2783085210710162, -0.3347904312791998
])

_intercept: float = -2.94578939

_feature_names = [
    'call_cnt_per_day', 'city_cent_meters', 'is_msk',
    'isalternative', 'isapartments', 'isjk', 'price_sqm',
    'price_sqm_model_diff_rate', 'roomscount', 'totalarea',
    'vas_rate'
]

def _which_interval(pred: float) -> int:
    if pred > 0 and pred <= 0.0277:
        return 0
    elif pred > 0.0277 and pred <= 0.0419:
        return 1
    elif pred > 0.0419 and pred <= 0.0635:
        return 2
    else:
        return 3

_interval_names = {
    0: 'Отличная',
    1: 'Хорошая',
    2: 'Средняя',
    3: 'Выше рынка'
}

_bins_mean = [
    0.013864459389549923,
    0.03053670573719926,
    0.05512542582842985,
    0.10943629981416478
]

def scale(obj: np.ndarray) -> np.ndarray:
    return (obj - _means) / _scales

def sigmoid(x: Union[np.ndarray, float]) -> Union[np.ndarray, float]:
    return 1 / (1 + np.exp(-x))

def predict(obj: np.ndarray) -> Union[np.ndarray, float]:
    obj = np.asarray(obj)
    scaled_object = scale(obj)
    preds = sigmoid(scaled_object.dot(_coefs) + _intercept)
    return preds

def report(features: Dict[str, Any], cost_price: float=0.00053) -> List[Tuple[Any]]:
    # альтернативная сделка (isalternative=1, vas_rate=0.5, call_cnt_per_day=0.25)
    # скидка 0-30% (isalternative=0, vas_rate=1, call_cnt_per_day=0.5 + price_sqm)
    # возвращаем предикт, бин, скидку, кост
    features['isalternative'] = 1
    features['vas_rate'] = 0.5
    features['call_cnt_per_day'] = 0.25
    pred_bad = predict([[features[feat] for feat in _feature_names]])[0]

    features['isalternative'] = 0
    features['vas_rate'] = 1
    features['call_cnt_per_day'] = 0.5
    pred_good = predict([[features[feat] for feat in _feature_names]])[0]
    cost_good = cost(pred_good, features['price'], cost_price, 0, 180)

    old_price = features['price_sqm']
    model_price = features['price_sqm'] / (1 + features['price_sqm_model_diff_rate'])
    price_chs = list(range(1, 31))
    costs = []
    preds = []
    for price_ch in price_chs:
        features['price_sqm'] = old_price * (1 - price_ch / 100)
        features['price_sqm_model_diff_rate'] = features['price_sqm'] / model_price - 1
        pred = predict([[features[feat] for feat in _feature_names]])[0]
        preds.append(pred)
        costs.append(cost(pred, features['price_sqm'] * features['totalarea'], cost_price, price_ch / 100, 180))
    costs_profit = [cost_good / cost - 1 for cost in costs]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(price_chs, costs_profit)
    ax.set_xlabel('Дисконт')
    ax.set_title('Средняя выгода для клиента в пересчете на весь срок продажи, %')
    plt.grid()
    plot_file = BytesIO()
    fig.savefig(plot_file, format='png')
    plot_file.seek(0)

    cost_best_idx = np.argmax(costs_profit)

    return {
        'bad': {
            'pred': pred_bad
        },
        'good': {
            'pred': pred_good,
            'bin': _interval_names[_which_interval(pred_good)]
        },
        'best': {
            'pred': preds[cost_best_idx],
            'price_ch': price_chs[cost_best_idx],
            'cost_diff': costs_profit[cost_best_idx]
        },
        'plot': plot_file
    }




def cost(pred: float, price_sqm: float, cost_per_day: float, price_change: float=0, max_days: int=180) -> float:
    return _bins_mean[_which_interval(pred)] * price_sqm * ((1 - price_change) * cost_per_day * max_days + price_change)