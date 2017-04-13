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
		CASE
			WHEN ProductFamily.ConfigType IN ('CTO', 'BTO&CTO') THEN 'CTO' 
			WHEN ProductFamily.ConfigType IN ('PPS Option', 'PPS Option 3F') THEN 'PPS Option'
			WHEN FEFlag = 1 THEN 'Complex CTO'
			WHEN ProductFamily.ConfigType IN ('ConfigRack') THEN 'Rack'
			ELSE 'Others' 
		END as ProdCat,
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
		{From} is NOT NULL
		AND
		{To} >= DATEADD(hh, -12, DATEADD(hh,DATEDIFF(hh,'19000101',GETDATE()),'19000101')) 
		AND
		{To} < DATEADD(hh,DATEDIFF(hh,'19000101',GETDATE()),'19000101')
	""".format(From = From, To = To))

	# for row in cursor:
		# print('row = %r' % (row,))

	PCT = {}
	if (Type != 'PC'):
		SKU = []
		for row in cursor:
			if (row['ProdCat'] != 'PPS Option'):
				PCT.update({row['PLO']:{'SKU':row['Product'].split(' ')[0], From:row[From], To:row[To]}})
				SKU.append(row['Product'].split(' ')[0])	

		SKUs = "'" + "','".join(SKU) + "'"
	else:
		for row in cursor:
			PCT.update({row['PLO']:{'ProdCat':row['ProdCat'], From:row[From], To:row[To]}})
				
	conn.close()

	if (Type != 'PC'):
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
		Item = (Platform[v['SKU']] if Platform[v['SKU']] != 'N/A' else v['SKU']) if Type != 'PC' else v['ProdCat']
		Count[Item]['Total'] += 1
		Sum += 1
		Goal = Target if Type != 'PC' else Target[v['ProdCat']]
		if (paying_hours(v[From], v[To], WorkingDay, WorkingHour) > Goal):
			Count[Item]['Fail'] += 1
			FailedPLO[Item].append(k)
			Sum_Fail += 1
	
	FailedPLOs = defaultdict(lambda: 'N/A')
	# Do sorting and stringlize
	for k, v in Count.items():
		v['Failure_Rate'] = v['Fail']/v['Total']
		FailedPLOs[k] = "'" + "','".join(FailedPLO[k]) + "'"
		
	PF = [ k for k in Count.keys() ]
	
	Sorted_PF = sorted(PF, key=lambda x: (Count[x]['Failure_Rate'], Count[x]['Fail']), reverse=True)
	
	# Generate table
	if (Type == 'MR'):
		html = """
		<table border="1" width="888">
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
	if (Type == 'P'):
		html = """
		<table border="1" width="888">
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
	if (Type == 'PGI'):
		html = """
		<table border="1" width="888">
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
	if (Type == 'PC'):
		html = """
		<table border="1" width="888">
			<tr bgcolor="#e842f4">
				<th colspan="4">Overall PCT Performance</th>
			</tr>
			<tr bgcolor="#e842f4">
				<th>Product Category</th>
				<th>PGI DG QTY</th>
				<th>PCT Fail DG QTY</th>
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