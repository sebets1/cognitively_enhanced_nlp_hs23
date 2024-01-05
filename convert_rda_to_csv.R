# ---------for smaller data (around 10000 rows)---------

# Load the RDA file
load("C:/Users/serai/Documents/00_UZH/osfstorage-archive/release 1.0/version 1.1/primary data/eye tracking data/joint_data_l2_trimmed.rda")

# List the objects in the R environment
print(ls())

# Identify the name of the data object 
rda_data <- joint.data

# Convert and save to CSV
write.csv(rda_data, file = "C:/Users/serai/Documents/00_UZH/osfstorage-archive/release 1.0/version 1.1/meco_data_short.csv", row.names = FALSE)



# ---------for larger data ---------

# Load the data
load("C:/Users/serai/Documents/00_UZH/osfstorage-archive/release 1.0/version 1.1/primary data/eye tracking data/joint_data_l2_trimmed.rda")

# Identify the name of the data object (replace "your_data" with the appropriate name)
rda_data <- joint.data

# Install and load the data.table package
# install.packages("data.table")
library(data.table)

# Convert the data to data.table
rda_data <- as.data.table(rda_data)

# Save to CSV 
fwrite(rda_data, "C:/Users/serai/Documents/00_UZH/osfstorage-archive/release 1.0/version 1.1/meco_data.csv", row.names = FALSE)
