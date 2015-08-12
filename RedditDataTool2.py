import requests
import requests.auth
import urllib2
import json
import time
import pymongo
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo import DESCENDING
from bson.code import Code
from bson.son import SON
import os
import csv
import datetime
import nltk
from nltk.corpus import stopwords
import re
import threading
from threading import Timer,Thread,Event
from collections import Counter
import numpy as np
import scipy.stats as stats
from scipy.stats.stats import pearsonr
import array


class PresentationMethods(object):
	"""docstring for PresMeths"""
	def __init__(self):
		self.header = "-------------------------------------------------------\n\tReddit Data Collection and Analysis Tool\n-------------------------------------------------------\n\n"
		pass
	#Just a method to clear the console
	def ClearScreen(self):
		os.system(['clear','cls'][os.name == 'nt'])
		pass
	#Just a method to press any key to continue		
	def AnyKey(self):
		x=raw_input('Press any key to continue')
		pass

	def WriteError(self,error,method):
		try:
			fileobject=open('C:\Users\Kevin\Documents\Bot\mainfile\GeneralErrors.csv','a')
		except:
			fileobject=open('C:\Users\Kevin\Documents\Bot\mainfile\GeneralErrors.csv','w')
			fileobject.write("METHOD,DATETIME,ERROR\n")
		try:
			fileobject.write(str(method)+","+str(datetime.datetime.now())+","+str(error)+"\n")
			fileobject.close()
		except:
			pass

	def ChoiceInput(self,minChoice,maxChoice):
		choice = raw_input("Please enter your choice : ")
		try:
			choice = int(choice)
			if choice >= minChoice and choice <=maxChoice:
				return choice
			else:
				return False
		except:
			return False	
	
	def ScrapingMenu(self):
		choice = False
		scrape = ScrapingMethods()
		# timer = threading.Timer(3600, scrape.RefreshToken())
		# timer.start()
		thread = ThreadingTimer()
		thread.start()
		try:
			while not choice:
				self.ClearScreen()
				self.Header()

				print "Menu : \n"
				print "1 : Scrape SubReddits"
				print "2 : Scrape Submissions"
				print "3 : Scrape Comments\n\n"
				print "0 : Exit\n\n"

				try:
					choice = int(input("Please Select an option : "))
				except:
					print "Invalid Option"
					choice = False
					self.AnyKey()
				if choice not in [0,1,2,3]:
					print "Invalid Option"
					choice = False
					self.AnyKey()
			
				if choice == 1:
					scrape.CollectSubReddits()
					choice = False
				elif choice == 2:
					scrape.StoreSubmissions()
					choice = False
				elif choice == 3:
					scrape.StoreComments()
					choice = False
				elif choice == 0:
					thread.event.set()
					return		
		except:
			thread.event.set()

	def Header(self):
		print self.header

	def Menu(self):
		choice = False
		while not choice:
			self.ClearScreen()
			self.Header()

			print "Menu : \n"
			print "1 : Scraping options"
			print "2 : Analysis options\n\n"
			print "0 : Exit\n\n"


			try:
				choice = int(input("Please Select an option : "))
			except:
				print "Invalid Option"
				choice = False
				self.AnyKey()
			if choice not in [0,1,2]:
				print "Invalid Option"
				choice = False
				self.AnyKey()

			if choice == 1:
				self.ScrapingMenu()
				choice = False
			elif choice == 2:
				self.AnalysisMenu()
				choice = False
			elif choice == 0:
				choice = True

	def AnalysisMenu(self):
		choice = False
		scrape = ScrapingMethods()
		dbInt = DataBaseInteractions()
		ana = Analysis()

		while not choice:
			self.ClearScreen()
			self.Header()
			
			print "Menu : \n"
			print "1 : Collection Information"
			print "2 : Perform word count on comment bodies for a period"
			print "3 : Perform word count on submission titles for a period"
			print "4 : Export word count on selected word to .csv"
			print "5 : Test correlation between two words for a time period"
			print "6 : Export total word count for period of time"
			print "7 : List most Frequent Authors for period of time\n\n"
			print "0 : Exit\n\n"
			
			try:
				choice = int(input("Please Select an option : "))
			except:
				print "Invalid Option"
				choice = False
				self.AnyKey()
			
			if choice not in [0,1,2,3,4,5,6,7]:
				print "Invalid Option"
				choice = False
				self.AnyKey()

			if choice == 1:
				print "Loading data..."
				subReddit = scrape.SelectSubReddit()
				subReddit = dbInt.ReturnSubReddit(subReddit)
				subRedditName = subReddit["name"]
				numComments = dbInt.CountCommentsBySubReddit(subRedditName)
				numSubmissions = dbInt.CountSubmissionsBySubReddit(subRedditName)
				
				print "SubReddit\t\t: "+subReddit["display_name"]
				print "SubReddit Id\t\t: "+subReddit["name"]
				print "\nSubscribers\t\t: "+str(subReddit["subscribers"])
				print "Created on\t\t: "+scrape.DateOutput(subReddit["created_utc"])
				print "Description\t\t: "+subReddit["public_description"]
				print "\n\nNumber submissions for this subreddit stored : "+str(numSubmissions)
				print "\n\nNumber comments for this subreddit stored : "+str(numComments)

				self.AnyKey()

				choice = False
			
			elif choice == 2:
				startDate = scrape.DateInput("Please enter a start date for the time period")
				endDate = scrape.DateInput("Please enter an end date for the time period")
				subReddit = scrape.SelectSubReddit()

				dbInt.PerformWordCount(startDate,endDate,subReddit)
				
				choice = False

			elif choice == 3:
				startDate = scrape.DateInput("Please enter a start date for the time period")
				endDate = scrape.DateInput("Please enter an end date for the time period")
				subReddit = scrape.SelectSubReddit()

				dbInt.PerformWordCount(startDate,endDate,subReddit,"title")
				
				choice = False
				
			elif choice == 4:
				dbInt.WordCountByDateToCSV()
				choice = False

			elif choice == 5:
				pair = dbInt.PrepareForPearsons()
				ana.TestCorrelation(pair[0],pair[1])
				self.AnyKey()

				choice = False

			elif choice == 6:
				dbInt.WriteWordsToCSV()
				self.AnyKey()

				choice = False

			elif choice == 7:
				dbInt.ListMostFrequentAuthors()
				self.AnyKey()

				choice = False
			elif choice == 0:
				choice = True

class DataBaseInteractions(object):
	"""docstring for DataBaseInteraction"""
	
	def __init__(self):
		self.client = MongoClient()
		client = MongoClient('localhost', 27017)
		self.db = self.client.RedditData	
		
		self.submissions = self.db.ProcessedSubmissions				
		self.comments = self.db.ProcessedComments
		self.subReddits = self.db.ProcessedSubReddits
		self.wordMonitor = self.db.WordMonitor

		self.subReddits.create_index('name', unique=True)
		self.submissions.create_index('name', unique=True)
		self.comments.create_index('name', unique=True)		

		self.submissions.create_index([('author',pymongo.DESCENDING)])
		self.comments.create_index([('author',pymongo.DESCENDING)])
		self.submissions.create_index([('subreddit_id',pymongo.DESCENDING)])
		self.comments.create_index([('subreddit_id',pymongo.DESCENDING)])



		self.wordMonitor.create_index([('word',ASCENDING),('date',ASCENDING),('subreddit',ASCENDING),('attribute',ASCENDING)],unique=True)
		#for sorting based on date
		self.submissions.create_index([('created_utc',pymongo.DESCENDING)])
		self.comments.create_index([('created_utc',pymongo.DESCENDING)])
		self.subReddits.create_index([('created_utc',pymongo.DESCENDING)])
		
		self.pres = PresentationMethods()

	def InsertSubmission(self,sub):
		try:
			self.submissions.insert_one(sub["data"])
			#self.client.close()
			return True
		except Exception, e:
			#self.client.close()
			return False
	
	def InsertComment(self,com):
		try:
			self.comments.insert_one(com["data"])

			
			#self.client.close()
			return True
		except Exception, e:
			#self.client.close()
			return False

	def InsertSubReddit(self,subRed):
		try:
			self.subReddits.insert_one(subRed["data"])
			#self.client.close()
			return True
		except Exception, e:
			#self.client.close()
			return False

	def SubRedditExists(self,subRed):
		try:
			result = self.subReddits.find_one({"display_name":subRed})
			if result == None:
				return False
			else:
				return True
		except Exception,e:
			#self.client.close()
			return False

	def ReturnSubReddit(self,subRed):
		try:
			result = self.subReddits.find_one({"display_name":subRed})
			#self.client.close()
			if result == None:
				return False
			else:
				return result
		except Exception,e:
			#self.client.close()
			return False

	def ReturnAllSubmissionDetails(self,subRedditId):
		listSubs = self.submissions.find({"subreddit_id":subRedditId},{"_id":0}).batch_size(30).sort([("created_utc",1)])
		#listSubs.max_time_ms(None)
		return listSubs

	def ReturnSubmissionsDetailsByPeriod(self,subRedditId,startDate,endDate):
		print subRedditId
		print startDate
		print endDate
		listSubs = self.submissions.find({"subreddit_id":subRedditId,"created_utc":{"$gte":startDate,"$lte":endDate}},{"_id":0}).batch_size(50)
		#listSubs.max_time_ms(None)
		#self.client.close()
		return listSubs

	def CountComments(self):
		count = self.comments.count()
		#self.client.close()
		return count

	def CountCommentsBySubReddit(self,subRedditId):
		count = self.comments.find({"subreddit_id":subRedditId}).count()
		return count
	
	def CountSubmissionsBySubReddit(self,subRedditId):
		count =self.submissions.find({"subreddit_id":subRedditId}).count()
		#self.client.close()
		return count
	
	def CountSubmissions(self):
		count =self.submissions.count()
		#self.client.close()
		return count
	
	def ReturnComments(self):
		listComs = self.comments.find({"subreddit_id":"t5_2qhb9"},{"_id":0}).batch_size(30).sort([("created_utc",1)])
		return listComs

	def ReturnCommentsByPeriod(self,subRedditId,startDate,endDate):
		listComs = self.comments.find({"subreddit_id":subRedditId,"created_utc":{"$gte":startDate,"$lte":endDate}},{"_id":0}).batch_size(30)
		return listComs

	def PerformWordCount(self,startDate,endDate,subReddit,subject=None):
		db = self.db
		scrape = ScrapingMethods()
		
		#Assign mapping and reducing functions from external js files.
		if subject == "title":
			map = Code(open('C:\Users\Kevin\webscraper\gitfile\wordmaptitles.js','r').read())
		else:
			map = Code(open('C:\Users\Kevin\webscraper\gitfile\wordmap.js','r').read())
		
		reduce = Code(open('C:\Users\Kevin\webscraper\gitfile\wordreduce.js','r').read())
				#import list of stopwords to remove from results
		cachedStopWords = stopwords.words("english")

		#loop which gets a word count for each day during the period of time
		while startDate<=endDate:
			#nextdate = startdate + 1 day
			nextDate = startDate + 86400
			if subject=="title":
				print "Counting words from submission titles on the "+ str(scrape.DateOutput(nextDate))
			else:
				print "Counting words from comments on the "+ str(scrape.DateOutput(nextDate))
			#clear the results collection
			db.Results.drop()

			#Perform map reduce
			self.comments.map_reduce(map,reduce,"Results",query={'created_utc':{"$gte":startDate,"$lte":nextDate},'subreddit':subReddit})
			unixDate  = startDate
			#convert unix start date into readable format to be stored
			startDate = ScrapingMethods().DateOutput(startDate)

			#Iterate thnrough results collection and add words, counts and dates to a new collection called word monitor
			for result in db.Results.find():
				#Use regex to only select valid words. Could do more specific Regex here
				##if re.match("^[A-Za-z]+|[A-Za-z]{1}'[A-Za-z]+$",result["_id"]) and result["value"]>0:
				if re.match("^[a-zA-Z\-_ ’'‘ÆÐƎƏƐƔĲŊŒẞÞǷȜæðǝəɛɣĳŋœĸſßþƿȝĄƁÇĐƊĘĦĮƘŁØƠŞȘŢȚŦŲƯY̨Ƴąɓçđɗęħįƙłøơşșţțŧųưy̨ƴÁÀÂÄǍĂĀÃÅǺĄÆǼǢƁĆĊĈČÇĎḌĐƊÐÉÈĖÊËĚĔĒĘẸƎƏƐĠĜǦĞĢƔáàâäǎăāãåǻąæǽǣɓćċĉčçďḍđɗðéèėêëěĕēęẹǝəɛġĝǧğģɣĤḤĦIÍÌİÎÏǏĬĪĨĮỊĲĴĶƘĹĻŁĽĿʼNŃN̈ŇÑŅŊÓÒÔÖǑŎŌÕŐỌØǾƠŒĥḥħıíìiîïǐĭīĩįịĳĵķƙĸĺļłľŀŉńn̈ňñņŋóòôöǒŏōõőọøǿơœŔŘŖŚŜŠŞȘṢẞŤŢṬŦÞÚÙÛÜǓŬŪŨŰŮŲỤƯẂẀŴẄǷÝỲŶŸȲỸƳŹŻŽẒŕřŗſśŝšşșṣßťţṭŧþúùûüǔŭūũűůųụưẃẁŵẅƿýỳŷÿȳỹƴźżžẓ]+$",result["_id"]) and result["value"]>0:
					#Do not count word if it is considered a stop word by NTLK
					if result["_id"] not in cachedStopWords:
						#Insert word and values into new collection WordMonitor
						try:
							if subject == "title":
								self.wordMonitor.insert_one({'word':result["_id"],'value':result["value"],'date':startDate,'subreddit':subReddit,'attribute':'title','unix_date':unixDate})
							else:
								self.wordMonitor.insert_one({'word':result["_id"],'value':result["value"],'date':startDate,'subreddit':subReddit,'attribute':'body','unix_date':unixDate})
						
						except Exception,e:
							PresentationMethods().WriteError(e,"wordMonitor insert statement")
			#Increase startdate to next day
			startDate = nextDate
					
	def WordCountOnWord(self,word):
		result = self.wordMonitor.find({'word':word})
		return result

	def WordCountByDateToCSV(self):
		scrape = ScrapingMethods()
		startDate = scrape.DateInput("Please enter a start date for the word count output : ")
		endDate = scrape.DateInput("Please enter an end date for the word count output : ")
		subReddit = scrape.SelectSubReddit()

		day = 86400
		dates = []
		
		while startDate<endDate:
			date = scrape.DateOutput(startDate)
			dates.append(date)
			startDate = startDate+day 

		print "Please enter a list of words to monitor separated by a comma (,)"

		try:
			words = raw_input().lower()
			words = words.replace(" ","")
			words = words.split(",")
		
		except Exception,e:
			print "error in words input"
			return
		
		validAttribute = False
		while validAttribute is False:
			print "Do you wish to print from titles or comment bodys?\n1: Title\n2: Body"
			attribute = raw_input()
			try:
				if int(attribute) not in [1,2]:
					print "Invalid input"
				else:
					validAttribute = True
					if attribute == 1:
						attribute = "title"
					else:
						attribute = "body" 
			except:
				print "Invalid input"
				validAttribute = False

		isValid = False

		while isValid is False:
			fileName = raw_input("Please enter a name for the file to be created : ")
			path = 'C:\Users\Kevin\webscraper\gitfile\\'+fileName+'.csv'
			if os.path.isfile(str(path)):
				print "A file with this name already exists. Please enter a new file name"
				isValid = False
				self.pres.AnyKey()
			else:
				isValid = True
		
		fileobject=open(str(path),"w")
		fileobject.write("Word,")

		for day in dates:
			fileobject.write(str(day)+",")
		fileobject.write("\n")
		
		for word in words:
			fileobject.write(str(word)+",")

			for day in dates:
				#Inefficient use of code here making too many requests to db, but didn't have time to come up with a better solution
				count = self.wordMonitor.find_one({"word":word,"date":day,"subreddit":subReddit,"attribute":attribute})
				value= 0
				if count==None:
					pass
				else:
					value = count["value"]
				
				fileobject.write(str(value)+",")
			fileobject.write("\n")
		fileobject.close()

	def PrepareForPearsons(self):
		word1 = raw_input("Type word one : ")
		word2 = raw_input("Type word two : ")
		pair = [word1.lower(),word2.lower()]
		
		
		scrape = ScrapingMethods()
		subReddit = scrape.SelectSubReddit()
		startDate = scrape.DateInput("Please enter a start date for the sample : ")
		endDate = scrape.DateInput("Please enter an end date for the sample : ")
		day = 86400
		dates = []
		
		while startDate<endDate:
			date = scrape.DateOutput(startDate)
			dates.append(date)
			startDate = startDate+day 

		array1 = []
		array2 = []


		#This could be extracted to a method
		for day in dates:
			#Inefficient use of code here making too many requests to db, but didn't have time to come up with a better solution
			count = self.wordMonitor.find_one({"word":word2,"date":day,"subreddit":subReddit})
			value= 0
			if count==None:
				pass
			else:
				value = count["value"]
			array1.append(value)
		for day in dates:
			#Inefficient use of code here making too many requests to db, but didn't have time to come up with a better solution
			count = self.wordMonitor.find_one({"word":word2,"date":day,"subreddit":subReddit})
			value= 0
			if count==None:
				pass
			else:
				value = count["value"]
			array2.append(value)


		return [array1,array2]

	def WriteWordsToCSV(self):
		scrape = ScrapingMethods()
		startDate = scrape.DateInput("Please enter a start date for the word count output : ")
		endDate = scrape.DateInput("Please enter an end date for the word count output : ")
		# startDate=scrape.DateOutput(startDate)
		# endDate = scrape.DateOutput(endDate)
		subReddit = scrape.SelectSubReddit()
		
		#Another useful feature of MongoDB is the aggregate function, where a pipeline of commands are executed in sequence
		# for performing calculations on a database 
		pipeline = [{"$match":{"$and":[{"subreddit":subReddit},{"unix_date":{"$gte":startDate,"$lte":endDate}}]}},
		{"$group":{"_id":"$word","count":{"$sum":"$value"}}},
		{"$sort": SON([("count", -1), ("_id", -1)])}]
		result= self.wordMonitor.aggregate(pipeline)
			
		isValid = False

		while isValid is False:
			fileName = raw_input("Please enter a name for the file to be created : ")
			path = 'C:\Users\Kevin\webscraper\gitfile\\'+fileName+'.csv'
			if os.path.isfile(str(path)):
				print "A file with this name already exists. Please enter a new file name"
				isValid = False
				self.pres.AnyKey()
			else:
				isValid = True

		
		fileobject=open(str(path),"w")
		fileobject.write("Word,Count\n")
		
		PresentationMethods().AnyKey()
		for item in result:
		
			fileobject.write(str(item["_id"])+","+str(item["count"])+"\n")
		fileobject.close()

	def ListMostFrequentAuthors(self):
		scrape = ScrapingMethods()
		startDate = scrape.DateInput("Please enter a start date for the word count output : ")
		endDate = scrape.DateInput("Please enter an end date for the word count output : ")
		# startDate=scrape.DateOutput(startDate)
		# endDate = scrape.DateOutput(endDate)
		subReddit = scrape.SelectSubReddit()

		#Another useful feature of MongoDB is the aggregate function, where a pipeline of commands are executed in sequence
		# for performing calculations on a database 
		pipeline = [{"$match":{"$and":[{"subreddit":subReddit},{"created_utc":{"$gte":startDate,"$lte":endDate}}]}},
		{"$group":{"_id":"$author","count":{"$sum":1}}},
		{"$sort": SON([("count", -1), ("_id", -1)])}]
		result= self.submissions.aggregate(pipeline)

		isValid = False

		while isValid is False:
			fileName = raw_input("Please enter a name for the file to be created : ")
			path = 'C:\Users\Kevin\webscraper\gitfile\\'+fileName+'.csv'
			if os.path.isfile(str(path)):
				print "A file with this name already exists. Please enter a new file name"
				isValid = False
				self.pres.AnyKey()
			else:
				isValid = True

		
		fileobject=open(str(path),"w")
		fileobject.write("Author,Submissions\n")
		
		PresentationMethods().AnyKey()
		for item in result:
		
			fileobject.write(str(item["_id"])+","+str(item["count"])+"\n")
		fileobject.close()

	def ListMostFrequentCommenters(self):
		scrape = ScrapingMethods()
		startDate = scrape.DateInput("Please enter a start date for the word count output : ")
		endDate = scrape.DateInput("Please enter an end date for the word count output : ")
		# startDate=scrape.DateOutput(startDate)
		# endDate = scrape.DateOutput(endDate)
		subReddit = scrape.SelectSubReddit()

		#Another useful feature of MongoDB is the aggregate function, where a pipeline of commands are executed in sequence
		# for performing calculations on a database 
		pipeline = [{"$match":{"$and":[{"subreddit":subReddit},{"created_utc":{"$gte":startDate,"$lte":endDate}}]}},
		{"$group":{"_id":"$author","count":{"$sum":1}}},
		{"$sort": SON([("count", -1), ("_id", -1)])}]
		result= self.comments.aggregate(pipeline)

		isValid = False

		while isValid is False:
			fileName = raw_input("Please enter a name for the file to be created : ")
			path = 'C:\Users\Kevin\webscraper\gitfile\\'+fileName+'.csv'
			if os.path.isfile(str(path)):
				print "A file with this name already exists. Please enter a new file name"
				isValid = False
				self.pres.AnyKey()
			else:
				isValid = True

		
		fileobject=open(str(path),"w")
		fileobject.write("Author,Comments\n")
		
		PresentationMethods().AnyKey()
		for item in result:
		
			fileobject.write(str(item["_id"])+","+str(item["count"])+"\n")
		fileobject.close()

class ScrapingMethods(object):
	"""docstring for ScrapingMethods"""
	

	def __init__(self):
		self.pres = PresentationMethods()
		self.db = DataBaseInteractions()
		self.headers = "" 
		#self.GetOAuth2Token()
		#self.timer = RefreshToken()
	
	def StartTimer(self):
		self.timer = self.RefreshToken()

	def RefreshToken(self):
		self.headers = self.GetOAuth2Token()

	def SelectSubReddit(self):
		while True:
			self.pres.ClearScreen()
			print "Please enter the SubReddit you wish to scrape (Case Sensitive):\n"
			subReddit = raw_input(" : ")
			if self.db.SubRedditExists(subReddit):
				print subReddit + " is a valid SubReddit and is stored on the database"
				return subReddit
			else:
				print subReddit + " is not a valid subReddit or does not exist in the database"
				self.pres.AnyKey()

	def SelectSubRedditSection(self):
		"""This method is just to allow the user to select which Reddit search algorithm is going to be used to select data"""
		choice = False
		while choice is False:
			self.pres.AnyKey()
			print "Please select a subreddit section to scrape from.\n"
			print "\t1: New\n\t2: Hot\n\t3: Controversial\n\t4: Top\n\t5: Scrape by Time Period (Warning may take some time to run)\n\n\t0: Back"
			
			try:
				choice = int(input())
			except:
				print "Invalid input"
				self.pres.AnyKey()

			if choice ==1:
				return "/new/.json"
			
			elif choice ==2:
				return "/hot/.json"
			
			elif choice ==3:
				return "/controversial/.json"
			
			elif choice ==4:
				
				print "From what time period do you want to scrape?\n\t1: All time\n\t2: Past Year\n\t3: Past Month\n\t4: Past Week (May not collect 1000 submissions)\n\t5: Past 24 hours (May not collect 1000 submissions)\n\t6: All of above (Not implemented yet)\n\t7: Back"
				period=["error","all","year","month","week","day"]
				
				choice2 = input()
				
				if (1<= int(choice2) <=5):
					return str("/top/.json?sort=top&t="+str(period[int(choice2)])+"&")
			
				else:
					print "Invalid choice"
					self.pres.AnyKey()

			elif choice ==5:
				return 5
			
			elif choice ==0:
				return 0
			
			else:
				print "invalid choice please select again"
				pres.AnyKey()

	def SelectLimit(self):
		"""This just allows the user to select how many submissions they want to scrape"""

		isValid = False
		while not isValid:
			PresentationMethods().ClearScreen()
			print "Please select the number of submissions you wish to retrive\n\n"
			print "1: 100\n2: 200\n3: 300\n4: 400\n5: 500\n6: 600\n7: 700\n8: 800\n9: 900\n10: 1000"
			limit =[0,100,200,300,400,500,600,700,800,900,1000]
			try:
				choice = int(input())
			except:
				print "Invalid Choice"
					
			if choice in [1,2,3,4,5,6,7,8,9,10]:
				isValid = True

		return limit[choice]

	def GetOAuth2Token(self):
		print "getting TOKEN"
		path = "C:\Users\Kevin\Documents\Bot\Mainfile\\accountdetails.txt"
		#I stored the details in a txt file in python dict format for easy access
		try:
			details = open(path,'r').read()
			myDetailsDict = eval(details)
		except Exception, e:
			self.pres.WriteError(e,"GetOAuth2Token")

		user_agent = "College Data collection project by u/Ouiski"
			
		#Acquiring an authentication token
		#*** I want to change this part to that the scraper automatically collects a token every 3600s(its expiry length I believe)
		# It'll require a bit of restructuring, but if I can use threading to run a timer that requests a new token then,
		# so that will prevent requesting a new token for each json request ***
		try:
			client_auth = requests.auth.HTTPBasicAuth(myDetailsDict['Client_Id'], myDetailsDict['Secret'])
			post_data = {"grant_type": "password", "username": myDetailsDict['User'], "password": myDetailsDict['Password']}
		
			headers = {"User-Agent": user_agent}
			response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
			access_token = response.json()
			token = access_token["access_token"]
			token = "bearer " +str(token)
			headers = {"Authorization": token, "User-Agent": user_agent}
			return headers
		except:
			self.pres.WriteError(e,"GetOAuth2Token")	

	def GetJSON(self, url):
		"""This method gets the JSON object from a specific url"""
		try:
			global headrs
			response = requests.get(url, headers=headrs)
			obj = response.json()
			return obj
					
		except Exception,e:
			#As Reddit is down quite a bit, I thought I'd store the urls I had errors when trying to request data, Just writing them to a .csv
			#Will be able to go through this urls at a later stage to collect the data
			try:
				#Need to change the path for this
				fileobject=open('C:\Users\Kevin\Documents\Bot\mainfile\UrlErrors.csv','a')
			except:
				fileobject=open('C:\Users\Kevin\Documents\Bot\mainfile\UrlErrors.csv','w')
				fileobject.write("URL,DATETIME,ERROR\n")
			try:
				fileobject.write(str(url)+","+str(datetime.datetime.now())+","+str(e)+"\n")
				fileobject.close()
			except:
				pass

	def DateInputOLD(self,reason=None):
		if reason != None:
			print str(reason) + "\n"
		
		day = raw_input("Please enter a day in dd format : ")

		month = raw_input("Please enter a month in mm format : ")
		year = raw_input("Please enter a year in yyyy format : ")

		date = day+"/"+month+"/"+year
		print date

		unixTimeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
		return int(unixTimeStamp)

	def DateInput(self,reason=None):
		if reason != None:
			print str(reason) + "\n"
		isValid = False
		while not isValid:
			date = raw_input("Please enter a day in dd/yy/yyyy format : ")
			#This regular expression was taken from online
			isValid = re.match("[\d]{2}/[\d]{2}/[\d]{4}",date)

			if not isValid:
				print "Invalid date entered. Please try again."
			
			if isValid:
				days = 0
				feb = 28
				leaps = [1972,1976,1980,1984,1988,1992,1996,2000,2004,2008,2012,2016,2020,2024,2028,2032]
				longMonths=[1,3,5,7,8,10,12]
				shortMonths	=[2,9,4,6,11]
				dateParts = date.split("/")
				
				dateParts = [int(x) for x in dateParts]

				if dateParts[2]<1970 or dateParts[2]>2035:
					isValid = False
					
				if dateParts[1] in longMonths:
					days = 31
				elif dateParts[1] in shortMonths:
					days = 30
				else:
					isValid= False
					

				if dateParts[2] in leaps and dateParts[1] is 2:
					days = 29

				if dateParts[0]<1 or dateParts[0]>days:
					isValid = False
					




		unixTimeStamp = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
		return int(unixTimeStamp)

	def DateOutput(self, unixDate):
		date = datetime.datetime.fromtimestamp(int(unixDate)).strftime('%d-%m-%Y')
		return date

	def SelectPeriod(self):
		while True:
			self.pres.ClearScreen()
			print "Please select a unit of time to scrape : \n\t 1 : Week \n\t 2 : Month \n\t 3 : 2 Months \n\t 4 : 3 Months \n\t 5 : 6 Months"
			choice = raw_input()
			if choice == "1":
				return 604800
			elif choice == "2":
				return 2629743
			elif choice == "3":
				return 5259487
			elif choice == "4":
				return 7889231
			elif choice == "5":
				return 15778462
			else:
				print "Invalid choice"
				self.AnyKey()

	def CycleTimeSearchs(self,subReddit,limit):
		
		# subReddit = self.SelectSubReddit()
		startDate = self.db.ReturnSubReddit(subReddit)["created_utc"]
		currentDate = time.strftime("%d/%m/%Y")
		currentDateUnix = time.mktime(datetime.datetime.strptime(currentDate, "%d/%m/%Y").timetuple())
		choice = False
		
		while choice is False:
			self.pres.ClearScreen()
			
			print "Start Date   (Unix): " + str(startDate)
			print "Start Date         : "+ self.DateOutput(startDate)
			print "\nCurrent Date       : "+ str(currentDate)
			print "Current Date (Unix): " + str(currentDateUnix)
			print "\nDo you wish to scrape from this period or select dates?\n\n1: Scrape from this period\n2: Select dates\n\n"
			
			try:
				choice = int(input())
			except:
				print "Invalid Option"
				choice = False
				self.pres.AnyKey()
		
			if choice == 1:
				period = self.SelectPeriod()
			elif choice == 2:
				startDate = self.DateInput("Please enter the start date of the time period you wish to scrape : ")
				currentDateUnix = self.DateInput("Please enter the end date of the time period you wish to scrape : ") 
				period = self.SelectPeriod()
			else:
				print "Invalid option"
				choice = False
				self.pres.AnyKey()
		
		# Potential to change start date to scrape
		
		
		# limit = self.SelectLimit()
		
		while startDate< currentDateUnix:
			self.StoreTimeSearchedSubmissions(subReddit,limit,startDate, period)
			time.sleep(1)
			startDate = startDate + period

	def StoreSubmissions(self):
		"""The method for collecting submissions"""
		
		subReddit = self.SelectSubReddit()
		limit = self.SelectLimit()
		section = self.SelectSubRedditSection()
		if section == 5:
			self.CycleTimeSearchs(subReddit,limit)
			return
		elif section == 0:
			return
		else:
			number = 0
			lastsub = ""
			jsonList = []
			successcounter = 0
			
			while(number<int(limit)):
				self.pres.ClearScreen()
				print "Scraping SubReddit : "+subReddit
				if number != 0:
					print (str(successcounter) +" entries have been successfully entered out of " + str(number))
					print "The last submission checked was "+str(lastsub) +"\n"
				
				#Time sleep to prevent overrequesting by the scraper
				time.sleep(1)
		
				jsonList = self.GetSubmissionJSON(number,lastsub, subReddit,section)
				
				try:#Cycling through the json object to insert individual submissions in the DB
					for item in jsonList["data"]["children"]:
						success = self.db.InsertSubmission(item)
						lastsub = str(item["data"]["name"])
						#Success counter to let the user know how many entries to DB
						if success is True:
							successcounter = successcounter+1
					#change back to 25 if changing
					number = number +100
				except Exception,e:
					number = number +100
					self.pres.WriteError(e,"StoreSubmissions")

	def StoreTimeSearchedSubmissions(self, subReddit,limit, startDate, period):

		number = 0
		lastsub = ""
		jsonList = []
		successcounter = 0

		while(number<int(limit)):
			self.pres.ClearScreen()
			print "Scraping SubReddit : "+subReddit
			if number != 0:
				print (str(successcounter) +" entries have been successfully entered out of " + str(number))
				print "The last submission checked was "+str(lastsub) +"\n"
			
			#Time sleep to prevent overrequesting by the scraper
			time.sleep(1)
	
			jsonList = self.GetTimeStampSearchJSON(number,lastsub, subReddit, startDate, period)
			
			try:#Cycling through the json object to insert individual submissions in the DB
				for item in jsonList["data"]["children"]:
					success = self.db.InsertSubmission(item)
					lastsub = str(item["data"]["name"])
					#Success counter to let the user know how many entries to DB
					if success is True:
						successcounter = successcounter+1
				if len(jsonList["data"]["children"])<100:
					#Exit the method early if less than 100 results per page to prevent time wasted after a search
					return
				number = number +100
			
			except Exception,e:
				self.pres.WriteError(e,"StoreTimeSearchedSubmissions")

	def GetSubmissionJSON(self,number,lastSub, subReddit,section):
		"""a method that gets the json data from a constructed url and returns a json object"""

		if section not in ["/new/.json","/hot/.json","/controversial/.json"]:
			if number==0:
				url = "https://oauth.reddit.com/r/"+str(subReddit)+str(section)
			else:
				url = "https://oauth.reddit.com/r/"+str(subReddit)+str(section)+"count="+str(number)+"&after="+str(lastSub)
		else:
			if number==0:
				url = "https://oauth.reddit.com/r/"+str(subReddit)+str(section)
			else:
				url = "https://oauth.reddit.com/r/"+str(subReddit)+str(section)+"?count="+str(number)+"&after="+str(lastSub)
			print "The current url is " + str(url)
			#raw_input('Continue?')
		
		try:
			result = self.GetJSON(url)
		except Exception,e:
			self.pres.WriteError(e,"GetSubmissionJSON")
		
		return result

	def GetTimeStampSearchJSON(self,number,lastSub,subReddit,startDate,period):

		#month = 2629743.83
		#week = month/4
		
		if number ==0:
			url = "https://oauth.reddit.com/r/"+str(subReddit)+"/search.json?sort=top&q=timestamp:"+str(int(startDate))+".."+str(int(startDate+period))+"&syntax=cloudsearch&restrict_sr=on"
			print "The current url is " + str(url)
		else:
			url = "https://oauth.reddit.com/r/"+str(subReddit)+"/search.json?sort=top&q=timestamp:"+str(int(startDate))+".."+str(int(startDate+period))+"&syntax=cloudsearch&restrict_sr=on&count="+str(number)+"&after="+str(lastSub)
			print "The current url is " + str(url)
		
		try:
			result = self.GetJSON(url)	
		except Exception,e:
			self.pres.WriteError(e,"GetTimeStampSearchJSON")

		return result

	def StoreComments(self):
		"""Method to Store Comments, accepts a list of subs stored in the DB"""
		subReddit = self.SelectSubReddit()
		print subReddit
		subReddit = self.db.ReturnSubReddit(subReddit)
		subRedditId = subReddit["name"]
		
		print "Scraping from "+subReddit["name"]
		
		self.pres.AnyKey()
		print "Do you wish to scrape all comments from Subreddit or from a specific time period? \n\n\t1 : All\n\t2 : Time Period"
		choice = raw_input()
		
		if choice == "1":
			listSubs = self.db.ReturnAllSubmissionDetails(subRedditId)
		
		elif choice == "2":
			print "Please enter start date to search from : "
			startDate = self.DateInput()
			print "Please enter end date"
			endDate = self.DateInput()
			listSubs = self.db.ReturnSubmissionsDetailsByPeriod(subRedditId,startDate,endDate)
	
		print listSubs.count()
		self.pres.AnyKey()

		#Prints the total number of comments and submissions in the db
		totalComs = self.db.comments.count()
		totalSubs = listSubs.count()
		subsScraped = 0
		comments = 0
		errors = 0
		
		#Cycles through the list of submissions and using the data to create a url and then collect the comment data for each submission
		for sub in listSubs:
			self.pres.ClearScreen()
			print "Submissions scraped : "+ str(subsScraped)
			print "Errors              : "+ str(errors)
			print "Submissions left    : "+ str(totalSubs-subsScraped)
			print "Total Comments      : "+ str(totalComs)
			print "Comments Stored     : "+ str(comments)
			print str(sub["subreddit"])
			print str(sub["id"])
			url = "https://oauth.reddit.com/r/"+str(sub["subreddit"])+"/comments/"+str(sub["id"])+"/?limit=500"
			print "Current url being scraped is \n:"+ url
			
			try:
				coms = self.CollectComments(url)
				for com in coms:
					print com["data"]["name"]
					success = self.db.InsertComment(com)
					if success:
						comments = comments + 1
						totalComs = totalComs + 1
				time.sleep(1)
				subsScraped = subsScraped +1

			except Exception,e:
			 	errors = errors + 1
			 	time.sleep(1)
			 	subsScraped = subsScraped +1
			 	self.pres.WriteError(e,"StoreComments : coms = self.CollectComments(url)")

	def CollectComments(self,url):
		"""The method that accepts the JSON data of a Submission url  and then feeds it into a comment flattening method.
		this then returns a list of flattened comment objects"""
		
		redditData = self.GetJSON(url)
		commentTree = redditData[1]
		comments = self.FlattenCommentTree(commentTree)
		return comments
		
	def FlattenCommentTree(self,commentTree):
		"""This is a recursive method for flattening the tree structure of a submission's comment page"""

		#list to be returned at the end. 
		flattenedList = []
		#list to be returned from the recursive
		replylist = []
		#assigning the list of comments to comments
		
		comments = commentTree["data"]["children"]
		#test is comments a list
		if isinstance(comments, list):
			#print "is list"
			#append each comment in top level list of comments to flattenedList
			for item in comments:
				flattenedList.append(item)
				#assign a comments replies attribute to var replies
				try:
					replies = item["data"]["replies"]
					replylist= replylist + self.FlattenCommentTree(replies)
				except:
					pass
					#self.pres.WriteError("End of available list","FlattenCommentTree")
					
				#if replies contains a json object with ["data"]["children"] this try will work and the method will call itself

			#return the two lists joined
			returnlist = flattenedList + replylist
			return returnlist
		else:
			self.pres.WriteError("Not a list","FlattenCommentTree")
			#returns comments as list

	def CollectSubReddits(self):
		number = 0
		lastSubReddit= ""
		successcounter = 0

		while number<9000:
			if number == 0:
				url = "https://oauth.reddit.com/subreddits.json"
			else:
				url = "https://oauth.reddit.com/subreddits.json?count="+str(number)+"&after="+lastSubReddit
			
			if number != 0:
				self.pres.ClearScreen()
				print (str(successcounter) +" entries have been successfully entered out of " + str(number))
				print "The last SubReddit checked was "+str(lastSubReddit) +"\n"

			time.sleep(1)

			jsonList = self.GetJSON(url)
			try:
				for item in jsonList["data"]["children"]:
					success = self.db.InsertSubReddit(item)
					lastSubReddit = str(item["data"]["name"])

					if success is True:
						successcounter = successcounter + 1
			except Exception,e:
				self.pres.WriteError(e,"CollectSubReddits")
				#self.pres.AnyKey()
			number = number + 100

class Analysis(object):
	"""docstring for Analysis"""
	def __init__(self):
		self.wordCount =[]

	def TestNormality(self,array):
		array = np.array(array)
		print stats.normaltest(array)
		if array[1] <0.2:
			print "Unlikely to be normally distributed"
			return False
		else:
			print "The dataset is likely to be normally distributed"
			return True

	def TestCorrelation(self,setOne,setTwo):
		setOne = np.array(setOne)
		setTwo = np.array(setTwo)
		results = pearsonr(setOne,setTwo)
		if results[1]<0.2 and results[1]>-0.2:
			print "These data sets are not correlated"
		elif results[1]>0.6:
			print "There is a positive correlation"
		elif results[1]<-0.6:
			print "There is a negative correlation"
		print results

class ThreadingTimer(threading.Thread):
	"""docstring for ThreadingTimer"""
	def __init__(self):
		threading.Thread.__init__(self)
		self.headers = self.GetOAuth2Token()
		self.event = threading.Event()
		self.scrape = ScrapingMethods()
	
	def run(self):
		while not self.event.is_set():
			self.RefreshToken()
			self.event.wait(3600)

	def GetOAuth2Token(self):
		print "getting TOKEN"
		path = "C:\Users\Kevin\Documents\Bot\Mainfile\\accountdetails.txt"
		#I stored the details in a txt file in python dict format for easy access
		try:
			details = open(path,'r').read()
			myDetailsDict = eval(details)
		except Exception, e:
			self.pres.WriteError(e,"GetOAuth2Token")

		user_agent = "College Data collection project by u/Ouiski"
			
		#Acquiring an authentication token
		#*** I want to change this part to that the scraper automatically collects a token every 3600s(its expiry length I believe)
		# It'll require a bit of restructuring, but if I can use threading to run a timer that requests a new token then,
		# so that will prevent requesting a new token for each json request ***
		try:
			client_auth = requests.auth.HTTPBasicAuth(myDetailsDict['Client_Id'], myDetailsDict['Secret'])
			post_data = {"grant_type": "password", "username": myDetailsDict['User'], "password": myDetailsDict['Password']}
		
			headers = {"User-Agent": user_agent}
			response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
			access_token = response.json()
			token = access_token["access_token"]
			token = "bearer " +str(token)
			headers = {"Authorization": token, "User-Agent": user_agent}
			return headers
		except:
			self.pres.WriteError(e,"GetOAuth2Token")	

	def RefreshToken(self):
		global headrs
		self.headers = self.GetOAuth2Token()
		headrs = self.headers

global headrs

#dbInt = DataBaseInteractions()
pres = PresentationMethods()
# analysis = Analysis()

#print dbInt.db.command("collstats")
#print dbInt.db.command("dbstats")
pres.Menu()




