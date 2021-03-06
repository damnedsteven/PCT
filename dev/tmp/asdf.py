import numpy as np
import matplotlib.pyplot as plt
import pymssql
import collections
from collections import defaultdict
from pprint import pprint

import matplotlib
matplotlib.use('Agg')

conn = pymssql.connect("16.187.224.112", "sa", "support", "FE2CheckPoint")
cursor = conn.cursor(as_dict=True)
cursor.execute("""
	SELECT
		*
	FROM
		PCTFailRate
	WHERE
		LEFT(Shift, 5) = '{Month}'
	ORDER BY
		Shift
""".format(Month = '17/04'))

FailRate = defaultdict(lambda: {})
for row in cursor:
	if (row['Name'][-8:] == 'FailRate'):
		if (row['Shift'][-2:] == '08'):
			FailRate[row['Shift'][3:8] + ' Day'].update({row['Name']:float(row['Value'])})
		if (row['Shift'][-2:] == '20'):
			FailRate[row['Shift'][3:8] + ' Night'].update({row['Name']:float(row['Value'])})

od = collections.OrderedDict(sorted(FailRate.items()))

N = len(FailRate)
x = []
y = defaultdict(lambda: [])
for k, v in od.items():
	x.append(k)
	for subk, subv in v.items():
			y[subk].append(subv)

pprint(x)
pprint(y['MR_FailRate'])

ind = np.arange(N)    # the x locations for the groups    "{:.0%}".format()
	
width = 0.1       # the width of the bars: can also be len(x) sequence

plt.plot(ind, y['MR_FailRate'])
plt.plot(ind, y['P_FailRate'])
plt.plot(ind, y['PGI_FailRate'])
plt.bar(ind, y['CTO_FailRate'], width)

plt.title('PCT/TAT Failure Rate')
plt.legend(['MR TAT', 'P TAT', 'PGI TAT', 'CTO PCT'], loc='upper left')


plt.xticks(ind, x)
plt.yticks(np.arange(0, 1, 0.1))

plt.savefig('plot.png')