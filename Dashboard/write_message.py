from __future__ import division
import pymssql
from get_paying_hours import paying_hours
from collections import defaultdict

def write_message(Type, Target, From, To, WorkingDay, WorkingHour, URL):
	# Get PCT data in 12 hours from 112 DB
	conn = pymssql.connect("16.187.224.112", "sa", "support", "FE2CheckPoint")
	cursor = conn.cursor(as_dict=True)
	cursor.execute("""
	SELECT
		SO,
		PLO,
		Product,
		{From},
		{To},
		FEFlag,
		MaxPCT AS Target
	FROM
		PCTMaster
		LEFT JOIN
		ProductFamily
		ON PCTMaster.Family=ProductFamily.ProductFamily AND (PCTMaster.ConfigType=ProductFamily.ConfigType OR PCTMaster.ConfigType is NULL)
	WHERE
		ProductFamily.ConfigType NOT IN ('PPS Option', 'PPS Option 3F')
		AND
		{To} >= DATEADD(hh, -12, DATEADD(hh,DATEDIFF(hh,'19000101',GETDATE()),'19000101')) 
		AND
		{To} < DATEADD(hh,DATEDIFF(hh,'19000101',GETDATE()),'19000101')
	""".format(From = From, To = To))

	# for row in cursor:
		# print('row = %r' % (row,))

	PCT = {}
	SKU = []
	for row in cursor:
		PCT.update({row['PLO']:{'SKU':row['Product'].split(' ')[0], From:row[From], To:row[To]}})
		SKU.append(row['Product'].split(' ')[0])	

	SKUs = "'" + "','".join(SKU) + "'"

	conn.close()

	# Retrieve SKU and Platform info from 111 DB
	conn = pymssql.connect("16.187.224.111", "yufei", "yufei123", "PLOdb")
	cursor = conn.cursor(as_dict=True)
	cursor.execute("""
	SELECT
		SKU,
		Name
	FROM
		SKUList
	WHERE
		SKU IN ({SKUs})
	""".format(SKUs = SKUs))

	Platform = defaultdict(lambda: 'N/A')
	for row in cursor:
		Platform[row['SKU']] = row['Name']

	conn.close()

	# Calculate fail rate
	# Count_Total = defaultdict(lambda: 0)
	Count = defaultdict(lambda: defaultdict(lambda: 0))
	FailedPLO = defaultdict(lambda: [])
	Sum = 0
	Sum_Fail = 0
	for k, v in PCT.items():
		Count[Platform[v['SKU']] if Platform[v['SKU']] != 'N/A' else v['SKU']]['Total'] += 1
		Sum += 1
		if (paying_hours(v[From], v[To], WorkingDay, WorkingHour) > Target):
			Count[Platform[v['SKU']] if Platform[v['SKU']] != 'N/A' else v['SKU']]['Fail'] += 1
			FailedPLO[Platform[v['SKU']] if Platform[v['SKU']] != 'N/A' else v['SKU']].append(k)
			Sum_Fail += 1
	
	FailedPLOs = defaultdict(lambda: 'N/A')
	# Do sorting and stringlize
	for k, v in Count.items():
		v['Failure_Rate'] = v['Fail']/v['Total']
		FailedPLOs[k] = "'" + "','".join(FailedPLO[k]) + "'"
		
	PF = [ k for k in Count.keys() ]
	
	Sorted_PF = sorted(PF, key=lambda x: (Count[x]['Failure_Rate'], Count[x]['Fail']), reverse=True)
	
	# Generate table
	if (Type == 1):
		html = """
		<table border="1">
			<tr bgcolor="#C6EFCE">
				<th colspan="4">备料(MR) TAT Performance</th>
			</tr>
			<tr bgcolor="#C6EFCE">
				<th>Platform</th>
				<th>MR PLO QTY</th>
				<th>MR TAT Fail PLO QTY (Over 24H)</th>
				<th>Failure Rate</th>
			</tr>
		"""
	if (Type == 2):
		html = """
		<table border="1">
			<tr bgcolor="#FFFF99">
				<th colspan="4">生产(P) TAT Performance</th>
			</tr>
			<tr bgcolor="#FFFF99">
				<th>Platform</th>
				<th>Handover PLO QTY</th>
				<th>P TAT Fail PLO QTY (Over 42H)</th>
				<th>Failure Rate</th>
			</tr>
		"""
	if (Type == 3):
		html = """
		<table border="1">
			<tr bgcolor="#E6E6FA">
				<th colspan="4">出货(PGI) TAT Performance</th>
			</tr>
			<tr bgcolor="#E6E6FA">
				<th>Platform</th>
				<th>PGI PLO QTY</th>
				<th>PGI TAT Fail PLO QTY (Over 6H)</th>
				<th>Failure Rate</th>
			</tr>
		"""
	# for k, v in Count.items():
	for v in Sorted_PF:
		html += '<tr>'
		html += '<td>' + v + '</td>'
		html += '<td>' + str(Count[v]['Total']) + '</td>'
		if (Count[v]['Fail'] > 0):	
			html += '<td bgcolor=\'#FFC7CE\'><a href=' + URL + '?PLO=' + FailedPLOs[v] + '>' + str(Count[v]['Fail']) + '</a></td>'
		else:
			html += '<td>' + str(Count[v]['Fail']) + '</td>'
		html += '<td>' + "{:.0%}".format(Count[v]['Failure_Rate']) + '</td>'
		html += '</tr>'

	html += """
		<tr>
			<th>Total</th>
			<th>{Sum}</th>
			<th>{Sum_Fail}</th>
			<th>{Failure_Rate}</th>
		</tr>
	</table>
	""".format(Sum = Sum, Sum_Fail = Sum_Fail, Failure_Rate = "{:.0%}".format(Sum_Fail/Sum))

	return html