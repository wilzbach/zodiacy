from itertools import chain
from nltk import word_tokenize
import random
from collections import deque, defaultdict
import utils

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


class Markov:
    """ A simple markov chain implementation

        Attributes:
            corpus: the given corpus (a corpus_entry needs to be a tuple or array)
            order: the maximal order
    """

    def __init__(self, corpus, order=1):
        """ Inits the Markov Chain with a given corpus and order """
        self.order = order
        self._start_symbol = '^'
        self._end_symbol = '$'
        self.transitions = self._compute_transitions(corpus, self.order)

    def _compute_transitions(self, corpus, order=1):
        """ Generates the transition probabilities of a corpus
        :param corpus: the given corpus (a corpus_entry needs to be a tuple or array)
        :param order: the maximal order
        :returns: transition probabilities
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
                for suffix in utils.get_suffixes(last_tokens):
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

    def generate_text(self, nr_of_entries):
        """ Generates sentences from a given corpus
        TODO: we DONT limit
        Args:
            nr_of_entries: Maximal number of entries to generate
        """
        last_tokens = deque([self._start_symbol] * self.order, maxlen=self.order)
        generated_tokens = []
        while last_tokens[-1] != self._end_symbol:
            new_token = self._generate_next_token(last_tokens)
            last_tokens.append(new_token)
            generated_tokens.append(new_token)

        return generated_tokens[:-1]

    def _generate_next_token(self, past):
        for key in utils.get_suffixes(past):
            if key in self.transitions:
                return self._weighted_choice(self.transitions[key].items(),
                        probability_sum=sum(self.transitions[key].values()))

    def _weighted_choice(self, item_probabilities, value_to_probability=lambda x: x, probability_sum=1):
        """ Expects a list of (item, probability)-tuples and the sum of all probabilities and returns one entry weighted at random """
        random_value = random.random() * probability_sum
        summed_probability = 0
        for item, value in item_probabilities:
            summed_probability += value_to_probability(value)
            if summed_probability > random_value:
                return item
