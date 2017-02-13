followers_out_set<-scores[!(scores$twitter_handle %in% user_fans$screenName),] #subset op. leaders not followed
#Say we suggest 5 opinion leaders that are far ideologically different from the user
pick<-sample(1:nrow(followers_out_set),5,prob=abs(followers_out_set$ideology_score-users_ideology_score)) # Probability based on absolute difference score
suggest_set<-followers_out_set[pick,]
suggest_set
