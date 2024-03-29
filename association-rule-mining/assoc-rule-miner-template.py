import sys
import os
from assoc_rule_mining_tools import *


def read_csv(filepath):
    '''Read transactions from csv_file specified by filepath
    Args:
        filepath (str): the path to the file to be read

    Returns:
        list: a list of lists, where each component list is a list of string representing a transaction

    '''

    transactions = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            transactions.append(line.strip().split(',')[:-1])
    return transactions


# To be implemented
def generate_frequent_itemset(transactions, minsup):
    '''Generate the frequent itemsets from transactions
    Args:
        transactions (list): a list of lists, where each component list is a list of string representing a transaction
        minsup (float): specifies the minsup for mining

    Returns:
        list: a list of frequent itemsets and each itemset is represented as a list string
        support_count_dict (dict): a dictionary of candidate frequent itemsets and correspondeing frequency

    Example:
        Output: [['margarine'], ['ready soups'], ['citrus fruit','semi-finished bread'], ['tropical fruit','yogurt','coffee'], ['whole milk']]
        The meaning of the output is as follows: itemset {margarine}, {ready soups}, {citrus fruit, semi-finished bread}, {tropical fruit, yogurt, coffee}, {whole milk} are all frequent itemset

    '''
    all_candidates = []

    ## Find all frequent 1-itemsets
    no_of_transactions = len(transactions)
    item_count = 1
    item_freq_dict = {}
    for transaction in transactions:
        for item in transaction:
            if frozenset([item]) in item_freq_dict:
                item_freq_dict[frozenset([item])] += 1
            else:
                item_freq_dict[frozenset([item])] = 1
    support_counts_dict = {item: freq for item, freq in item_freq_dict.items() if freq >= minsup * no_of_transactions}
    freqk_itemsets = list(support_counts_dict.keys())
    all_candidates.extend(freqk_itemsets)
    while freqk_itemsets:
        item_count += 1
        ## Candidate generation
        candidates = generate_candidates(freqk_itemsets)
        ## Candidate pruning
        candidates = prune_candidates(candidates, freqk_itemsets)
        item_freq_dict = count_freq(transactions, candidates)
        freqk_itemsets = [item for item, freq in item_freq_dict.items() if freq >= minsup * no_of_transactions]
        for itemset in freqk_itemsets:
            support_counts_dict[itemset] = item_freq_dict[itemset]
        all_candidates.extend(freqk_itemsets)
    return all_candidates, support_counts_dict

# To be implemented
def generate_association_rules(transactions, minsup, minconf):
    '''Mine the association rules from transactions
    Args:
        transactions (list): a list of lists, where each component list is a list of string representing a transaction
        minsup (float): specifies the minsup for mining
        minconf (float): specifies the minconf for mining

    Returns:
        list: a list of association rule, each rule is represented as a list of string

    Example:
        Output: [['root vegetables', 'rolls/buns','=>', 'other vegetables'],['root vegetables', 'yogurt','=>','other vegetables']]
        The meaning of the output is as follows: {root vegetables, rolls/buns} => {other vegetables} and {root vegetables, yogurt} => {other vegetables} are the two associated rules found by the algorithm


    '''
    assoc_rules = []

    ## Fetch the frequent itemsets as well as their corresponding frequency
    freq_itemsets, support_counts_dict = generate_frequent_itemset(transactions, minsup)
    for itemset in freq_itemsets:
        if len(itemset) > 1:
            H1 = [frozenset([item]) for item in itemset]
            new_rules, H1 = prune_consequents(itemset, H1, support_counts_dict, minconf)
            assoc_rules.extend(new_rules)
            new_rules = ap_genrules(itemset, H1, support_counts_dict, minconf)
            assoc_rules.extend(new_rules)
    return assoc_rules


def main():

    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Wrong command format, please follwoing the command format below:")
        print("python assoc-rule-miner-template.py csv_filepath minsup")
        print("python assoc-rule-miner-template.py csv_filepath minsup minconf")
        exit(0)


    if len(sys.argv) == 3:
        transactions = read_csv(sys.argv[1])
        result, support_counts_dict = generate_frequent_itemset(transactions, float(sys.argv[2]))
        # store frequent itemsets found by your algorithm for automatic marking
        with open('.'+os.sep+'Output'+os.sep+'frequent_itemset_result.txt', 'w') as f:
            for items in result:
                output_str = '{'
                for e in items:
                    output_str += e
                    output_str += ','

                output_str = output_str[:-1]
                output_str += '}\n'
                f.write(output_str)

    elif len(sys.argv) == 4:
        transactions = read_csv(sys.argv[1])
        minsup = float(sys.argv[2])
        minconf = float(sys.argv[3])
        result = generate_association_rules(transactions, minsup, minconf)

        # store associative rule found by your algorithm for automatic marking
        with open('.'+os.sep+'Output'+os.sep+'assoc-rule-result.txt', 'w') as f:
            for items in result:
                output_str = '{'
                for e in items:
                    if e == '=>':
                        output_str = output_str[:-1]
                        output_str += '} => {'
                    else:
                        output_str += e
                        output_str += ','

                output_str = output_str[:-1]
                output_str += '}\n'
                f.write(output_str)


if __name__ == '__main__':
    main()
