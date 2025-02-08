import numpy as np

class Consensus:
    def __init__(self):
        self.stakers = {}  # Pemegang saham
        self.validators = []  # Validator jaringan

    def stake(self, address, amount):
        """ Menambahkan stake untuk delegasi DPoS """
        if address in self.stakers:
            self.stakers[address] += amount
        else:
            self.stakers[address] = amount

    def select_validators(self):
        """ Pemilihan validator berbasis AI-PoS """
        stake_values = np.array(list(self.stakers.values()))
        probability = stake_values / stake_values.sum()
        selected = np.random.choice(list(self.stakers.keys()), size=5, p=probability)
        self.validators = selected.tolist()
        return self.validators
