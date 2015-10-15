from copy import deepcopy
from itertools import chain
from nltk import word_tokenize
import random
from collections import deque, defaultdict

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


class Markov:
    """
    A simple markov chain implementation
    """

    def __init__(self, corpus, order=1):
        """
        """
        self.order = order
        self._start_symbol = '^'
        self._end_symbol = '$'
        self.transitions = self._compute_transitions(corpus, self.order)

    def _compute_transitions(self, corpus, order=1):
        """
        generates the transition probabilities of a corpus
        :param corpus: the given corpus (a corpus_entry needs to be a tuple or array)
        :param order: the maximal order
        :return: transition probabilities
        """
        transitions = defaultdict(lambda: defaultdict(int))
        distinct_tokens = set()

        for corpus_entry in corpus:
            if corpus_entry[0] is None:
                # there are invalid entries
                continue
            tokens = word_tokenize(corpus_entry[0])
            rating = corpus_entry[1] if len(corpus_entry) > 1 else 1
            # efficient circular buffer
            last_tokens = deque([self._start_symbol] * order, maxlen=order)
            # count the occurences of "present | past"
            for token in chain(tokens, [self._end_symbol]):
                distinct_tokens.add(token)
                past = tuple(last_tokens)
                for suffix in (past[i:] for i in range(len(past))):
                    transitions[suffix][token] += rating

                last_tokens.append(token)

        # compute probabilities
        for transition_counts in transitions.values():
            summed_occurences = sum(transition_counts.values())
            for token in transition_counts.keys():
                transition_counts[token] /= summed_occurences

        # ensure there is a probability
        # WHY? do we do that? leads to a loop?
        for token in distinct_tokens:
            if (token,) not in transitions:
                transitions[(token,)] = {token: 1}

        return transitions

    def _weighted_choice(self, item_probabilities, value_to_probability=lambda x: x, probability_sum=1):
        """ Expects a list of (item, probability)-tuples and the sum of all probabilities and returns one entry weighted at random """
        random_value = random.random() * probability_sum
        summed_probability = 0
        for item, value in item_probabilities:
            summed_probability += value_to_probability(value)
            if summed_probability > random_value:
                return item

    def generate_text(self, count):
        last_tokens = [self._start_symbol] * self.order
        generated_tokens = []
        while last_tokens[-1] != self._end_symbol:
            new_token = self.generate_next_token(tuple(last_tokens))
            last_tokens = last_tokens[1:]
            last_tokens.append(new_token)
            generated_tokens.append(new_token)

        return generated_tokens[:-1]

    def generate_next_token(self, past, precondition=lambda x: True):
        for key in [past[i:] for i in range(len(past))]:
            if key in self.transitions:
                possible_transitions = deepcopy(self.transitions[key])
                for key in self.transitions[key].keys():
                    if not precondition(key):
                        del possible_transitions[key]
                return self._weighted_choice(possible_transitions.items(), probability_sum=sum(possible_transitions.values()))
