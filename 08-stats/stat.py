import pandas as pd
import sys
import json

filename = sys.argv[1]
mode = sys.argv[2]

modes = ['dates', 'deadlines', 'exercises']

def main():
    if mode not in modes:
        raise ValueError("invalid input value: {}".format(mode))
    points = pd.read_csv(filename, index_col = 0)
    result = {}
    entity = {}
    for e in entities(points, mode):
        entity['mean'] = e.mean()
        q = e.quantile([0.25, 0.5, 0.75])
        entity['first'] = q[0.25]
        entity['last'] = q[0.75]
        entity['median'] = q[0.5]
        entity['passed'] = int(sum(e > 0))
        result[e.name] = entity.copy()
    print(json.dumps(result))

def entities(dataframe, mode):
    if mode == 'deadlines':
        for c in dataframe:
            yield dataframe[c]
    elif mode == 'dates':
        dates = set([d.split('/')[0] for d in dataframe])
        for d in dates:
            yield dataframe.filter(like=d).sum(axis=1).rename(d)
    elif mode == 'exercises':
        exercises = set([d.split('/')[1] for d in dataframe])
        for e in exercises:
            yield dataframe.filter(like='/'+e).sum(axis=1).rename(e)


if __name__ == '__main__':
    main()
