##This is the first step to get IDs of all the people the elites in our set follow
##Currently gets congress ids + those added in Jan 2016 update

##code is based on this tutorial: https://codeandculture.wordpress.com/2016/01/19/scraping-twitter-with-python/
##Needs python 3 to run to avoid UTF encoding errors when writing to CSV

#import needed packages
from twython import Twython, TwythonError
import pandas as pd
import time

#set up authentication
t = Twython(
'Your consumer key here', #consumer key
'your consumer secret here' #consumer secret
)

"""
#importing list of opinion leaders whose followers were already scraped
#-- allows to do in multi steps w/o starting over
already_done_list='scraped_ids.201703020.txt'
done_ones = [line.rstrip() for line in open(already_done_list)]
print(len(done_ones))
"""
scrapedInfo = {} #initializes dictionary to add scraped user info to
#^^(will ultimately be a list of dictionaries where key = user ID and value = number of people in the elite set who follow them)
#^^was the best method I could think of to be able to update follower counts, but it may not be the best way...

"""
#import data for previously scraped followers if resarting after a halted scraping session
scraped_followers_df = pd.read_csv("userstolookup20170302.csv", dtype={'ID': object})
for index, row in scraped_followers_df.iterrows():
    scrapedInfo[row['ID']] = row['num_elite_follow']
print(scrapedInfo)
"""

#get list of opinion leaders from CSV file and convert to python list
leaders = pd.read_csv("congress_twitters.csv")
lead_list = list(leaders.twitter_handle)

#adding new folks (from list used in Barberas 2016 update)
rep_cands =["RealBenCarson", "tedcruz", "CarlyFiorina", "GrahamBlog",
    "GovMikeHuckabee", "GovernorPataki", "RandPaul", "marcorubio",
    "RickSantorum", "bobbyjindal", "GovernorPerry", "realDonaldTrump",
    "JebBush", "GovChristie", "JohnKasich", "ScottWalker",
    "gov_gilmore"]

dem_cands = ['HillaryClinton', 'BernieSanders', "MartinOMalley",
    "LincolnChafee", "JimWebbUSA"]

media = ["EconUS", "BBCWorld", "nprnews", "NewsHour", "WSJ", "ABC",
    "CBSNews", "NBCNews", "CNN", "USATODAY", "theblaze", "nytimes",
    "washingtonpost", "msnbc", "GuardianUS", "Bloomberg", "NewYorker",
    "politico", "YahooNews", "FoxNews", "MotherJones", "Slate", "BreitbartNews",
    "HuffPostPol", "StephenAtHome", "thinkprogress", "TheDailyShow",
    "DRUDGE_REPORT", "dailykos", "seanhannity", "ajam", "edshow",
    "glennbeck", "rushlimbaugh", "BuzzFeedPol"]

politicians = ["algore", "MittRomnney", "SarahPalinUSA", "KarlRove", "POTUS",
    "JoeBiden", "newtgingrich", "TheDemocrats", "GOP", "billclinton",
    "GeorgeHWBush", "dccc", "HouseDemocrats", "SenateDems", "Senate_GOPs", "HouseGOP"]
journalists = ["maddow", "glennbeck", "limbaugh", "andersoncooper", "gstephanopoulos",
    "AnnCoulter", "seanhannity", "oreillyfactor", "megynkelly", "MHarrisPerry"] # journalists
interest_groups = ["Heritage", "OccupyWallSt", "HRC", "RANDCorporation", "BrookingsInst",
    "CatoInstitute", "AEI", "NRA", "glaad", "ACLU"] # interest groups

full_list = list(set(lead_list + rep_cands + dem_cands + media + politicians
                        + journalists + interest_groups))
print(len(full_list))

"""
#removes users already looked up from list to look up if restarting
full_list = list(set(full_list)-set(done_ones)) #removes those we have data for
print(len(full_list))
"""
#full_list = ["mbfhunzaker"] #single user for testing

scraped_users = []
bad_ids = []
for leader in full_list:
    scraped_users.append(leader) #keeps list of who's already been scraped incase you have to stop/start the code
    #^^ is output as the file that will be imported as the "already_done_list" above
    cur = -1 # used to function argument to 1st page of followers--idk why -1 if the first page...
    try:
        while cur !=0: # until you run out of pages of followers...

            followers = t.get_friends_ids(screen_name = leader, cursor = cur) #this line is the API call that looks up the people that user follows in chunks of 5000
            follower_ids = followers["ids"] #extracts list of follower ids from API call data
            for user_id in follower_ids: #iterates over list of ids
                if user_id not in scrapedInfo: #if we dont already have the user in our dictionary of users
                    print(user_id)
                    #scrapedInfo[user_id]=leader #method to keep track of who follows
                    scrapedInfo[user_id]= 1 #method to keep track of how many follow; sets to 1 if not in our set yet
                elif user_id  in scrapedInfo: #if we DO have the user in our dictionary of users (e.g. if they're followed by someone we already scraped)
                    #scrapedInfo[user_id] = scrapedInfo[user_id] + ", " + leader #method to keep track of *who* follows
                    scrapedInfo[user_id]=scrapedInfo[user_id] +1 #method to keep track of how many follows them; increments count of elites who follow them by 1
                else:
                    print("ruh-roh!") #just in case... maybe should set up a list of these instead, but i don't think its ever happened
            cur = followers['next_cursor'] #go to next page of peole the user follows
            print(leader + " cursor # = " + str(cur))
            print("added " + str(len(follower_ids)) + " for "+ leader)
            time.sleep(75) ## 75 second rest between api calls. The API allows 15 calls per 15 minutes so this is conservative
    except: #this keeps track of IDs that couldn't be looked up for some reason -- usually bc they changed their username--i only had 2 of these
        bad_ids.append(leader)
        print(leader + " is a bad ID :( ")
        time.sleep(75)

    print("Bad Ids:")
    print(bad_ids)

    ##this last part of the code saves out a CSV of ids of people the elites follow/follow counts
    ##as well as a text file that lists everyone whose been scraped so far
    ## right now I do this at each loop in case the there is an error/the connection is cut
    ## with file names that are unique by hour so if something goes wrong with saving ideally we don't lose more than an hour or two of work
    ## ^^ may not be ideal, however....

    now = time.strftime("%Y%m%d%H")

    ##converts scrapedInfo dictionary to pandas dataframe and saves it out as a CSV file where keys (ids) are col 1 and values (elite follower counts) are col 2
    filename =("userstolookup" + now + ".csv")
    scrapedInfodf = pd.DataFrame.from_dict(scrapedInfo, orient='index')
    scrapedInfodf.to_csv(filename)


    ##saves out a text file of ids of all teh users we've scraped so far
    ##(this file would be imported as already_done_list at the top of file,
    ##if you were stopping/restarting scraping)
    id_file = open('scraped_ids.'+ now + '.txt', 'w')
    for item in scraped_users:
        id_file.write('%s\n' % item)

    print(len(scraped_users))

print("All Done! :)")
