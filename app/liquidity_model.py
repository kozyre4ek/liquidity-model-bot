from typing import Union

import numpy as np


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

def scale(obj: np.ndarray) -> np.ndarray:
    return (obj - _means) / _scales

def sigmoid(x: Union[np.ndarray, float]) -> Union[np.ndarray, float]:
    return 1 / (1 + np.exp(-x))

def predict(obj: np.ndarray) -> Union[np.ndarray, float]:
    obj = np.asarray(obj)
    scaled_object = scale(obj)
    preds = sigmoid(scaled_object.dot(_coefs) + _intercept)
    return preds