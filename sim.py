from random import random, shuffle, betavariate, sample
from functools import partial

from curves import generators, evolvers


class Person:
    def __init__(self, index, sex, attractiveness, attraction_curve, curve_evolver):
        self.index = index
        self.sex = sex
        self.attractiveness = attractiveness
        self.attraction_curve = attraction_curve
        self.curve_evolver = curve_evolver
        self.choices = []
        self.candidates = set()

    def init_candidates(self, people):
        self.candidates = set(people)

    def select_candidates(self, n, test_attraction=True):
        selection = sample(self.candidates, min(n, len(self.candidates)))
        if not test_attraction:
            return selection
        return [p for p in selection if self.is_attracted_to(p)]

    def remove_candidate(self, person):
        if person in self.candidates:
            self.candidates.remove(person)

    def add_choice(self, person):
        self.choices.append(person)

    def evaluate_choices(self):
        selected_person = None
        for person in self.choices:
            if person in self.candidates:
                self.remove_candidate(person)
                person.remove_candidate(self)
                if self.is_attracted_to(person):
                    selected_person = person
                    break
        self.choices = []
        return selected_person

    def is_attracted_to(self, other_person):
        p_attraction = self.attraction_curve(other_person.attractiveness)
        return random() < p_attraction

    def update_attraction_curve(self, sim):
        self.attraction_curve = self.curve_evolver(self, sim)
        # print(f'person: {str(self)}, cycle: {sim.cycle}, curve: {str(self.attraction_curve)})

    def __hash__(self):
        return hash((self.index, self.sex))

    def __eq__(self, other):
        return self.index == other.index and self.sex == other.sex

    def __str__(self):
        return f'<Person index: {self.index} sex: {self.sex}, attractiveness: {self.attractiveness}>'


class Match:
    def __init__(self, male, female, cycle):
        self.male = male
        self.female = female
        self.cycle = cycle

    def __str__(self):
        return f'{self.male} matches with {self.female} at cycle {self.cycle}'


def init_pool(n, sex, attractiveness_dist, curve_generator, curve_evolver):
    ppl = []
    for i in range(n):
        attractiveness = attractiveness_dist()
        # print('attractiveness ' + str(attractiveness))
        attraction_curve_result = curve_generator(attractiveness)
        # print('attraction curve result ' + str(attraction_curve_result))
        new_person = Person(i, sex, attractiveness=attractiveness,
                            attraction_curve=attraction_curve_result, curve_evolver=curve_evolver)
        ppl.append(new_person)
    return ppl


class Simulation:
    def __init__(self, n_males, n_females, male_params=None, female_params=None):
        self.cycle = 0

        if male_params is None:
            male_params = Simulation.default_params()
        if female_params is None:
            female_params = Simulation.default_params()

        self.male_pool = init_pool(n_males, 'm', **male_params)
        self.female_pool = init_pool(n_females, 'f', **female_params)

        for male in self.male_pool:
            male.init_candidates(self.female_pool)
        for female in self.female_pool:
            female.init_candidates(self.male_pool)

        self.matches = []

    @staticmethod
    def default_params(attractiveness_dist='normal', curve_generator=None, curve_evolver=None):
        if attractiveness_dist == 'normal':
            # beta distribution at alpha=4 and beta=4 is roughly normal and constrained to [0, 1]
            attractiveness_dist = partial(betavariate, alpha=4, beta=4)
        else:
            attractiveness_dist = random

        if curve_generator is None:
            curve_generator = generators.attractiveness_dependent(starting_width=4, shift_factor=1.25,
                                                                  shift_noise=1.25)

        if curve_evolver is None:
            curve_evolver = evolvers.cycle_decreasing(decrement=0.02)

        return {
            'attractiveness_dist': attractiveness_dist,
            'curve_generator': curve_generator,
            'curve_evolver': curve_evolver
        }

    def remove_from_pool(self, person):
        if person.sex == 'm':
            self.male_pool.remove(person)
            for female in self.female_pool:
                female.remove_candidate(person)
        else:
            self.female_pool.remove(person)
            for male in self.male_pool:
                male.remove_candidate(person)

    def step(self):
        raise NotImplementedError

    def poststep(self):
        self.cycle += 1
        for male in self.male_pool:
            male.update_attraction_curve(self)
        for female in self.female_pool:
            female.update_attraction_curve(self)
        shuffle(self.male_pool)
        shuffle(self.female_pool)

    def run(self, steps):
        for _ in range(steps):
            self.step()
            self.poststep()


class TinderSimulation(Simulation):
    def step(self):
        people_to_remove = []

        for male in self.male_pool:
            choices = male.select_candidates(10)
            for female in choices:
                female.add_choice(male)

        for female in self.female_pool:
            selected_male = female.evaluate_choices()
            if selected_male is not None:
                # male *must* be removed from pool here so he doesn't match up with other females
                self.remove_from_pool(selected_male)
                self.matches.append(Match(selected_male, female, self.cycle))
                people_to_remove.append(female)

        for person in people_to_remove:
            self.remove_from_pool(person)
