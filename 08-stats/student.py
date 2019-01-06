import pandas as pd
import numpy as np
import sys
import json

filename = sys.argv[1]
sid = sys.argv[2]

semester_start = np.datetime64('2018-09-17')

def main():
    points = pd.read_csv(filename, index_col=0)
    if sid == 'average':
        st = points.mean()
    else:
        try:
            st = points.loc[int(sid),:]
        except (ValueError, KeyError):
            raise ValueError('invalid input student id: {}'.format(sid))
    exercises = set(d.split('/')[1] for d in st.index)
    s = pd.Series([st.filter(like='/'+e).sum() for e in exercises], index = exercises)
    student = dict(mean=s.mean(), median=s.median(), total=s.sum(), passed=int(sum(s>0)))
    dates = set(d.split('/')[0] for d in st.index)
    s = pd.Series([st.filter(like=d+'/').sum() for d in dates], index = dates)
    cummulative = s.sort_index().cumsum()
    cummulative.index = cummulative.index.astype('datetime64', copy=False)
    days = np.array(cummulative.index) - semester_start
    days = days.astype('timedelta64[D]') / np.timedelta64(1, 'D')
    A = np.vstack([days, np.zeros(len(days))]).T
    slope = np.linalg.lstsq(A, cummulative.values, rcond=None)[0][0]
    student['regression slope'] = slope
    if slope == 0:
        print(json.dumps(student))
        return
    student['date 16'] = str(semester_start + np.timedelta64(int(16/slope), 'D'))
    student['date 20'] = str(semester_start + np.timedelta64(int(20/slope), 'D'))
    print(json.dumps(student, indent=3, sort_keys=True))


if __name__ == '__main__':
    main()