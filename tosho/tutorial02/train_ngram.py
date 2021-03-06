import os, sys
sys.path.append(os.path.pardir)
from common.n_gram import NGram
from common.smoothings import SimpleSmoothing, MultiLayerSmoothing, WittenBell
from os import path

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--train-file')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('-n', '--n-gram', type=int, required=True)
    parser.add_argument('-s', '--smoothing', choices=('simple', 'multilayer', 'witten-bell'))
    parser.add_argument('-r', '--unk-rate', type=float, nargs='*', required=False)
    arg = parser.parse_args()

    print(f'train model with {arg.train_file} with {arg.smoothing} smoothing')

    model = NGram(arg.n_gram)
    with open(arg.train_file, 'r') as f:
        model.train(list(f))
    model.print_params()

    if arg.smoothing == 'simple':
        smoothing = SimpleSmoothing(arg.unk_rate[0])
    elif arg.smoothing == 'multilayer':
        rates = {}
        for i, rate in enumerate(arg.unk_rate):
            rates[i] = rate
        smoothing = MultiLayerSmoothing(rates)
    elif arg.smoothing == 'witten-bell':
        with open(arg.train_file, 'r') as f:
            smoothing = WittenBell(arg.n_gram)
            smoothing.train(list(f))

    model.save_params(arg.output_file)

    filename_body, filename_ext = path.splitext(arg.output_file)
    smoothing_output_file = f'{filename_body}-{arg.smoothing}{filename_ext}'

    smoothing.save_params(smoothing_output_file)
    
    print(f'saved parameters to {arg.output_file}')
    print(f'saved smoothing params to {smoothing_output_file}')

'''
$ python train_ngram.py -t ../../test/02-train-input.txt -c test-bigram.pyc -n 2
train model with ../../test/02-train-input.txt
6 types (2-gram)
p(('<s>', 'a')) = 0.25
p(('a', 'b')) = 0.25
p(('b', 'c')) = 0.125
p(('c', '</s>')) = 0.125
p(('b', 'd')) = 0.125
p(('d', '</s>')) = 0.125
6 types (1-gram)
p(('<s>',)) = 0.2
p(('a',)) = 0.2
p(('b',)) = 0.2
p(('</s>',)) = 0.2
p(('c',)) = 0.1
p(('d',)) = 0.1
p(unk) = 1e-06
saved parameters to test-bigram.pyc

$ python train_ngram.py -t ../../data/wiki-en-train.word -c wiki-bigram.pyc -n 2
train model with ../../data/wiki-en-train.word
21514 types (2-gram)
p(('.', '</s>')) = 0.03532168963785503
p(('of', 'the')) = 0.005440544612465822
p((',', 'and')) = 0.005273143239774566
p(('<s>', 'The')) = 0.004073433402153897
p(('in', 'the')) = 0.0038781318006807656
p((',', 'the')) = 0.0029016237933151053
p(('-RRB-', '.')) = 0.002817923106969477
p(('<s>', 'In')) = 0.002706322191841973
p(('of', 'a')) = 0.002566821047932593
p(('can', 'be')) = 0.002538920819150717
5235 types (1-gram)
p((',',)) = 0.04794981557763239
p(('the',)) = 0.038903696524244136
p(('<s>',)) = 0.03502678835850631
p(('</s>',)) = 0.03502678835850631
p(('.',)) = 0.034515251864415904
p(('of',)) = 0.030207576124707213
p(('a',)) = 0.021942223299141157
p(('to',)) = 0.020272998950004038
p(('and',)) = 0.018630697574240098
p(('in',)) = 0.014376867781277764
p(unk) = 1e-06
saved parameters to wiki-bigram.pyc
'''