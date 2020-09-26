from random import random, shuffle
from curve import random_attraction_curve, shift_attraction_curve


class Person:
    @classmethod
    def random(cls, index, sex, attraction_curve=None):
        attractiveness = random()
        if not attraction_curve:
            attraction_curve = random_attraction_curve(attractiveness)
        return Person(index, sex, attractiveness=attractiveness, attraction_curve=attraction_curve)

    def __init__(self, index, sex, attractiveness, attraction_curve):
        self.index = index
        self.sex = sex
        self.attractiveness = attractiveness
        self.attraction_curve = attraction_curve

    def is_attracted_to(self, other_person):
        p_attraction = self.attraction_curve(other_person.attractiveness)
        return random() < p_attraction

    def __str__(self):
        return f'<Person index: {self.index} sex: {self.sex}, attractiveness: {self.attractiveness}>'


class Match:
    def __init__(self, male, female, cycle):
        self.male = male
        self.female = female
        self.cycle = cycle

    def __str__(self):
        return f'{self.male} matches with {self.female} at cycle {self.cycle}'


def init_pool(n, sex, attraction_curve):
    return [Person.random(i, sex, attraction_curve) for i in range(n)]


class Simulation:
    def __init__(self, n_males, n_females, cycle_factor=0.02, attraction_curve=None):
        self.cycle = 0
        self.male_pool = init_pool(n_males, 'm', attraction_curve)
        self.female_pool = init_pool(n_females, 'f', attraction_curve)
        self.matches = []
        self.cycle_factor = cycle_factor

    def determine_match(self, male, female):
        if male.is_attracted_to(female) and female.is_attracted_to(male):
            self.matches.append(Match(male, female, self.cycle))
            self.male_pool.remove(male)
            self.female_pool.remove(female)
            return True
        return False

    def recalc_attraction_curve(self, person):
        person.attraction_curve = shift_attraction_curve(person.attraction_curve, shift=-self.cycle_factor)

    def step(self):
        for male, female in zip(self.male_pool, self.female_pool):
            matched = self.determine_match(male, female)
            if not matched:
                self.recalc_attraction_curve(male)
                self.recalc_attraction_curve(female)
        self.cycle += 1
        shuffle(self.male_pool)
        shuffle(self.female_pool)

    def run(self, steps):
        for _ in range(steps):
            self.step()
