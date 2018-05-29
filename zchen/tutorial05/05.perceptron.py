import sys
sys.path.append("..")
import numpy as np
from collections import Counter
from utils.n_gram import interpolate_gen

class Perceptron:
    def __init__(self, in_dim, out_dim):
        self._weights = np.zeros((out_dim, in_dim))

    def predict(self, x):
        result = np.matmul(self._weights, x)
        return np.sign(result).flatten() # why do i have to do this?

    def update(self, x, t):
        #print("x", x)
        y = self.predict(x)
        err_idx = (y != t)
        mis = np.sum(err_idx)
        if mis == 0:
            return 0
        x = x.T[err_idx].T
        t = t[err_idx]
        #print("t", t)
        #print("x", x)
        s = t * x
        s = np.sum(s, axis = 1)
        #print("s", s)
        #print("t", t)
        #print("w", self._weights.shape)
        self._weights += s
        return mis / len(err_idx)

def _vectorize(vocab, inputs, has_oov):
    num_dim = len(vocab)
    num_sen = len(inputs)
    vectors = np.zeros((num_dim, num_sen))
    for i, sentence in enumerate(inputs):
        for tok, cnt in sentence.items():
            if has_oov and tok not in vocab:
                continue
            pos = vocab.index(tok)
            vectors[pos, i] = cnt
    return vectors

class Wrapper:
    def __init__(self):
        self._perceptron = None
        self._vocab = set()
        self._labels = []
        self._inputs = []

    def add_corpus(self, fname):
        with open(fname) as fr:
            for line in fr:
                label, sentence = line.split('\t')
                self._labels.append(int(label))
                sentence = sentence.split(' ')
                self._inputs.append(Counter(sentence))
                self._vocab |= set(sentence)

    def seal(self, bias = False):
        self._vocab = tuple(self._vocab)
        self._perceptron = Perceptron(len(self._vocab), 1)
        # temp.shape = temp.shape + (1,)

    def train(self, num_epoch = 30, min_mis = 0.01, batch_size = 1000):
        p = self._perceptron
        inp = interpolate_gen(0.8)
        total = len(self._inputs)
        mis_mu = 1
        for i in range(num_epoch):
            t = 0
            while t < total:
                inputs = _vectorize(self._vocab, self._inputs[t:t + batch_size], False)
                labels = np.asarray(self._labels[t:t + batch_size])
                mis = p.update(inputs, labels)
                mis_mu = inp(mis, mis_mu)
                print("Error rate epoch.%d(%d/%d): %f" % (i, t, total, mis_mu), mis)
                t += batch_size
            if mis_mu < min_mis:
                break
        print("Train end")

    def test(self, fname):
        sentences = []
        with open(fname) as fr:
            for line in fr:
                sentences.append(Counter(line.split()))
        inputs = _vectorize(self._vocab, sentences, True)
        return self._perceptron.predict(inputs)

    def __str__(self):
        s = 'A perceptron wrapper\n'
        s += '\tVocab size: %d\n' % len(self._vocab)
        s += '\tCorpus size: %d\n' % len(self._inputs)
        return s

if __name__ == '__main__':
    w = Wrapper()
    w.add_corpus('../../data/titles-en-train.labeled')
    #w.add_corpus('../../test/03-train-input.txt')
    w.seal()
    print(w)
    w.train()
    res = w.test('../../data/titles-en-test.word')
    with open("my.labels", "w") as fw:
        for i in res:
            fw.write('%d\n' % i)
