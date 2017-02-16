library(stringr)
library(twitteR)
library(ROAuth)
# library(sendmailR)

Load_data <- function(address){
  data <- read.csv(address)
  return(data)
}

Login <- function(){
  # Connect to ConservativeEchoBot (@EchoBot3)
  # username: EchoBot3
  # password: GraysonAllen
  api_key <- "TcLXWUtB0FqdP9u9cA2zeNH8n"
  api_secret <- "8Q6cizMCw8hLGVCAlLT7398Xve8vw3Z5dEOKDlbW1xadT8vndA"
  access_token <- "831320825676648448-QKrowo3WAknXuiKcq7Vm7RcDipxEL07"
  access_token_secret <- "RzaQC6dsf9JLbIlL86ZHKZZJRJ7qAJskRk0Czb78alOEk"
  setup_twitter_oauth(api_key,api_secret,access_token,access_token_secret)
}


Retweet <- function(lowbound, upbound, N, retweet = T){
  # Sample N handlers to retweet their most recent status.
  handles<-sample(handleset$twitter_handle[which(handleset$ideology_score>lowbound & handleset$ideology_score<upbound)], 2) # choose handle (ideology>1)
  # Store the retweeted statuses in a matrix.

  for (i in 1:length(handles)){
    handle_info <- rep(NA, 5)
    names(handle_info) <- c("handle", "ScreenName", "status_id", "text", "time") # The first and second should equals. Just to cross-validate
    
    handle <- as.character(handles[i])
    status <- twListToDF(userTimeline(handle, n=1))
    status_c <- statusFactory$new(text=status$text, screenName=status$screenName, id=status$id) # convert the status into a S4 status class.
    if (retweet){
      retweetStatus(status_c) # Retweet.  
    } else{
      status <- paste("RT ",handle,":",post,sep="") # Put "RT" and source in the front
      # status <- paste("RT ","@",handle,":",post,sep="") # Put "RT" and source in the front
      status <- gsub('http.* *', '',post) # remove URLs if any (linked to the tweet itself) 
      tweet(status) # tweet 
    }
    time <- Sys.time()
    handle_info <- c(handle, status_c$getScreenName(), status_c$getId(), gsub("\n", "", status_c$getText()), time)
    Write_log(handle_info)
    print(paste0("Retweeted ", i, " of ", length(handles))) # Check the content of the tweet. Email?
    if (i < length(handles)) Sys.sleep(runif(1, 10, 20)) # Stop, to avoid 403 error
  }
  # TODO: add some error-handling mechanism (e.g. 403 error)
}

Scheduler <- function(){
  # Under construction
}

Write_log <- function(handle_info){
  write.table(retweeted_info, file = "tweet_bot_log.txt", quote=F, sep="\n", eol = "\n[ENDEND]\n", row.names=F, col.names=F, append=T)
}

Email_Notify <- function(retweeted){
  # Still fiddling this module
  from <- "econotify@gmail.com"
  to <- "haohanch@gmail.com"
  subject <- "Retweeted Today"
  body <- "Test"                     
  mailControl=list(smtpServer="ASPMX.L.GOOGLE.COM")
  sendmail(from=from,to=to,subject=subject,msg=body,control=mailControl)
}


############
# Main 
############
HANDLER_ADDRESS <- "https://docs.google.com/spreadsheets/d/1iIkn_K3H5GpvOGn4GlIaB9HdKjuCw7_kZsHlku68xJg/pub?output=csv"
N_HANDLES_SAMPLE = 2
RETWEET <- T

handlerset <- Load_data(HANDLER_ADDRESS) # Get Handler data
Login() # Login to Twitter Bot (add function to log into differnt bots later)
  
# Retweet a sample of conservative accounts
# Four parameters: lower bound of ideology, upper bound of ideology, Number of handles to sample, retweet or copy
Retweet(1, Inf, N_HANDLES_SAMPLE, RETWEET) 
