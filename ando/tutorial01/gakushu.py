dic={}
total=0
token=0

f = open("/Users/one/nlptutorial/data/wiki-en-test.word")
lines = f.readlines()
for line in lines:
    line = line.rstrip()
    words = line.split(" ")
    words.append("</s>")
    for word in words:
        if word in dic:
            dic[word] += 1
        else:
            dic[word] = 1
            total += 1
        token+=1

with open("model.txt", "w") as fout:
    for i,j in dic.items():
        fout.write("{}:{}\t".format(i,j/token))
print(total)