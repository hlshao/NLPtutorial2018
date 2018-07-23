import argparse
from math import log2
from collections import defaultdict
from itertools import product


def arguments_parse():
    parser = argparse.ArgumentParser(
        usage='\tビームサーチを用いた品詞推定のテストプログラム',
        description='説明',
        epilog='end',
        add_help=True,
    )
    parser.add_argument('-m', '--model', help='モデルファイル名', type=str)
    parser.add_argument('-i', '--input', help='入力ファイル名', type=str)
    return parser.parse_args()


def update_best(score, prev, next_, best_score, best_edge, my_best=None, next_tag=None):
    '最良のスコアとエッジを更新'
    current_best_score = best_score[next_]
    if current_best_score and score >= current_best_score:
        return
    best_score[next_] = score
    best_edge[next_] = prev
    if next_tag:
        my_best[next_tag] = score


def test_hmm(unk_prob=0.05, vocab_num=1e6, B=10):
    '''品詞推定して my_answer.pos に出力'''
    output_file = 'my_answer.pos'

    # モデルの読み込み
    transition = defaultdict(float)
    emission = defaultdict(float)
    possible_tags = defaultdict(int)
    for line in open(model_file, encoding='utf-8'):
        ptype, context, word, prob = line.split()
        possible_tags[context] = 1
        if ptype == 'T':
            transition[f'{context} {word}'] = float(prob)
        else:
            emission[f'{context} {word}'] = float(prob)

    # テスト
    # 出力ファイルオープン
    f = open(output_file, 'w', encoding='utf8')

    for line in open(test_file, encoding='utf8'):
        # 前向きステップ
        words = line.split()
        l = len(words)
        best_score = defaultdict(float)
        best_edge = defaultdict(str)
        # print(best_edge)
        active_tags = []
        tags = possible_tags.keys()
        # BOS
        best_score['0 <s>'] = 0
        best_edge['0 <s>'] = None
        active_tags.append(['<s>'])
        # Sequense
        for i in range(l):
            my_best = {}
            for prev, next_ in product(active_tags[i], tags):
                if f'{i} {prev}' not in best_score or f'{prev} {next_}' not in transition:
                    continue
                prob_t = transition[f'{prev} {next_}']
                prob_e = (1 - unk_prob) * emission[f'{next_} {words[i]}'] + unk_prob / vocab_num
                score = best_score[f'{i} {prev}'] - log2(prob_t) - log2(prob_e)
                update_best(score, f'{i} {prev}', f'{i+1} {next_}', best_score, best_edge, my_best, next_)
                my_best[next_] = score
            best_b = sorted(my_best.items(), key=lambda x: x[1], reverse=True)[:B]
            active_tags.append([k for k, v in best_b])
        # EOS
        for tag in active_tags[-1]:
            if not transition[f'{tag} </s>']:
                continue
            score = best_score[f'{l} {tag}'] - log2(transition[f'{tag} </s>'])
            update_best(score, f'{l} {tag}', f'{l+1} </s>', best_score, best_edge)


        # 後ろ向きステップ
        tags = []
        next_edge = best_edge[f'{l+1} </s>']
        from pprint import pprint
        pprint(best_edge.values())
        while next_edge != '0 <s>':
            _, tag = next_edge.split()
            tags.append(tag)
            next_edge = best_edge[next_edge]
        tags.reverse()

        # 書き出し
        f.write(' '.join(tags) + '\n')
    # 出力ファイルクローズ
    f.close()


if __name__ == '__main__':
    import os
    args = arguments_parse()

    test_file = args.input if args.input else '../../data/wiki-en-test.norm'.replace('/', os.sep)
    model_file = args.model if args.model else 'hmm_model'

    # 時間の計測
    import time
    start = time.time()
    test_hmm()
    process_time = time.time() - start
    print(process_time)

''' ビームサーチ
実行時間
1.6322784423828125 sec



'''

''' 元
実行時間
17.593451023101807 sec

perl ..\..\script\gradepos.pl ..\..\data\wiki-en-test.pos my_answer.pos

Accuracy: 90.82% (4144/4563)

Most common mistakes:
NNS --> NN      45
NN --> JJ       27
NNP --> NN      22
JJ --> DT       22
VBN --> NN      12
JJ --> NN       12
NN --> IN       11
NN --> DT       10
NNP --> JJ      8
JJ --> VBN      7
'''
