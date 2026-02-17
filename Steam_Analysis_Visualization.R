# ==============================================================================
# STEAM DATA ANALYSIS & VISUALIZATION SCRIPT
# Author: [Your Name]
# Purpose: Generate charts for "The Real Gaming Habits of Adult Content Consumers"
# ==============================================================================

# 1. SETUP & LIBRARIES
# ------------------------------------------------------------------------------
if(!require(ggplot2)) install.packages("ggplot2")
if(!require(dplyr)) install.packages("dplyr")
if(!require(tidyr)) install.packages("tidyr")
if(!require(scales)) install.packages("scales")

library(ggplot2)
library(dplyr)
library(tidyr)
library(scales)

# Set a clean theme for all charts
theme_set(theme_minimal(base_size = 14))

# 2. LOAD DATA
# ------------------------------------------------------------------------------
# Ensure these CSV files are in your working directory
df_adult <- read.csv("steam_adult_group.csv", stringsAsFactors = FALSE)
df_control <- read.csv("steam_control_group.csv", stringsAsFactors = FALSE)

# Add Group Labels
df_adult$Group <- "Adult Gamers"
df_control$Group <- "Mainstream Gamers"

# Combine into one dataset
df_combined <- bind_rows(df_adult, df_control)

# 3. DATA CLEANING & FIXES
# ------------------------------------------------------------------------------
# FIX: Reclassify 'Destiny 2' as MMORPG (as per analysis findings)
df_combined <- df_combined %>%
  mutate(genre = ifelse(top_game == "Destiny 2", "MMORPG", genre))

# OPTIONAL: Filter out extreme outliers for better visualization 
# (e.g., removing playtimes > 10,000 hours if they distort the chart too much)
# df_combined <- df_combined %>% filter(hours_played < 10000)

# 4. CHART 1: PLAYTIME COMPARISON (BOX PLOT)
# ------------------------------------------------------------------------------
# This chart highlights the "High-Retention" behavior of adult gamers.

median_playtime <- df_combined %>%
  group_by(Group) %>%
  summarise(median = median(hours_played, na.rm = TRUE))

p1 <- ggplot(df_combined, aes(x = Group, y = hours_played, fill = Group)) +
  geom_boxplot(alpha = 0.7, outlier.shape = 21, outlier.alpha = 0.5) +
  scale_y_continuous(labels = comma, limits = c(0, 5000)) + # Limited to 5k for readability
  labs(
    title = "Lifetime Hours in Top-Played Game",
    subtitle = "Adult gamers show significantly higher median engagement",
    x = "",
    y = "Hours Played"
  ) +
  scale_fill_manual(values = c("Adult Gamers" = "#FF6F61", "Mainstream Gamers" = "#6B5B95")) +
  theme(legend.position = "none") +
  annotate("text", x = 1, y = 4500, label = paste("Median:", median_playtime$median[1], "hrs"), fontface = "bold") +
  annotate("text", x = 2, y = 4500, label = paste("Median:", median_playtime$median[2], "hrs"), fontface = "bold")

print(p1)
ggsave("chart_playtime_boxplot.png", p1, width = 8, height = 6)


# 5. CHART 2: GENRE PREFERENCE COMPARISON (BAR CHART)
# ------------------------------------------------------------------------------
# This chart shows the shift from Shooters to MMORPGs/Utility.

# Calculate Percentages
genre_summary <- df_combined %>%
  group_by(Group, genre) %>%
  summarise(Count = n(), .groups = 'drop') %>%
  group_by(Group) %>%
  mutate(Percentage = Count / sum(Count) * 100)

# Filter for the most relevant genres to declutter the chart
# We keep the top 6 genres + Utility
top_genres <- c("Shooter", "MMORPG", "Action / Adventure", "RPG", "Utility / Software", "Strategy & MOBA", "Hardcore Action")
genre_filtered <- genre_summary %>%
  filter(genre %in% top_genres)

p2 <- ggplot(genre_filtered, aes(x = reorder(genre, -Percentage), y = Percentage, fill = Group)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.7) +
  labs(
    title = "Genre Preferences: Adult vs. Mainstream Gamers",
    x = "",
    y = "Percentage of Users (%)"
  ) +
  scale_fill_manual(values = c("Adult Gamers" = "#FF6F61", "Mainstream Gamers" = "#6B5B95")) +
  scale_y_continuous(expand = expansion(mult = c(0, .1))) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.position = "top"
  ) +
  geom_text(aes(label = round(Percentage, 1)), 
            position = position_dodge(width = 0.8), 
            vjust = -0.5, size = 3.5)

print(p2)
ggsave("chart_genre_distribution.png", p2, width = 10, height = 6)

# 6. OUTPUT SUMMARY STATS (Check Console)
# ------------------------------------------------------------------------------
cat("\n--- SUMMARY STATISTICS ---\n")
print(median_playtime)
cat("\n--- GENRE BREAKDOWN ---\n")
print(genre_summary %>% filter(genre %in% c("Shooter", "MMORPG", "Utility / Software")))
