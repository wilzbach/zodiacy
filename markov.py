from nltk import word_tokenize, pos_tag
from itertools import chain
import random
from copy import deepcopy

def compute_transitions(tokens_list, order=1): 
    transitions = dict()
    distinct_tokens = set()

    for tokens_entry in tokens_list:
        tokens = word_tokenize(tokens_entry[0])
        last_tokens = ['^']
        # count the occurences of "present | past"
        for token in chain(tokens[1:], ['$']):
            distinct_tokens.add(token)
            past = tuple(last_tokens)
            suffixes = [past[i:] for i in range(len(past))]
            for suffix in suffixes:
                if suffix not in transitions:
                    transitions[suffix] = {token : 1}
                else:
                    if token not in transitions[suffix]:
                        transitions[suffix][token] = 1
                    else:
                        transitions[suffix][token] += 1

            last_tokens = last_tokens[1 if len(last_tokens) == order else 0:]
            last_tokens.append(token)

    # compute probabilities
    for transition_counts in transitions.values():
        summed_occurences = sum(transition_counts.values())
        for token in transition_counts.keys():
            transition_counts[token] /= summed_occurences
    # ensure there is a probability
    for token in distinct_tokens:
        if (token,) not in transitions:
            transitions[(token,)] = {token: 1}

    return transitions

def compute_token_probabilities(pos_tagged_tokens):
    token_probabilities = dict()

    for item in pos_tagged_tokens:
        if item[1] not in token_probabilities:
            token_probabilities[item[1]] = {item[0]: 1}
        else:
            if item[0] not in token_probabilities[item[1]]:
                token_probabilities[item[1]][item[0]] = 1
            else:
                token_probabilities[item[1]][item[0]] += 1

    for probabilities in token_probabilities.values():
        summed_occurences = sum(probabilities.values())
        for token in probabilities.keys():
            probabilities[token] /= summed_occurences


    return token_probabilities

def _weighted_choice(item_probabilities, value_to_probability=lambda x:x, probability_sum=1):
    """ Expects a list of (item, probability)-tuples and the sum of all probabilities and returns one entry weighted at random """
    random_value = random.random()*probability_sum
    summed_probability = 0
    for item, value in item_probabilities:
        summed_probability += value_to_probability(value)
        if summed_probability > random_value:
            return item
        
def generate_text(transitions, count, order=1):
    print(transitions[('^',)])
    last_tokens = ['^']
    generated_tokens = []
    i = 0
    while last_tokens[-1] != '$':
        print(last_tokens)
        new_token = generate_next_token(transitions, tuple(last_tokens[-i if i < order else -order:]))
        i+=1
        last_tokens = last_tokens[1 if len(last_tokens) == order else 0:]
        last_tokens.append(new_token)
        generated_tokens.append(new_token)

    return generated_tokens

def generate_next_token(transitions, past, precondition=lambda x: True):
    for key in [past[i:] for i in range(len(past))]:
        if key in transitions:
            possible_transitions = deepcopy(transitions[key])
            for key in transitions[key].keys():
                if not precondition(key):
                    del possible_transitions[key]
            return _weighted_choice(possible_transitions.items(), probability_sum=sum(possible_transitions.values()))

def lexicographic_markov(input, count, order=1):
    tokens = word_tokenize(input)
    pos_tagged_tokens = pos_tag(tokens)
    symbol_transitions = compute_transitions([x[1] for x in pos_tagged_tokens])
    token_probabilities = compute_token_probabilities(pos_tagged_tokens)

    return generate_text(symbol_transitions, random.choice([x[1] for x in pos_tagged_tokens]), count, lambda symbol: _weighted_choice(token_probabilities[symbol].items()), order)
