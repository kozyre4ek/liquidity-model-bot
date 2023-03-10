import numpy as np
import pytest


from context import liquidity_model


@pytest.fixture
def object():
    # 266011978
    return np.array([[
        0.14285714285714285, 18116, 1, 0, 0, 0,
        229118.30942255177, 0.032683136395010394, 2, 46.8, 1.0
    ]])

@pytest.fixture
def scaled_object():
    # 266011978
    return np.array([[
        -0.5719320330877558, 1.6525246799167885, 1, 0, 0, 0,
        -0.0175414986473495, -0.5967609645380674, 0.1525523024155774,
        -0.26774874076227256, 1.0
    ]])

def test_scale(object, scaled_object):
    np.testing.assert_allclose(liquidity_model.scale(object), scaled_object, rtol=1e-05)

def test_predict(object):
    np.testing.assert_allclose(liquidity_model.predict(object), np.array([0.0248246]), rtol=1e-05)

def test_cost():
    assert int(liquidity_model.cost(0.056, 341_429, 53e-5, 0.2)) == 5_200
    assert int(liquidity_model.cost(0.056, 341_429, 53e-5)) == 1_795

def test_which_interval():
    assert liquidity_model._which_interval(0.01) == 0
    assert liquidity_model._which_interval(0.0419) == 1
    assert liquidity_model._which_interval(0.05) == 2
    assert liquidity_model._which_interval(0.99) == 3