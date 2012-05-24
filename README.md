weather-scraper
===============

a simple tool to collect historic weather data from weatherunderground.com

Hourly Data from Airports

	This data is reported in METAR/SPECI format hourly. Using the METAR parser by Tom Pollard this data can be simply collected and compiled. 

Hourly Data from PWS

	This data is most thoroughly exported as an XML and is available historically. These results are very comprehensive (usually every few minutes) and will need serious cleanup

Daily/Weekly/Monthly/Yearly for both

	This will be done currently by scraping the html page. There may be a better way to do this but it hasn't come to me yet.