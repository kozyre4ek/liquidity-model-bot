import pytest

from context import utils


def test_geocoder():
    assert utils.geocoder('Москва, Ясеневая ул., 28') == 85937
    assert utils.geocoder('Улица пушкина дом колотушкина') is None

@pytest.fixture
def infra_params():
    return {
        'realty_id': 85937,
        'city_cent_meters': 18116,
        'date': '2022-02-01',
    }

def test_get_city_center(infra_params):
    assert utils.get_city_cent_meters(infra_params['realty_id'], infra_params['date']) == infra_params['city_cent_meters']
    assert utils.get_city_cent_meters(0, infra_params['date']) is None

@pytest.fixture
def val_model_params():
    return {
        'realty_id': 85937,
        'floor': 'Другой',
        'repairtype': 'Косметический',
        'roomscount': '1',
        'date': '2022-08-29',
        'price_sqm': 300000,
        'price_sqm_model_diff_rate': 0.191
    }

def test_get_price_sqm_model_diff_rate(val_model_params):
    price_sqm_model_diff_rate = utils.get_price_sqm_model_diff_rate(val_model_params, val_model_params['date'])
    assert round(price_sqm_model_diff_rate, 3) == round(val_model_params['price_sqm_model_diff_rate'], 3)
    val_model_params['realty_id'] = 0
    assert utils.get_price_sqm_model_diff_rate(val_model_params, val_model_params['date']) is None