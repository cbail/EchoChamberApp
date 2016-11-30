#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(twitteR)
library(ggplot2)

# Define UI for application that draws a histogram
ui <- shinyUI(fluidPage(
   
   # Application title
   titlePanel("Echo Chamber App"),
   
   # Sidebar with a slider input for number of bins 
   sidebarLayout(
      sidebarPanel(
        textInput("term", "Enter your Twitter handle here:", "")
      
      ),
      
      # Show a plot of the generated distribution
      mainPanel(
         plotOutput("TwitterPlot")
      )
   )
))

# Define server logic required to draw a histogram
server <- shinyServer(function(input, output) {
   
   output$TwitterPlot <- renderPlot({
      
     setup_twitter_oauth("0WOTlq9uxTuqrviYHK5dSrNXC", 
                         "qpvR9L0TpTuWEHg6tCGHIdD6iFe3eWW7F3qBEeXWIbzipjsywv", 
                       )
     
     token <- get("oauth_token", twitteR:::oauth_cache)
     token$cache()
     
     
     user<-getUser("@chris_bail")
     user_fans<-user$getFriends()
     user_fans<-twListToDF((user_fans))
     scores<-read.csv("https://docs.google.com/spreadsheets/d/1iIkn_K3H5GpvOGn4GlIaB9HdKjuCw7_kZsHlku68xJg/pub?output=csv")
     followers_in_set<-scores[scores$twitter_handle %in% user_fans$screenName,]
     users_ideology_score<-mean(followers_in_set$ideology_score)
     
     ggplot(scores, aes(x=ideology_score))+
       geom_histogram(color="gray")+
       geom_vline(xintercept=users_ideology_score)+
       geom_text(aes(0,users_ideology_score,label = "Your ideology score", vjust = -3),color="purple")+
       theme_minimal()+
       xlab("liberal                                conservative")+
       ylab("Number of Twitter Opinion Leaders")
     
   })
})

# Run the application 
shinyApp(ui = ui, server = server)

