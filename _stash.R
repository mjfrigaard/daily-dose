library(lubridate)

generate_md_dates <- function(start_from, end_with) {
  
  strt <- lubridate::ymd(start_from)
  end <- lubridate::ymd(end_with)
  
  dates <- seq(strt, end, by = "1 day")
  
  sorted_dates <- sort(dates, decreasing = TRUE)
  
  return(cat(paste0("## ", sorted_dates, collapse = "\n\n\n")))
  
}

generate_md_dates(start_from = "2023-12-15", end_with = "2023-12-27")

