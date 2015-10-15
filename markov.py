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
            use_emissions: allows to turn off the expensive nltk tagging
    """

    def __init__(self, corpus, order=1, use_emissions=True):
        """ Initializes the Markov Chain with a given corpus and order """
        assert order >= 1, "Invalid Markov chain order"
        assert order <= 20, "Markov chain order too high"
        assert corpus is not None, "Corpus is empty"
        self.order = order
        self._start_symbol = '^'
        self._end_symbol = '$'
        self._use_emissions = use_emissions
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
            if self._use_emissions:
                tokens = pos_tag(word_tokenize(corpus_entry[0]))
            else:
                tokens = ((w, None) for w in word_tokenize(corpus_entry[0]))

            rating = corpus_entry[1] if len(corpus_entry) > 1 else 1
            last_tokens = utils.prefilled_buffer(
                self._start_symbol, length=self.order)
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

    def _text_generator(self, emit=lambda x, _: x):
        last_tokens = utils.prefilled_buffer(
            self._start_symbol, length=self.order)
        generated_tokens = []
        while last_tokens[-1] != self._end_symbol:
            new_token = self._generate_next_token(last_tokens)
            generated_tokens.append(emit(new_token, last_tokens))
            last_tokens.append(new_token)
        text = generated_tokens[:-1]
        return utils.join_tokens_to_sentences(text)

    def generate_text(self, generation_type='markov'):
        """ Generates sentences from a given corpus
        TODO:
            we DONT limit the sentence length
        Args:
            generation_type: 'markov' | 'hmm'
        Returns:
            Properly formatted string of generated sentences
        """
        assert generation_type in ['markov', 'hmm']
        if generation_type == "markov":
            return self._text_generator()
        elif generation_type == "hmm":
            return self._text_generator(emit=self._emitHMM)

    def _emitHMM(self, new_token, past):
        token_type = pos_tag([new_token])[0][1]
        assert token_type in self.emissions
        return self._weighted_choice(self.emissions[token_type].items(),
                                     probability_sum=sum(self.emissions[token_type].values()))

    def _generate_next_token(self, past):
        key = tuple(past)
        assert key in self.transitions, "%s" % str(key)
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
