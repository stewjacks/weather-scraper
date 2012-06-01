#!/usr/bin/env python
# encoding: utf-8

"""
weather module

Created by Stewart Jackson on 2012-04-30.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import datetime
import urllib2, cookielib
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
		self.check = False

		# self.getData1()
		# self.metarParse(['METAR CWTA 250500Z AUTO 15004KT M18/M24 RMK AO1 SLP263 T11771242 58030'], check = True)
		self.getData1()

	def metarTest(self):
		l = []

		print l

	def metarParse(self, list1, check): #This takes a METAR code list and outputs a nice list of data. Mostly taken from example in Metar
		results = []
		if self.check == False:
			results.append(['Date UTC', 'Temperature (C)', 'Dew Point (C)', 'Wind Speed (km/h)', 'Wind Direction (deg)', 'Peak Wind', 'Visibility', 'Pressure (hPa)', 'Precipitation (cm)', 'Present Weather', 'Sky Conditions', 'Observations', 'Report Type'])
			self.check = True
		tempHour = None
		for code in list1: 
			print 'metar: %s \n' %(code)
		# Initialize a Metar object with the coded report
			obs = Metar.Metar(code)
			print "String:"
			print obs.string()
			print '\n'

			# The 'station_id' attribute is a string.
			# print obs.station_id
			l = []
			# The 'time' attribute is a datetime object
			hour = obs._hour
			
			if tempHour is not None: 
				if (tempHour + 1) != hour:
					for x in range(tempHour + 1 ,hour):
						date = datetime.datetime(obs._year, obs._month, obs._day, x, obs._min)
						results.append([date])


			if obs.time:
				l.append(obs.time.ctime())
			else: l.append('')
			print "temp: "

			print obs.temp
			print '\n'

			# The 'temp' and 'dewpt' attributes are temperature objects
			if obs.temp:
				temp = re.search('-?(\d+\.\d+)', obs.temp.string("F"))
				l.append(temp.group(0))
			else: l.append('')

			if obs.dewpt:
				temp = re.search('-?(\d+\.\d+)', obs.dewpt.string("C"))
				l.append(temp.group(0))
			else: l.append('')

			# The wind() method returns a string describing wind observations
			# which may include speed, direction, variability and gusts.
			if obs.wind_speed:
				temp = re.search('\d+', obs.wind_speed.string("KMH"))
				l.append(temp.group(0))
			else: l.append('')

			if obs.wind_dir:
				temp = re.search('\d+', obs.wind_dir.string())
				l.append(temp.group(0))
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
			print l
			print "\n*******************\n"

		return results
		

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

	def getData1(self, l = []):
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
				elif (year == self.yearS) and (month == self.monthS):
					if month in [4, 6, 9, 11]:
						daysAll = range(self.dayS,31)
					elif month == 2:
						daysAll = range(self.dayS,29)
					else:
						daysAll = range(self.dayS,32)

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
					l += self.xmlMaker(year, month, day)
			
			print "l: "
			print l
			print "\n"
		# self.pparse(l)

		# print l
		self.csvtool(l)

	def xmlMaker(self, currentYear, currentMonth, currentDay, data = []):
		#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MD7696&day=1&year=2012&month=5
		#http://www.wunderground.com/history/airport/CWTA/2012/05/02/DailyHistory.html
		# possible to implement geolookup here. 

		#http://api.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MAS947&month=5&day=11&year=2012&format=XML !!!!!!!
		data = []
		if re.match('^\w{4}$', self.station):
			urlbase = 'http://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html?format=1' %(self.station, currentYear, currentMonth, currentDay)
			results = self.getAirportData(urlbase)
			# print "results: "
			# print results
			# print "\n"

		else:
			urlbase = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=%s&day=%s&year=%s&month=%s&format=XML' %(self.station, currentDay, currentYear, currentMonth)
			results = self.getDataPWSData(urlbase)
			for item in results:
				data.append(item)

		return results


	def getAirportData(self, url, check = False, l = [], i = 0, source = "csv"): ##MAKE Hourly true
	##parse METAR/SPECI

		cookieJar = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
		setmetar = 'http://www.wunderground.com/cgi-bin/findweather/getForecast?setpref=SHOWMETAR&value=1'
		
		request = urllib2.Request(setmetar)
		response = opener.open(request)

		while True:
			try:
				request = urllib2.Request(url)
				page = opener.open(request)
				data = page.read()
				break
			except:
				i += i
				print '%d - error with url - trying again \n' % (i)
				if i == 5:
					raise urllib.error.HTTPError
		# print data
		p = re.split('<br />', data)

		pp = []
		p2 = []

		for thing in p: #do this with regex for speed later
			p1 = re.sub('\n', '', thing)
			p1 = re.split(',', p1)

			if p1 != ['']:
				pp.append(p1)

		if source == 'csv':
			metar = pp[0].index('FullMetar')
			if check == False:
				pp.pop(0)

			timeOld = None
			log = []

			for row in pp:
				data = []
				if not (re.match('AAXX', row[metar])): #get rid of the 6 hour stamps
					
					time = re.split(":", row[0])


						

					if timeOld is None:
						if int(time[0]) != 12:
							p2.append(['12:00 AM'])
							for x in range(1, int(time[0])):
								timestr = '%d:%s' %(x, time[1])
								p2.append([timestr])
						p2.append(row)

					elif (int(time[0]) == (int(timeOld[0])+1)) or ((int(time[0]) == 1) and (int(timeOld[0]) == 12)): #append the first row that is one hour ahead of previous row

						if not ((int(time[0]) == 12) and re.search("AM", time[1])):
							p2.append(row)
					elif (int(time[0]) > int(timeOld[0]) + 1) or (int(time[0]) < int(timeOld[0])):

						if ((re.search('AM', timeOld[1])) and (re.search('AM', time[1]))) or ((re.search('PM', timeOld[1])) and (re.search('PM', time[1]))):
							if int(time[0]) < int(timeOld[0]):
								for x in range(1, int(time[0])):
									timestr = '%d:%s' %(x, time[1])
									p2.append([timestr])

							for x in range((int(timeOld[0]) + 1), int(time[0])):
								timestr = '%d:%s' %(x, time[1])
								p2.append([timestr])
							p2.append(row)

						elif (re.search('AM', timeOld[1])) and (re.search('PM', time[1])):
							
							for x in range((int(timeOld[0]) + 1), 12):
								timestr = '%d:%s' %(x, timeOld[1])
								p2.append([timestr])
							
							if int(time[0]) != 12:
								timestr = '%d:%s' %(12, time[1])
								p2.append([timestr])
								for x in range(1, int(time[0])):
									timestr = '%d:%s' %(x, time[1])
									p2.append([timestr])
							
							p2.append(row)
					log.append(time)
					log.append(timeOld)

					timeOld = time
			if int(timeOld[0]) < 11 and len(p2) != 24:
				for x in range(int(timeOld[0]) + 1, 12):
					timestr = '%d:%s' %(x, timeOld[1])
					p2.append([timestr])

			#confirmation of data
			if len(p2) != 24:
				for row in log:
					print row
				for row in p2:
					print row
					print '\n'

				print 'length of p2:'
				print len(p2)
				# print p2
			return p2



		elif source == "metar":
			metar = pp[0].index('FullMetar')
			pp.pop(0)

			p2 = []

			timeOld = [None]
			for row in pp:
				if re.match('AAXX', row[metar]): #get rid of the 6 hour stamps
					print 'skipped AAXX'
					print "\n*******************\n"
				else: #Make hourly
					time = re.split("[A,P,M,:]+", row[0])
					if (time[0] != timeOld[0]):
						p2.append(row[metar])
					timeOld = time

			temp = self.metarParse(p2, check)
		
			print "temp: "
			print temp
			print "\n"
			# p1 += temp 
			return temp


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
		filename = str(datestring + '.csv')
		print "!Destination: %s" % (filename)

		# file(filename)

		FILE = open(filename, "w")
		write = csv.writer(FILE, delimiter=',', quoting=csv.QUOTE_ALL)

		for line in list1:
			write.writerow(line)

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
				mode = str(raw_input('Style of parsing (first, last, or blank for all) \n'))
				break
			except ValueError: 
				print 'invalid mode choice'
		while True:
			try:
				saveLocation = str(raw_input('Save location (blank current directory) \n'))
				break
			except ValueError: #create regex/sys to make sure this matches a directory location
				print 'invalid location'

		data = hourlyData(saveLocation, name, yearS, monthS, dayS, yearE, monthE, dayE, str(args[0]), mode)

	elif args[0] == 'debug':
		name = 'CYUL'
		yearS = 2008	
		monthS = 1
		dayS = 1	
		yearE = 2011
		monthE = 12
		dayE = 31
		saveLocation = '/Users/Stewart/.test/'
		mode = 'first'

		for year in range(yearS, yearE+1):
			data = hourlyData(saveLocation, name, year, monthS, dayS, year, monthE, dayE, str(args[0]), mode)


	# try:
	
	# except NameError:
		# print NameError