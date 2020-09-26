from scipy.special import betainc
import random


def random_attraction_curve(attractiveness, curve_width=4, attractiveness_shift=1.25, shift_noise=1.25):
    if attractiveness_shift >= curve_width:
        raise ValueError('Cannot have curve shift >= curve width')

    shift = attractiveness_shift * (attractiveness - 0.5) / 0.5
    noise = random.gauss(mu=0, sigma=shift_noise)
    a, b = shift_betainc_params(curve_width, curve_width, shift + noise)

    return betainc_attraction_curve(a, b)


def shift_attraction_curve(curve, shift):
    a, b = curve.params['a'], curve.params['b']
    new_a, new_b = shift_betainc_params(a, b, shift)
    return betainc_attraction_curve(new_a, new_b)


def shift_betainc_params(a, b, shift, floor_val=0.1):
    if a + shift < 0:
        shift = floor_val - a
    if b - shift < 0:
        shift = b - floor_val
    return a + shift, b - shift


def betainc_attraction_curve(a, b):
    return NumpyAttractionCurve(params=dict(a=a, b=b), np_ufunc=betainc)


class NumpyAttractionCurve:
    def __init__(self, params, np_ufunc):
        self.params = params
        self.curve_func = np_ufunc

    def __call__(self, attractiveness):
        return self.curve_func(*self.params.values(), attractiveness)

    def __str__(self):
        return f'<Attraction curve func={self.curve_func.__name__}, params={str(self.params)}'
