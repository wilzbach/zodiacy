from collections import defaultdict
from itertools import chain
import warnings
import random
import utils
with warnings.catch_warnings(record=True):
    # we need to workaround the Python bug due to simplefilter('ignore')
    warnings.filterwarnings("always", category=DeprecationWarning)
    from nltk import word_tokenize, pos_tag

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
        self._compute_transitions(corpus, self.order)

    def _compute_transitions(self, corpus, order=1):
        """ Generates the transition probabilities of a corpus
        Args:
            corpus: the given corpus (a corpus_entry needs to be a tuple or array)
            order: the maximal order
        Returns:
            transition probabilities
        """
        self.transitions = defaultdict(lambda: defaultdict(float))
        self.emissions = defaultdict(lambda: defaultdict(float))

        for corpus_entry in corpus:
            if corpus_entry[0] is None:
                # there are invalid entries
                continue
            tokens = pos_tag(word_tokenize(corpus_entry[0]))
            rating = corpus_entry[1] if len(corpus_entry) > 1 else 1
            last_tokens = utils.prefilled_buffer(self._start_symbol, length=self.order)
            # count the occurrences of "present | past"
            for token in chain(tokens, [self._end_symbol * 2]):
                token_value = token[0]
                token_type = token[1]
                for suffix in utils.get_suffixes(last_tokens):
                    self.transitions[suffix][token_value] += rating
                    self.emissions[token_type][token_value] += rating

                last_tokens.append(token_value)

        # compute probabilities
        for transition_counts in self.transitions.values():
            summed_occurences = sum(transition_counts.values())
            for token in transition_counts.keys():
                transition_counts[token] /= summed_occurences

    def generate_text(self, nr_of_entries):
        """ Generates sentences from a given corpus
        TODO:
            we DONT limit
        Args:
            nr_of_entries: Maximal number of entries to generate
        Returns:
            Properly formatted string of generated sentences
        """
        last_tokens = utils.prefilled_buffer(self._start_symbol, length=self.order)
        generated_tokens = []
        while last_tokens[-1] != self._end_symbol:
            new_token = self._generate_next_token(last_tokens)
            last_tokens.append(new_token)
            generated_tokens.append(new_token)

        text = generated_tokens[:-1]
        return utils.join_tokens_to_sentences(text)

    def generate_hmm(self):
        """ Generates sentences from a given corpus using an HMM
        Returns:
            Properly formatted string of generated sentences
        """
        last_tokens = utils.prefilled_buffer(self._start_symbol, length=self.order)
        generated_tokens = []
        while last_tokens[-1] != self._end_symbol:
            new_token = self._generate_next_token(last_tokens)
            last_tokens.append(new_token)
            generated_tokens.append(new_token)

        text = generated_tokens[:-1]
        return utils.join_tokens_to_sentences(text)

    def _generate_next_token(self, past):
        for key in utils.get_suffixes(past):
            if key in self.transitions:
                return self._weighted_choice(self.transitions[key].items(),
                                             probability_sum=sum(self.transitions[key].values()))

    def _weighted_choice(self, item_probabilities,
                         value_to_probability=lambda x: x, probability_sum=1):
        """ Expects a list of (item, probability)-tuples
        and the sum of all probabilities and returns one entry weighted at random
        """
        random_value = random.random() * probability_sum
        summed_probability = 0
        for item, value in item_probabilities:
            summed_probability += value_to_probability(value)
            if summed_probability > random_value:
                return item
