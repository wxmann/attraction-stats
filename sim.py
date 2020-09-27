from random import random, shuffle, betavariate, sample
from curve import random_attraction_curve, shift_attraction_curve
from functools import partial


class Person:
    def __init__(self, index, sex, attractiveness, attraction_curve):
        self.index = index
        self.sex = sex
        self.attractiveness = attractiveness
        self.attraction_curve = attraction_curve
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


def init_pool(n, sex, attraction_curve, attractiveness_func):
    ppl = []
    if attraction_curve is None:
        attraction_curve = random_attraction_curve
    for i in range(n):
        attractiveness = attractiveness_func()
        attraction_curve_result = attraction_curve(attractiveness)
        new_person = Person(i, sex, attractiveness=attractiveness, attraction_curve=attraction_curve_result)
        ppl.append(new_person)
    return ppl


class Simulation:
    def __init__(self, n_males, n_females, cycle_factor=0.02, attraction_curve=None, attractiveness_dist='normal'):
        self.cycle = 0
        if attractiveness_dist == 'normal':
            # beta distribution at alpha=4 and beta=4 is roughly normal and constrained to [0, 1]
            attractiveness_func = partial(betavariate, alpha=4, beta=4)
        else:
            attractiveness_func = random

        self.male_pool = init_pool(n_males, 'm', attraction_curve, attractiveness_func)
        self.female_pool = init_pool(n_females, 'f', attraction_curve, attractiveness_func)
        for male in self.male_pool:
            male.init_candidates(self.female_pool)
        for female in self.female_pool:
            female.init_candidates(self.male_pool)

        self.matches = []
        self.cycle_factor = cycle_factor

    def recalc_attraction_curve(self, person):
        person.attraction_curve = shift_attraction_curve(person.attraction_curve, shift=-self.cycle_factor)

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
            self.recalc_attraction_curve(male)
        for female in self.female_pool:
            self.recalc_attraction_curve(female)
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
