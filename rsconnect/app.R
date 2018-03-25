library(shiny)
library(ggplot2)

cdc <- read.csv("https://raw.githubusercontent.com/kylegilde/D608-Data-Viz/master/data/cleaned-cdc-mortality-1999-2010-2.csv")
str(cdc)

cdc2010 <- subset(cdc, Year == 2010)
title1 <- "Crude Mortality Rates by State in 2010"

ui <- fluidPage(
  
  #tab title
  title = title1,
  
  # Give the page a title
  titlePanel(title1),
  
  selectInput(inputId = "causeSelector", 
              label = "Select Cause of Death", 
              choices = unique(cdc2010$ICD.Chapter
              )
  ),
    
  # Create a spot for the barplot
    plotOutput("state2010Plot")
)

server <- function(input, output) {
  
  # Fill in the spot we created for a plot
  output$state2010Plot <- renderPlot({
    
    plot_data <- subset(cdc2010, ICD.Chapter == input$causeSelector)
    # Render a barplot
    ggplot(data = plot_data) + 
      geom_bar(mapping = aes(x = factor(plot_data$State, levels = plot_data$State[order(plot_data$Crude.Rate)]),
                             y = Crude.Rate), 
               stat = "identity") + 
      scale_y_continuous(position = "right") + 
      #labs(x = "State", y = "# Deaths per 100,000") +
      coord_flip() +
      theme_fivethirtyeight()
  }, height = 800)
}

shinyApp(ui = ui, server = server)

#https://shiny.rstudio.com/gallery/telephones-by-region.html
#https://rstudio-pubs-static.s3.amazonaws.com/7433_4537ea5073dc4162950abb715f513469.html

