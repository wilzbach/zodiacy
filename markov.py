from collections import defaultdict
from itertools import chain
import warnings
import logging
import random
import utils
with warnings.catch_warnings(record=True):
    # we need to workaround the Python bug due to simplefilter('ignore')
    warnings.filterwarnings("always", category=DeprecationWarning)
    from nltk import word_tokenize, pos_tag
    from nltk.corpus import wordnet as wn

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

TOKENS_FOR_SYNONYMS = ["VB", "JJ", "NN", "RB"]
logger = logging.getLogger('root')


class Markov:
    """ A simple markov chain implementation

        Attributes:
            corpus: given corpus (a corpus_entry needs to be a tuple or array)
            order: maximal order to look back for a given state
            use_emissions: allows to turn off the expensive nltk tagging
            order_emissions: maximal order to look back at previous emissions for a given emission (only HMM)
            prob_hmm_states: When using previous states and emissions,
                                weight for the previous states (only HMM)
            prob_hmm_emissions: When using previous states and emissions,
                                weight for the previous emissions (only HMM)
            use_synonyms:
            prob_use_synonyms:
    """

    def __init__(self, corpus, order=1, use_emissions=True, order_emissions=1,
                 prob_hmm_states=0.5, prob_hmm_emissions=0.5, use_synonyms=False,
                 prob_use_synonyms=0.1):
        """ Initializes the Markov Chain with a given corpus and order """
        assert order >= 1, "Invalid Markov chain order"
        assert order <= 20, "Markov chain order too high"
        assert corpus is not None, "Corpus is empty"
        self.order = order
        self._start_symbol = '^'
        self._end_symbol = '$'
        self._use_emissions = use_emissions
        self._compute_transitions(corpus, self.order)
        self.order_emissions = order_emissions
        self.prob_hmm_states = prob_hmm_states
        self.prob_hmm_emissions = prob_hmm_emissions
        if self._use_emissions:
            self._compute_emissions(corpus, self.order)

        self.use_synonyms = use_synonyms
        self.prob_use_synonyms = prob_use_synonyms

    def _compute_transitions(self, corpus, order=1):
        """ Computes the transition probabilities of a corpus
        Args:
            corpus: the given corpus (a corpus_entry needs to be iterable)
            order: the maximal Markov chain order
        """
        self.transitions = defaultdict(lambda: defaultdict(int))

        for corpus_entry in corpus:
            tokens = utils.expanding_words(word_tokenize(corpus_entry[0]))

            rating = corpus_entry[1] if len(corpus_entry) > 1 else 1
            last_tokens = utils.prefilled_buffer(
                self._start_symbol, length=self.order)
            # count the occurrences of "present | past"
            for token_value in chain(tokens, self._end_symbol):
                for suffix in utils.get_suffixes(last_tokens):
                    self.transitions[suffix][token_value] += rating

                last_tokens.append(token_value)

        self._compute_relative_probs(self.transitions)

    def _compute_emissions(self, corpus, order=1):
        """ Computes the emissions and transitions probabilities of a corpus
            based on word types
        Args:
            corpus: the given corpus (a corpus_entry needs to be iterable)
            order: the maximal Markov chain order
        Computes:
            self.emissions: Probabilities to emit word (token_value) at state x (token_type)
            self.transitions_hmm: Transition probabilities to switch between states (token_type)
            self.emissions_past: Probabilities to emit a word (token_value) at state x
                                 (token_type) based on previous emissions (token_value)
        """
        self.emissions = defaultdict(lambda: defaultdict(int))
        self.transitions_hmm = defaultdict(lambda: defaultdict(int))
        self.emissions_past = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int)))

        for corpus_entry in corpus:
            tokens = pos_tag(
                list(utils.expanding_words(word_tokenize(corpus_entry[0]))))

            rating = corpus_entry[1] if len(corpus_entry) > 1 else 1
            last_tokens = utils.prefilled_buffer(
                self._start_symbol, length=self.order)
            last_emissions = utils.prefilled_buffer(
                self._start_symbol, length=self.order_emissions)

            for token in chain(tokens, [[self._end_symbol] * 2]):
                token_value = token[0]
                token_type = token[1]

                for suffix in utils.get_suffixes(last_tokens):
                    self.transitions_hmm[suffix][token_type] += rating
                    self.emissions[token_type][token_value] += rating

                for suffix in utils.get_suffixes(last_emissions):
                    self.emissions_past[token_type][
                        suffix][token_value] += rating

                last_tokens.append(token_type)
                last_emissions.append(token_value)

        self._compute_relative_probs(self.emissions)
        self._compute_relative_probs(self.transitions_hmm)
        for val in self.emissions_past.values():
            self._compute_relative_probs(val)

    def _compute_relative_probs(self, prob_dict):
        """ computes the relative probabilities for every state """
        for transition_counts in prob_dict.values():
            summed_occurences = sum(transition_counts.values())
            for token in transition_counts.keys():
                transition_counts[token] = transition_counts[
                    token] * 1.0 / summed_occurences

    def _text_generator(self, next_token=None, emit=lambda x, _, __: x):
        """ loops from the start state to the end state and records the emissions
        Tokens are joint to sentences by looking ahead for the next token type"""
        assert next_token is not None
        last_tokens = utils.prefilled_buffer(
            self._start_symbol, length=self.order)
        last_emissions = utils.prefilled_buffer(
            self._start_symbol, length=self.order_emissions)
        generated_tokens = []
        while last_tokens[-1] != self._end_symbol:
            new_token = next_token(last_tokens)
            emission = emit(new_token, last_tokens, last_emissions)
            last_tokens.append(new_token)
            last_emissions.append(emission)
            if self.use_synonyms:
                if random.random() > self.prob_use_synonyms:
                    emission = self._search_synonym(emission)
            generated_tokens.append(emission)
        text = generated_tokens[:-1]
        return utils.join_tokens_to_sentences(text)

    def _search_synonym(self, word):
        """ Tries to find synonyms using the wordnet API
        Only searches synonyms for verbs (VB), adjectives (JJ), nouns (NN)
        and adverbs(RB).
        The synonym is randomly chosen from all available ones.

        Args:
            word: word to replace with a synonym
        Returns:
            synonym if we found a synonym
            word if there are no synonyms
        """
        if pos_tag([word])[0][1] in TOKENS_FOR_SYNONYMS:
            syns = [y for y in (x.lemma_names()[0]
                                for x in wn.synsets(word)) if y != word]
            if len(syns) > 0:
                w = random.choice(syns)
                logger.debug("found synonym %s for %s", w, word)
        return word

    def generate_text(self, generation_type='markov'):
        """ Generates sentences from a given corpus
        TODO:
            we DONT limit the sentence length
        Args:
            generation_type: 'markov' | 'hmm'
        Returns:
            Properly formatted string of generated sentences
        """
        assert generation_type in ['markov', 'hmm', 'hmm_past']
        if generation_type == "markov":
            return self._text_generator(next_token=self._generate_next_token)
        elif generation_type == "hmm":
            return self._text_generator(next_token=self._generate_next_token_hmm, emit=self._emitHMM)
        elif generation_type == "hmm_past":
            return self._text_generator(next_token=self._generate_next_token_hmm, emit=self._emitHMM_with_past)

    def _generate_next_token(self, past_states):
        """ generates next token based previous words """
        return self._generate_next_token_helper(past_states, self.transitions)

    def _generate_next_token_hmm(self, past_states):
        """ generates next token based previous word types """
        return self._generate_next_token_helper(past_states, self.transitions_hmm)

    def _generate_next_token_helper(self, past_states, transitions):
        """ generates next token based previous states """
        key = tuple(past_states)
        assert key in transitions, "%s" % str(key)
        return self._weighted_choice(transitions[key].items())

    def _emitHMM(self, token_type, past_states, past_emissions):
        """ emits a word based on previous tokens """
        assert token_type in self.emissions
        return self._weighted_choice(self.emissions[token_type].items())

    def _emitHMM_with_past(self, token_type, past_states, past_emissions):
        """ emits a word based on previous states (=token) and previous emissions (=words)
        The states and emissions are weighted according to their defined probabilities
            self.prob_hmm_states and self.prob_hmm_emissions"""
        assert token_type in self.emissions
        states_items = [(x[0], x[1] * self.prob_hmm_states)
                        for x in self.emissions[token_type].items()]
        key_emissions = tuple(past_emissions)
        if key_emissions in self.emissions_past[token_type]:
            states_emissions = [(x[0], x[1] * self.prob_hmm_emissions) for x in self.emissions_past[
                                token_type][tuple(past_emissions)].items()]
            return self._weighted_choice(states_items + states_emissions)
        return self._weighted_choice(states_items)

    def _weighted_choice(self, item_probabilities):
        """ Expects a list of (item, probability)-tuples
        and the sum of all probabilities and returns one entry weighted at random
        """
        probability_sum = sum(x[1] for x in item_probabilities)
        assert probability_sum > 0
        random_value = random.random() * probability_sum
        summed_probability = 0
        for item, value in item_probabilities:
            summed_probability += value
            if summed_probability > random_value:
                return item
