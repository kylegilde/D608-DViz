load_packages <- c("prettydoc", "jsonlite", "knitr", "tidyverse")

#see if we need to install any of them
install_load <- function(pkg){
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg)) 
    install.packages(new.pkg, dependencies = TRUE)
  sapply(pkg, require, character.only = TRUE, quietly = TRUE)
}

install_load(load_packages)


View(my_results)

rm(crime_df)
crime_df <- read.csv("https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv?accessType=DOWNLOAD")

crime_df_v2 <- crime_df %>% dplyr::select(c(Date, Primary.Type, Description, Location, Arrest, 
                                      Domestic, Community.Area, Year, Latitude, Longitude))

write.csv(crime_df_v2, "crime_df_v2.csv")
crime_df_v2 <- read.csv("crime_df_v2.csv")

crime_df_ <- 

View(head(crime_df_v2,100))
