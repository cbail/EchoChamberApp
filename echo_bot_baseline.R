## The baseline code to retweet posts from sources to the echo chamber bot

library(stringr)
library(twitteR)
library(ROAuth)

# Load the opinion leader handles
handleset<-read.csv("https://docs.google.com/spreadsheets/d/1iIkn_K3H5GpvOGn4GlIaB9HdKjuCw7_kZsHlku68xJg/pub?output=csv")

# Connect to ConservativeEchoBot (@EchoBot3)
api_key <- "TcLXWUtB0FqdP9u9cA2zeNH8n"
api_secret <- "8Q6cizMCw8hLGVCAlLT7398Xve8vw3Z5dEOKDlbW1xadT8vndA"
access_token <- "831320825676648448-QKrowo3WAknXuiKcq7Vm7RcDipxEL07"
access_token_secret <- "RzaQC6dsf9JLbIlL86ZHKZZJRJ7qAJskRk0Czb78alOEk"
setup_twitter_oauth(api_key,api_secret,access_token,access_token_secret)

# Choose a handle and retweet a post
handle<-sample(handleset$twitter_handle[which(handleset$ideology_score>1)],1) # choose handle (ideology>1)
post<-twListToDF(userTimeline(handle, n=1))$text # Get most recent post
post<-paste("RT ","@",handle,":",post,sep="") # Put "RT" and source in the front
post<-gsub('http.* *', '',post) # remove URLs if any (linked to the tweet itself) 
tweet(post) # tweet 
