import random

from curves.base import shift_betainc_params, betainc_attraction_curve


def attractiveness_dependent(starting_width=4, shift_factor=1.25, shift_noise=1.25):
    def func(attractiveness):
        if shift_factor >= starting_width:
            raise ValueError('Cannot have curve shift >= curve width')

        shift = shift_factor * (attractiveness - 0.5) / 0.5
        noise = random.gauss(mu=0, sigma=shift_noise)
        a, b = shift_betainc_params(starting_width, starting_width, shift + noise)

        return betainc_attraction_curve(a, b)

    return func
