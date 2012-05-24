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

import HTMLParser

from metar import Metar
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from BeautifulSoup import BeautifulStoneSoup


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

		self.metarParse('METAR CWTA 220800Z AUTO 22003KT 19/17 RMK AO1 2PAST HR 8010 SLP141 P0012 T01850169 50044', check = True)

	def metarTest(self):
		string = 'METAR CWTA 221000Z AUTO 19001KT 19/17 RMK AO1 6PAST HR 6007 SLP139 P0006 T01870172 50060'
		# string = 'METAR CWTA 221100Z AUTO 19003KT M15/M17 RMK AO1 SLP334 T11461166 51010'
		obs = Metar.Metar(string)
		temp = re.search('-?(\d+\.\d+)', obs.temp.string("C"))
		print temp.group(0)

	def metarParse(self, code, check = False, results = []):
#This needs to first navigate to CSV and check dates for overlaps, get metars from CSV, and put into new list

		if check == False:
			results.append(['Date UTC', 'Temperature (C)', 'Dew Point (C)', 'Wind', 'Peak Wind', 'Visibility', 'Pressure (hPa)', 'Precipitation (cm)', 'Present Weather', 'Sky Conditions', 'Observations', 'Report Type'])

		# Initialize a Metar object with the coded report
		obs = Metar.Metar(code)

		# The 'station_id' attribute is a string.
		# print obs.station_id
		l = []
		# The 'time' attribute is a datetime object
		if obs.time:
			l.append(obs.time.ctime())
		else: l.append('')

		# The 'temp' and 'dewpt' attributes are temperature objects
		if obs.temp:
			temp = re.search('-?(\d+\.\d+)', obs.temp.string("C"))
			l.append(temp.group(0))
		else: l.append('')

		if obs.dewpt:
			temp = re.search('-?(\d+\.\d+)', obs.dewpt.string("C"))
			l.append(temp.group(0))
		else: l.append('')

		# The wind() method returns a string describing wind observations
		# which may include speed, direction, variability and gusts.
		if obs.wind_speed:
			l.append(obs.wind())
		else: l.append('')
		
		# The peak_wind() method returns a string describing the peak wind 
		# speed and direction.
		if obs.wind_speed_peak:
			l.append(obs.peak_wind())
		else: l.append('')
		
		# The visibility() method summarizes the visibility observation.
		if obs.vis:
			l.append(obs.visibility())
		else: l.append('')
		
		# The 'press' attribute is a pressure object.
		if obs.press:
			temp = re.search('(\d+\.\d+)', obs.press.string("hPa"))
			l.append(temp.group(0))
		else: l.append('')
		
		# The 'precip_1hr' attribute is a precipitation object.
		if obs.precip_1hr:
			temp = re.search('(\d*\.*\d*)', obs.precip_1hr.string("cm"))
			l.append(temp.group(0))
		else: l.append('')
		
		# The present_weather() method summarizes the weather description (rain, etc.)
		if obs.present_weather:
			l.append(obs.present_weather())
		else: l.append('')
		
		# The sky_conditions() method summarizes the cloud-cover observations.			
		if obs.sky_conditions:
			l.append(obs.sky_conditions())
		else: l.append('')
		
		# The remarks() method describes the remark groups that were parsed, but 
		# are not available directly as Metar attributes.  The precipitation, 
		# min/max temperature and peak wind remarks, for instance, are stored as
		# attributes and won't be listed here.
		if obs._remarks:
		  l.append(obs.remarks())
		else: l.append('')
		
		if obs.type:
		  l.append(obs.report_type())
		else: l.append('')

		results.append(l)
		print results
		

	def urlMaker(self, currentYear, currentMonth, currentDay):
		#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MD7696&day=1&year=2012&month=5
		#http://www.wunderground.com/history/airport/CWTA/2012/05/02/DailyHistory.html
		# possible to implement geolookup here. 

		#http://api.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MAS947&month=5&day=11&year=2012&format=XML !!!!!!!

		if re.match('^\w{4}$', self.station):
			urlbase = 'http://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html?format=1' %(self.station, currentYear, currentMonth, currentDay)
		else:
			urlbase = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=%s&day=%s&year=%s&month=%s&format=1' %(self.station, currentDay, currentYear, currentMonth)
		return urlbase

	def getData1(self, check = False):
		l = []
		check = False
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
					(url, data) = self.xmlMaker(year, month, day)
					print "!URL: %s" % (url)
					l.append(data)
					
		self.pparse(l)
		# self.csvtool(l)

	def xmlMaker(self, currentYear, currentMonth, currentDay):
		#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MD7696&day=1&year=2012&month=5
		#http://www.wunderground.com/history/airport/CWTA/2012/05/02/DailyHistory.html
		# possible to implement geolookup here. 

		#http://api.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MAS947&month=5&day=11&year=2012&format=XML !!!!!!!

		if re.match('^\w{4}$', self.station):
			urlbase = 'http://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html?format=1' %(self.station, currentYear, currentMonth, currentDay)
			data = self.getAirportData(urlbase)
		else:
			urlbase = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=%s&day=%s&year=%s&month=%s&format=XML' %(self.station, currentDay, currentYear, currentMonth)
			data = self.getDataXML(urlbase)
		return url, data


	def getAirportData(self, url, check = False, l = [], i = 0): ##MAKE Hourly true
	##parse METAR/SPECI
		while True:
			try:
				resp = urllib2.urlopen(url)
				html = resp.read()
				break
			except:
				i += i
				print 'error with url - trying again %d' % (i)
				if i == 5:
					raise urllib.error.HTTPError
		print html
		if re.search('<br>', html):
			p = re.split(',\n<br>|<br>', html)
		elif re.search('<br />', html):
			p = re.split('<br />', p)

		pp = []

		for thing in p:
			p1 = re.sub('\n', '', thing)
			p2 = re.split(',', p1)

			if p2 != ['']:
				pp.append(p2)
				# print '%s' % (p2)

		if check == True:
			h = l[0]

			if len(pp[0]) == len(h[0]):
				pp.pop(0)

		else:
			check = True

		l.append(pp)

	def getDataPWSData(self, check = False): #for PWS with XML feed of data. <precip_today_metric> for rainfall
		l=[]

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
							url = self.xmlMaker(year, month, day)
							print "!URL: %s" % (url)

							#go online
							while True:
								# try:
								resp = urllib2.urlopen(url)
								data = resp.read()
								# print data
								tree = ET.ElementTree(ET.fromstring(data))
								##this is where you stopped. you are trying to parse a string in xml using ElementTree. You aren't sure if this is the best idea...
								
								l1 = []
								l2 = []
								for elm in tree.iter(): ##this is working
									if check == False:
										l1.append(elm.tag)
										l2.append(elm.text)


									print elm.tag
									# print elm.text
									

									#Take weather sample either at the first or last point in an hour. Take total rainfall. 


	def getData(self, check = False, l = []):
		
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

		l = self.cleanup(l)
		self.csvtool(l)

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
			for l1 in line:
				# print l1
				# print "*******"
				write.writerow(l1)

	def pparse(self, list1, count = 0, hOld = '', listTemp = []): #THIS DOES NOT WORK!!!!!!!
		s = list1[0]
		re.IGNORECASE
		
		for cell in s[0]:
			# print cell
			m = re.search('Precip', str(cell))
			print m
			if m is not None:
				break
			count = count + 1
		print count


#pop functionality not working so figure this out
	def cleanup(self, list1, count = 0, hOld = '', listTemp = []):
		print list1
		print "############ \n"

#ADD A PRECIPITATION PARSER
# Take the last per hour 
		if mode == 'last':
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
		elif mode == 'first':
			for row in list1:
				h = re.findall('^\d{1,2}', row[1])
				listTemp.append(row)
				if str(h) == str(hOld):
					listTemp.pop(count)
				else:
					count = count + 1
					print 'popped \n'
				hOld = h
		print listTemp

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
				break
			except ValueError: 
				print 'invalid mode choice'
		while True:
			try:
				saveLocation = str(raw_input('Save location (blank current directory) \n'))
				break
			except ValueError: #create regex/sys to make sure this matches a directory location
				print 'invalid location'

	elif args[0] == 'debug':
		name = 'IQCMONTR7'
		yearS = 2011
		monthS = 1
		dayS = 1
		yearE = 2011
		monthE = 1
		dayE = 3
		saveLocation = '/Users/Stewart/.test/'
		mode = 'first'

	# try:
	data = hourlyData(saveLocation, name, yearS, monthS, dayS, yearE, monthE, dayE, str(args[0]), mode)
	# except NameError:
		# print NameError