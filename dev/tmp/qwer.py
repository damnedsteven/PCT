# a stacked bar plot
# -*- coding: utf-8 -*-  
import numpy as np
import matplotlib.pyplot as plt
import pymssql
import collections
from collections import defaultdict
from pprint import pprint

def make_plot(Shift):
	# Get PCT data in 12 hours from 112 DB
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
	""".format(Month = Shift[:4]))

	FailRate = defaultdict(lambda: {})
	for row in cursor:
		if (row['Name'][-8:] == 'FailRate'):
			if (row['Shift'][-2:] == '11'):
				FailRate[row['Shift'][3:8] + ' Day'].update({row['Name']:float(row['Value'])})
			if (row['Shift'][-2:] == '20'):
				FailRate[row['Shift'][3:8] + ' Night'].update({row['Name']:float(row['Value'])})

	od = collections.OrderedDict(sorted(FailRate.items()))

	# Begin plotting
	N = len(FailRate)
	x = []
	y = defaultdict(lambda: [])
	for k, v in od.items():
		x.append(k)
		for subk, subv in v.items():
				y[subk].append(subv)
	
	ind = np.arange(N)    # the x locations for the groups    "{:.0%}".format()
	
	width = 0.1       # the width of the bars: can also be len(x) sequence
	
	pprint(y['MR_FailRate'])
	plt.plot(y['MR_FailRate'])
	# p2 = plt.plot(ind, y['P_FailRate'])
	# p3 = plt.plot(ind, y['PGI_FailRate'])
	# p4 = plt.bar(ind, y['CTO_FailRate'], width)
	
	plt.title('PCT/TAT Failure Rate')
	plt.legend(['MR TAT', 'P TAT', 'PGI TAT', 'CTO PCT'], loc='upper left')
	# plt.legend((p1[0], p2[0], p3[0], p4[0]), ('MR TAT', 'P TAT', 'PGI TAT', 'CTO PCT'), loc='upper left')


	# p1 = plt.bar(ind, menMeans, width, color='#d62728')
	# p2 = plt.bar(ind, womenMeans, width, bottom=menMeans)

	plt.xticks(ind, x)
	plt.yticks(np.arange(0, 1, 0.1))
	# plt.legend((p1[0], p2[0]), ('Men', 'Women'))

	plt.savefig('plot.png')

if __name__ == "__main__":
	make_plot(Shift='17/04/26-14')