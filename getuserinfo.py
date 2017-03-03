##This is the second step to look up information about the people the elites follow
##Right now its set to look up people followed by at least 20 elites
##and also to only output those accounts that are verified <-- we may or may not want this

##code is based on this tutorial: https://codeandculture.wordpress.com/2016/01/19/scraping-twitter-with-python/
##Needs python 3.6 to run to avoid UTF encoding errors when writing to CSV

#Import needed packages
from twython import Twython
import sys
import time
import pandas as pd
from math import ceil
from requests.exceptions import Timeout, ConnectionError #import error types for try/except
from requests.packages.urllib3.exceptions import ReadTimeoutError

targetlist='followed_ids.txt'
today = time.strftime("%Y%m%d")

#import CSV of data to lookup as pandas dataframe
scraped_followers_df = pd.read_csv("userstolookup.csv", dtype=object) #note- CSV has 1mil + entries and is too large to open/save properly in excel
scraped_followers_df.columns = ["ID", "num_elite_follow"] #because of ^, must rename cols here
scraped_followers_df["num_elite_follow"] = scraped_followers_df["num_elite_follow"].astype(int) #converting column from string to int
scraped_followers_df = scraped_followers_df.set_index('ID')

##checking dimensions to be sure the data loaded properly
print(list(scraped_followers_df))
print(scraped_followers_df.head())
print(scraped_followers_df.shape)


"""
#the below operations indicate I have a couple of repeat ids
#(likely because I restarted the code once due to interruption)
friendsofelites = scraped_followers_df['ID'].tolist()
print(len(friendsofelites))
print(len(list(set(friendsofelites))))
#vc = pd.Series(friendsofelites).value_counts()
#print(vc[vc > 1].index.tolist())
"""

#this code condenses the repeat id numbers, and sums counts
scraped_followers_df=scraped_followers_df.groupby(scraped_followers_df.index).sum() #renames "ID" to "index" for some reason
print(list(scraped_followers_df))
print(scraped_followers_df.head())
print(scraped_followers_df.shape)
#below shows duplicates are now gone
unique_handles = scraped_followers_df.index.tolist()
print(len(unique_handles))
print(len(list(set(unique_handles))))

##Subsets down to data with only x number of followers (20 in current code)
scraped_followers_df= scraped_followers_df[(scraped_followers_df['num_elite_follow'] > 20 )]

"""
##checking length again
print(len(scraped_followers_df))
handles = scraped_followers_df.index.tolist()
print(len(handles))
"""
#authenticate
t = Twython(
'Your consumer key here', #consumer key
'your consumer secret here' #consumer secret
)


#function to export to CSV
#this custom fuction (from rossman's code) is necessary
#bc users dont always have the same number of entries in their data dictionaires
def tw2csv(twdata,csvfile_out):
    import csv
    import functools
    allkey = functools.reduce(lambda x, y: x.union(y.keys()), twdata, set())
    with open(csvfile_out,'wt') as output_file:
        dict_writer=csv.DictWriter(output_file,allkey)
        dict_writer.writeheader()
        dict_writer.writerows(twdata)



#API allows 100 users per query. Cycle through, 100 at a time
#users = twitter.lookup_user(screen_name=handles) #this one line is all you need if len(handles) < 100
verified_users=[] #initialize data object
hl=len(handles)
cycles=ceil(hl/100) #find out numbers of look up cycles of 100 needed to finish
n=1
for i in range(0, cycles):
    try: #added try/except due to connection time out issues.
        print("currently running cycle: " + str(n))
        h=handles[0:100]
        incremental = t.lookup_user(user_id=h) #this is the main/important line of code--calls api to look up user info by their ids
        for user in incremental:
            if user["verified"] == True: #right now I'm only keeping verified accounts but we could delete these 2 lines if we dont want that
                verified_users.append(user)
        time.sleep(75) ## 75 second rest between api calls. The API allows 15 calls per 15 minutes so this is conservative
        del handles[0:100] #moved here from example code so handles arent deleted until sucesfully scraped, if an exception/error occurs

        print("just completed cycle: " +str(n)) #these lines of code keep track of progress :)
        print(str(cycles-n) + " cycles remaining.")
        n+=1
    except (Timeout, ssl.SSLError, ReadTimeoutError, ConnectionError) as exc: #restart loop w/o breaking if there's a time out issues
        print("Time out/Connection error encountered--trying again!")
        time.sleep(75)

filename='friendsofelites_'+today+'.csv' #defines name of file to export to
tw2csv(verified_users,filename) #exports to file
