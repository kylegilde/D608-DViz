

installed_and_loaded <- function(pkg){
  # Load packages. Install them if needed.
  # CODE SOURCE: https://gist.github.com/stevenworthington/3178163
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg)) install.packages(new.pkg, dependencies = TRUE)
  sapply(pkg, require, character.only = TRUE, quietly = TRUE, warn.conflicts = FALSE)
}

# required packages
packages <- c("shiny","tidyverse", "ggthemes", "shinythemes", "quantmod", "zoo") 
installed_and_loaded(packages)

# read data
cdc <- read.csv("https://raw.githubusercontent.com/kylegilde/D608-Data-Viz/master/data/cleaned-cdc-mortality-1999-2010-2.csv")
str(cdc)

# add YoY variables
cdc <- cdc %>% 
  arrange(State, ICD.Chapter, Year) %>% 
  group_by(State, ICD.Chapter) %>% 
  mutate(
    YoY.Pct.Change.Crude.Rate = Delt(Crude.Rate) * 100,
    YoY.Change.Crude.Rate = Crude.Rate - dplyr::lag(Crude.Rate)
  ) 


# create national-level df 
nationwide_cdc <- cdc %>% 
  group_by(Year, ICD.Chapter) %>% 
  summarise(
    Population = sum(Population),
    Deaths = sum(Deaths),
    Crude.Rate = Deaths / Population * 100000
  ) %>% 
  arrange(ICD.Chapter, Year) %>% 
  group_by(ICD.Chapter) %>% 
  mutate(
    YoY.Pct.Change.Crude.Rate = Delt(Crude.Rate) * 100,
    YoY.Change.Crude.Rate = Crude.Rate - dplyr::lag(Crude.Rate)
  )

# plotting parameter
years <- range(cdc$Year)
y_breaks <- seq(years[1], years[2], by = 2)


# create UI
ui <- fluidPage(theme = shinytheme("cosmo"),


  #headerPanel("Homework #3: Shiny App"),
  # tab title
  title = "Homework #3",
  
  h1("CUNY DS608 Data Viz", align="center"),
  h2("Homework #3: Shiny App", align="center"),
  h3("Kyle Gilde", align="center"),

  tabsetPanel(
    # TAB #1
    tabPanel("Question 1",
      # Page title
      column(12, align="center", titlePanel("2010 Crude Mortality Rates by State")),
      h4("(Deaths per 100,000)", align="center"),
      
      sidebarLayout(
        sidebarPanel(
          # dropdown menu
          selectInput(inputId = "causeSelector", 
                      label = "Select Cause of Death", 
                      choices = unique(cdc2010$ICD.Chapter)      
          )
        ),
        mainPanel(
          # Create a spot for the barplot
          plotOutput("state2010Plot")     
        )
      )
    ),
    # TAB #1  
    tabPanel("Question 2",
             
    # Page title
    column(12, align="center", titlePanel("National vs. State Year-over-Year Change in Mortality Rate")),
    h4("(Black Line = National Mortality Rate)", align="center"),
    
      sidebarLayout(
        sidebarPanel(    
          # dropdown menus
          selectInput(inputId = "causeSelector2", 
                      label = "Select Cause of Death", 
                      choices = unique(cdc2010$ICD.Chapter)
          ),
          selectInput(inputId = "stateSelector", 
                      label = "Select States", 
                      choices = unique(cdc2010$State),
                      multiple = TRUE
          )
        ),
        mainPanel(
          # Create a spot for the smoothplot
          plotOutput("MortalityRateChange")      
        )
      )
    )
  )
)


server <- function(input, output) {
  
  # PLOT #1
  output$state2010Plot <- renderPlot({
    
    plot_data <- subset(cdc2010, ICD.Chapter == input$causeSelector)
    
    # Render Barplot
    ggplot(data = plot_data) + 
      geom_bar(mapping = aes(x = factor(plot_data$State, levels = plot_data$State[order(plot_data$Crude.Rate)]),
                             y = Crude.Rate), 
               stat = "identity") + 
      scale_y_continuous(position = "right") + 
      coord_flip() +
      theme_fivethirtyeight()
  }, height = 800)
  
  # PLOT #2
  output$MortalityRateChange <- renderPlot({
    
    plot_data <- subset(cdc2010, ICD.Chapter == input$causeSelector2)
    
    state_df <- subset(cdc, ICD.Chapter == input$causeSelector2 & State %in% input$stateSelector)
    national_df <- subset(nationwide_cdc, ICD.Chapter == input$causeSelector2)
    
    # Render Smooth Plot
    ggplot() +
      geom_smooth(data = state_df, 
                  mapping = aes(x = Year, y = YoY.Change.Crude.Rate, col = State), 
                  se = FALSE) +
      geom_smooth(data = national_df, 
                  mapping = aes(x = Year, y = YoY.Change.Crude.Rate), 
                  size = 2, 
                  color = "Black") +
      scale_x_continuous(breaks = y_breaks) +
      theme_fivethirtyeight()
  }, height = 800 )  
}

shinyApp(ui = ui, server = server)

#REFERENCES & EXAMPLES
#https://shiny.rstudio.com/articles/layout-guide.html
#https://shiny.rstudio.com/gallery/telephones-by-region.html
#http://rstudio.github.io/shinythemes/
#https://rstudio-pubs-static.s3.amazonaws.com/7433_4537ea5073dc4162950abb715f513469.html

