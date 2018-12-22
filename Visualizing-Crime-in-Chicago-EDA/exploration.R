

#see if we need to install any of them
install_load <- function(pkg){
  new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if (length(new.pkg)) 
    install.packages(new.pkg, dependencies = TRUE)
  sapply(pkg, require, character.only = TRUE, quietly = TRUE)
}

load_packages <- c("prettydoc", "jsonlite", "knitr", "lubridate",
                   "tidyverse", "anytime", "data.table")
install_load(load_packages)


# View(my_results)
# 
# rm(crime_df)
# crime_df <- read.csv("https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv?accessType=DOWNLOAD")
# 
# crime_df_v2 <- crime_df %>% dplyr::select(c(Date, Primary.Type, Description, Location, Arrest, 
#                                       Domestic, Community.Area, Year, Latitude, Longitude))
# 
# write.csv(crime_df_v2, "crime_df_v2.csv")


setwd("C:\\Users\\kyleg")
crime_df_v2 <- data.table(read.csv("crime_df_v2.csv"))
str(crime_df_v2)

crime_samp <- sample_n(crime_df_v2, 1000)
# crime_tab <- table(crime_samp$Primary.Type)
# 
# crime_samp2 <- data.frame(
#   crime = names(crime_tab),
#   incidents = as.integer(crime_tab)
# )
# write.csv(crime_samp2, "crime_samp2.csv")
# 
# write.csv(crime_samp, "crime_samp.csv")

crime_samp2 <- 
  crime_samp %>% 
  mutate(
    originalDate = Date,
    DateTime = lubridate::mdy_hms(as.character(Date)),
    Date = as.Date.POSIXct(DateTime),
    Year = year(DateTime),
    Month = month(DateTime, label = T),
    DayOfMonth = day(DateTime),
    DayOfWeek = wday(DateTime),
    Hour = hour(DateTime)
  )
anytime(as.character(crime_samp$Date))


str(crime_samp2)
lubridate::as_date()
crime_samp2[, c("originalDate", "Date")]

            