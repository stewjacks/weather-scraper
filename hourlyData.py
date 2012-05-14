#!/usr/bin/env python
# encoding: utf-8

"""
weather module

Created by Stewart Jackson on 2012-04-30.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import urllib2
import csv
import socket
import re
import optparse

try:
	from BeautifulSoup import BeautifulStoneSoup
except:
	from bs4 import BeautifulStoneSoup

VERSION = "1.0"
REPO_VERSION = "1.0"

def get_options():
    usage = """Usage: %prog [options] command
    
%prog is a easy way to get weather data. 
If you want to use it just run ./%prog data.
    
Commands:
  hourly - 
  daily -
  weekly -
  monthly -
  yearly - """
  
    op = optparse.OptionParser(version='%prog ' + VERSION, usage = usage)
    op.add_option('-b', '--branch',
        dest='branch',
        default='last',
        type='choice',
        action='store',
        choices=['last', 'first', 'all'],
        help='How to parse data for multiple readings first/last/all (default: %default)')
    op.add_option('-d', '--debug',
        dest='debug',
        default=False,
        action='store_true',
        help='Turn on debug')


    return (op, op.parse_args())


class hourlyData:
	def __init__(self, filepath, station, yearS, monthS, dayS, yearE, monthE, dayE, operation, mode):
		self.station = station
		self.dest = filepath
		self.yearS = yearS
		self.monthS = monthS
		self.dayS = dayS
		self.yearE = yearE
		self.monthE = monthE
		self.dayE = dayE
		self.operation = operation
		self.mode = mode
		
		self.getData()
	
	def urlMaker(self, currentYear, currentMonth, currentDay):
		#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MD7696&day=1&year=2012&month=5
		#http://writeroww.wunderground.com/history/airport/CWTA/2012/05/02/DailyHistory.html
		# possible to implement geolookup here. 
		if re.match('^\w{4}$', self.station):
			urlbase = 'http://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html' %(self.station, currentYear, currentMonth, currentDay)
		else:
			urlbase = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=%s&day=%s&year=%s&month=%s' %(self.station, currentDay, currentYear, currentMonth)
		
		return urlbase	
		#now make the dates work nicely.
			
	def getData(self, check = False):
		l = []
		check = False
		if self.yearE == self.yearS:
			yearsAll = [self.yearE]
		else:
			yearsAll = range(self.yearS, self.yearE + 1)

		for year in yearsAll:
			if self.operation == 'yearly':
				print 'make yearly already...'
#Make YEARLY
			else:
				if self.yearS == self.yearE:
					monthsAll = range(self.monthS, self.monthE + 1)
				elif year == self.yearE:
					monthsAll = range(1, self.monthE + 1)
				else: 
					monthsAll = range(1, 13)

				
				for month in monthsAll:

					if self.operation == 'monthly':
						print 'make monthly already...'

#make monthly segment

					else:
						if (self.yearS == self.yearE) and (self.monthS == self.monthE): #we're looking at dates in one month
							daysAll = range(self.dayS, self.dayE + 1)
						elif (year == self.yearE) and (month == self.monthE): #wrapping up
							daysAll = range(1, self.dayE + 1)
						else:
							if month in [4, 6, 9, 11]:
								daysAll = range(1,31)
							elif month == 2:
								daysAll = range(1,29)
							else:
								daysAll = range(1,32)
								
						for day in daysAll:
							url = self.urlMaker(year, month, day)
							print "!URL: %s" % (url)
							
							#go online
							while True:
								try:
									resp = urllib2.urlopen(url)
									html = resp.read()
									soup = BeautifulStoneSoup(html)

		#THIS IS WHERE DAILY AND HOURLY SPLIT. MAKE DAILY

									#Title: do this once 
									table = soup.find('table', id="obsTable")
									#Throw a title on the CSV the first time around unless otherwise specified
									
									if check == False:
										l1 = []
										l1.append('date')
										title = table.findAll('th')
										for th in title:
											l1.append(th.text)

										l.append(l1)
										print check
										check = True
										print check

									#Data:
									rows = table.findAll('tr')
									for tr in rows:
										l2 = []
										cols = tr.findAll('td')		
										l2.append('%d/%d/%d' %(year, month, day)) #add date to each row

										##Clean up the mess: could probably do this in a nicer way with a better regex
										for td in cols:
											match1 = re.sub('&nbsp;&deg;C', '', td.text)
											match1 = re.sub('Comma\sDelimited\sFile', '', match1)
											match1 = re.sub('hPa','', match1)	
											match1 = re.sub('&nbsp;','', match1)
											match1 = re.sub('km/h','', match1)
											match1 = re.sub('mm', '', match1)
											match1 = re.sub('%', '', match1)
											l2.append(match1)

										if len(l2) > 3:
											l.append(l2)
									break
								except:
									print 'error in loop'


		self.csvtool(l)
		self.cleanup(l)

	def csvtool(self, list1):
		datestring = "%s--%s-%s-%s--%s-%s-%s" % (self.station, self.yearS, self.monthS, self.dayS, self.yearE, self.monthE, self.dayE)
		print "!Datestring: %s" % (datestring)
		# filename = self.dest + datestring + '.csv'
		filename = str(self.station + '.csv')
		print "!Destination: %s" % (filename)

		# file(filename)

		FILE = open(filename, "w")
		write = csv.writer(FILE, delimiter=',', quoting=csv.QUOTE_ALL)

		for line in list1:
			write.writerow(line)

#pop functionality not working so figure this out
	def cleanup(self, list1):
		count = 0
		hOld = ''
		listTemp = []
# Take the last per hour 
		if mode == 'last'
			for row in list1:
				count = count + 1
				h = re.findall('^\d{1,2}', row[1])
				listTemp.append(row)
				if str(h) == str(hOld):
					count = count - 1 
					listTemp.pop(count)
					print 'popped \n'
				hOld = h
#take the first per hour
		elif mode == 'first'
			for row in list1:
				count = count + 1
				h = re.findall('^\d{1,2}', row[1])
				listTemp.append(row)
				if str(h) == str(hOld):
					listTemp.pop(count)
					count = count - 1
					print 'popped \n'
				hOld = h

		return listTemp




if __name__ == '__main__':
	(op, (options, args)) = get_options()
	if len(args) < 1: #Could have input for date and station here in one string or a list as below
		op.print_usage()
	
	if args[0] in ['hourly', 'daily', 'weekly', 'monthly', 'yearly']:

		while True:
			try:
				name = str(raw_input('Input station ID: \n'))
				break
			except ValueError:
				print 'invalid id'

		while True:	
			try:
				yearS = int(raw_input('Start year: \n'))
				if re.match('^\d{4}$', str(yearS)):
					break
				else: raise ValueError	
			except ValueError:
				print 'invalid year'

	if args[0] in ['hourly', 'daily', 'weekly', 'monthly']:			
		while True:
			try:
				monthS = int(raw_input('Start month: \n'))
				if monthS <= 12 and monthS > 0 :
					break
				else: raise ValueError
			except ValueError:
				print 'invalid month'

	if args[0] in ['hourly', 'daily', 'weekly']:			
		while True:		
			try:
				dayS = int(raw_input('Start day: \n'))
				if ((dayS <= 30 and monthS in [4, 6, 9, 11]) or (dayS <= 29 and monthS == 2) or (dayS <= 31 and monthS in [1, 3, 5, 7, 8, 10, 12])):
					break
				else: raise ValueError
			except ValueError:
				print 'invalid day'

	if args[0] in ['hourly', 'daily', 'weekly', 'monthly', 'yearly']:
		while True:		
			try:
				yearE = int(raw_input('End year: \n'))
				if yearE >= yearS and re.match('^\d{4}$', str(yearE)): 
					break
				else: raise ValueError
			except ValueError:
				print 'invalid year'

	if args[0] in ['hourly', 'daily', 'weekly', 'monthly']:
		while True:		
			try:
				monthE = int(raw_input('End month: \n'))
				if (yearE == yearS) and (monthE < monthS):
					raise ValueError
				elif monthE <= 12 and monthE > 0:
					break
				else: raise ValueError
			except ValueError:
				print 'invalid month'

	if args[0] in ['hourly', 'daily', 'weekly']:
		while True:			
			try:	
				dayE = int(raw_input('End day: \n'))
				if ((dayE < dayS) and (monthE == monthS) and (yearE == yearS)):
					raise ValueError
				elif (dayE <= 30 and monthE in [4, 6, 9, 11]) or (dayE <= 29 and monthE == 2) or (dayE <= 31 and monthE in [1, 3, 5, 7, 8, 10, 12]):
					break
				else: raise ValueError
			except ValueError:
				print 'invalid day'

	if args[0] in ['hourly', 'daily', 'weekly', 'monthly', 'yearly']:
		while True:
			try:
				mode = str(raw_input('Style of parsing (first, last, or blank for all) \name'))
		while True:
			try:
				saveLocation = str(raw_input('Save location (blank current directory) \n'))
				break
			except ValueError: #create regex/sys to make sure this matches a directory location
				print 'invalid location'

	elif args[0] == 'debug':
		name = 'MC7533'
		yearS = 2011
		monthS = 1
		dayS = 1
		yearE = 2011
		monthE = 1
		dayE = 1
		saveLocation = '/Users/Stewart/.test/'
		mode = 'first'

	try:
		data = hourlyData(saveLocation, name, yearS, monthS, dayS, yearE, monthE, dayE, str(args[0]), mode)
	except NameError:
		print "invalid option, see usage: \n "
		op.print_usage()