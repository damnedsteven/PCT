# a stacked bar plot
# -*- coding: utf-8 -*-  
import numpy as np
import matplotlib.pyplot as plt
import pymssql
import collections
from collections import defaultdict

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
	""".format(Month = Shift[:5]))

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

	ind = np.arange(N)    # the x locations for the groups    "{:.0%}".format()
		
	width = 0.1       # the width of the bars: can also be len(x) sequence

	p1 = plt.plot(ind, y['MR_FailRate'])
	p2 = plt.plot(ind, y['P_FailRate'])
	p3 = plt.plot(ind, y['PGI_FailRate'])
	p4 = plt.bar(ind, y['CTO_FailRate'], width)
	
	p4[0].set_color('y')

	plt.title('PCT/TAT Failure Rate')
	# plt.legend(['MR TAT', 'P TAT', 'PGI TAT', 'CTO PCT'], loc='upper left')
	plt.legend((p1[0], p2[0], p3[0], p4[0]), ('MR TAT', 'P TAT', 'PGI TAT', 'CTO PCT'), loc='upper right')


	# p1 = plt.bar(ind, menMeans, width, color='#d62728')
	# p2 = plt.bar(ind, womenMeans, width, bottom=menMeans)

	plt.xticks(ind, x)
	plt.yticks(np.arange(0, 1, 0.1))
	# plt.legend((p1[0], p2[0]), ('Men', 'Women'))
	# plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in gca().get_yticks()]) 

	plt.savefig('img/plot.png')

# if __name__ == "__main__":
	# make_plot(Shift='17/04/26-14')