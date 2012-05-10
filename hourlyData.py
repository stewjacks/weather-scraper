#!/usr/bin/env python
# encoding: utf-8

# sam is gay
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

from BeautifulSoup import BeautifulStoneSoup

VERSION = "1.0"
REPO_VERSION = "1.0"

def get_options():
    usage = """Usage: %prog [options] command
    
%prog is a easy way to get weather data. 
If you want to use it just run ./%prog data.
    
Commands:
  Hourly - 
  Daily -
  Weekly -
  Monthly -
  Yearly - """
  
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
	def __init__(self, filepath, station, yearS, monthS, dayS, yearE, monthE, dayE):
		self.station = station
		self.dest = filepath
		self.yearS = yearS
		self.monthS = monthS
		self.dayS = dayS
		self.yearE = yearE
		self.monthE = monthE
		self.dayE = dayE
		
		self.getData()
	
	def urlMaker(self, currentYear, currentMonth, currentDay):
		#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MD7696&day=1&year=2012&month=5
		#http://www.wunderground.com/history/airport/CWTA/2012/05/02/DailyHistory.html
		# possible to implement geolookup here. 
		if self.station == ('\w\w\w\w'):
			urlbase = 'http://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html' %(self.station, currentYear, currentMonth, currentDay)
		else:
			urlbase = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=%s&day=%s&year=%s&month=%s' %(self.station, currentDay, currentYear, currentMonth)
		
		return urlbase	
		#now make the dates work nicely.
		 

		
			
	def getData(self, check = False):
		
		datestring = "%s--%s-%s-%s--%s-%s-%s" % (self.station, self.yearS, self.monthS, self.dayS, self.yearE, self.monthE, self.dayE)
		print "!Datestring: %s" % (datestring)
		filename = self.dest + datestring + '.csv'
		print "!Destination: %s" % (filename)
		# file(filename)
		FILE = open('test.csv', "w")
		write = csv.writer(FILE, delimiter=',', quoting=csv.QUOTE_ALL)
		
		list1 = []
		
		if self.yearE == self.yearS:
			yearsAll = [self.yearE]
		else:
			yearsAll = range(self.yearS, self.yearE + 1)

		for year in yearsAll:
			if self.yearS == self.yearE:
				monthsAll = range(self.monthS, self.monthE + 1)
			elif year == self.yearE:
				monthsAll = range(1, self.monthE + 1)
			else: 
				monthsAll = range(1, 13)

			
			for month in monthsAll:
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
					l = []
					url = self.urlMaker(year, month, day)
					print "!URL: %s" % (url)
					
					#go online
					resp = urllib2.urlopen(url)
					html = resp.read()
					soup = BeautifulStoneSoup(html)

					#Title: do this once 
					table = soup.find('table', id="obsTable")
					if check == False: #Throw a title on the CSV the first time around
						l1 = []
						l1.append('date')
						title = table.findAll('th')
						for th in title:
							l1.append(th.text)
						write.writerow(l1)
						check == True

					#Data:
					rows = table.findAll('tr')
					for tr in rows:
						cols = tr.findAll('td')		
						l = []
						l.append('%d/%d/%d' %(year, month, day)) #add date to each row

						##Clean up the mess: could probably do this in a nicer way with a single regex
						for td in cols:
							match1 = re.sub('&nbsp;&deg;C', '', td.text)
							match1 = re.sub('Comma\sDelimited\sFile', '', match1)
							match1 = re.sub('hPa','', match1)	
							match1 = re.sub('&nbsp;','', match1)
							match1 = re.sub('km/h','', match1)
							match1 = re.sub('mm', '', match1)
							match1 = re.sub('%', '', match1)
							l.append(match1)

						write.writerow(l)
		

if __name__ == '__main__':
	(op, (options, args)) = get_options()
	if len(args) < 1: #Could have input for date and station here in one string or a list as below
		op.print_usage()
	
	if args[0] == 'hourly':
		try:
			name = str(raw_input('Input station ID: \n'))
		except ValueError:
			print 'invalid id'
			
		try:
			yearS = int(raw_input('Start year: \n'))
		except ValueError:
			print 'invalid year'
		try:
			monthS = int(raw_input('Start month: \n'))
		except ValueError:
			print 'invalid month'
			
		try:
			dayS = int(raw_input('Start day: \n'))
		except ValueError:
			print 'invalid day'
			
		try:
			yearE = int(raw_input('End year: \n'))
			if yearE < yearS: 
				raise ValueError
		except ValueError:
			print 'invalid year'
			
		try:
			monthE = int(raw_input('End month: \n'))
			if (yearE == yearS) and (monthE < monthS):
				raise ValueError
		except ValueError:
			print 'invalid month'
				
		try:	
			dayE = int(raw_input('End day: \n'))
			if (dayE < dayS) and (monthE == monthS) and (yearE == yearS):
				raise ValueError
		except ValueError:
			print 'invalid day'

		try:
			saveLocation = str(raw_input('Save location (blank current directory) \n'))
		except ValueError: #create regex to make sure this matches a directory location
			print 'invalid location'

	elif args[0] == 'debug':
		name = 'CWTA'
		yearS = 2010
		monthS = 1
		dayS = 1
		yearE = 2010
		monthE = 1
		dayE = 1
		saveLocation = '/Users/Stewart/.test/'



		# break #replace this for some loop. 
			##!Add some block against future values? 
		
	else:
		print "invalid option, see usage: \n "
		op.print_usage()
	
	
	#start a new data collector process
	data = hourlyData(saveLocation, name, yearS, monthS, dayS, yearE, monthE, dayE)
		