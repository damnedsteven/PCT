#!/usr/bin/env python3

from datetime import date, datetime, timedelta
import time
import math

def paying_hours(fromdate, todate, workingdays, workinghours):
	# fromdate = datetime.strptime(fromdate_str, '%Y-%m-%d %H:%M:%S')
	# todate = datetime.strptime(todate_str, '%Y-%m-%d %H:%M:%S')
	
	fromdate_in_sec = time.mktime(fromdate.timetuple())
	todate_in_sec = time.mktime(todate.timetuple())	
	
	days = (fromdate + timedelta(x) for x in range((todate - fromdate).days+1))
	
	result = 0
	
	for day in days:
		if (day.weekday() in workingdays):
			
			for workinghour in workinghours:
				fromhour = str(math.floor(workinghour[0]))
				fromminute = str(int(workinghour[0]*60)%60)
				tohour = str(math.floor(workinghour[1]))
				tominute = str(int(workinghour[1]*60)%60)

				fromworkinghour = datetime.strptime(str(day.year)+'-'+str(day.month)+'-'+str(day.day)+' '+fromhour+':'+fromminute, '%Y-%m-%d %H:%M')
				toworkinghour = datetime.strptime(str(day.year)+'-'+str(day.month)+'-'+str(day.day)+' '+tohour+':'+tominute, '%Y-%m-%d %H:%M')
				
				fromworkinghour_in_sec = time.mktime(fromworkinghour.timetuple())
				toworkinghour_in_sec = time.mktime(toworkinghour.timetuple())
				
				result += min(todate_in_sec, toworkinghour_in_sec) - max(fromdate_in_sec, fromworkinghour_in_sec)

	return result/3600

# if __name__ == '__main__':
	# FROM = '2017-03-18 09:19:00'
	# TO = '2017-03-20 09:19:00'
	# WD = (0, 1, 2, 3, 4)
	# WH = [(0.0, 23.99)]
	# PH = paying_hours(FROM, TO, WD, WH)
	# print(PH)
