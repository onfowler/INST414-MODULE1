# The Gaming Habits of Adult Content Consumers

> **Do consumers of adult video games play differently than the average Steam user?** > An exploratory data analysis comparing the gaming habits, playtime engagement, and genre preferences of adult content consumers versus mainstream gamers.

## 📌 Project Overview
This project investigates the behavioral distinctiveness of the "Adult Gamer" demographic. Often stereotyped as socially isolated or casual consumers, this analysis seeks to determine if this group exhibits a unique "behavioral signature" in their software usage.

By scraping public Steam profiles (n=400), I compared a study cohort of adult game reviewers against a control group of mainstream gamers. The findings challenge common assumptions, revealing that this demographic functions as **High-Retention Power Users** with a distinct preference for deep, persistent systems over transient action games.

---

## 📊 Key Findings

### 1. The "No Life" Metric (High Engagement)
* **Control Group Median Playtime:** 446 Hours
* **Adult Group Median Playtime:** **768 Hours**
* **Insight:** The adult gamer spends **~72% more time** in their favorite game than the average user. They demonstrate extreme dedication to single ecosystems.

### 2. The Shift from Shooters to Worlds
* **Shooter Preference:** Control Group (35.5%) vs. Adult Group (23.0%)
* **MMORPG Preference:** Control Group (3.0%) vs. Adult Group (**9.5%**)
* **Insight:** While the mainstream gamer prefers competitive, lobby-based shooters (*CS2*, *Apex*), the adult gamer pivots toward immersive, persistent worlds (*Final Fantasy XIV*, *Destiny 2*).

### 3. The "Digital Architect" Persona
* **Utility Software Usage:** Adult gamers were **2x more likely** to have desktop customization tools (e.g., *Wallpaper Engine*) as their most-played application.
* **Insight:** This suggests a user persona that values agency and customization of their digital environment.

---

## 🛠️ Methodology

### Data Collection
* **Source:** Steam Store API & Steamworks Web API.
* **Sample Size:** 400 Users (200 Study Group, 200 Control Group).
* **Selection Criteria:**
    * *Study Group:* Users who reviewed high-engagement adult titles (e.g., *Subverse*, *Summer Clover*).
    * *Control Group:* Users who reviewed mainstream "Titan" titles (e.g., *Counter-Strike 2*, *Stardew Valley*).

### Data Processing
* **Metric 1 (`top_game`):** The single game with the highest lifetime hours.
* **Metric 2 (`genre`):** Mapped using a custom **Priority-Based Tagging Algorithm**.
    * *Logic:* Specific tags (`MMORPG`, `Utility`) override generic tags (`Action`, `Adventure`).
    * *Edge Case Fix:* *Destiny 2* was manually reclassified from "Action" to "MMORPG" to reflect its "lifestyle game" status.

---

## 📂 Repository Structure

```text
├── data/
│   ├── steam_adult_group.csv       # Raw data for the study cohort
│   ├── steam_control_group.csv     # Raw data for the control group
├── scripts/
│   ├── steam_adult_scraper.py      # Python script for scraping Study Group
│   ├── steam_control_scraper.py    # Python script for scraping Control Group
│   └── steam_analysis_visualization.R    # R script for generating charts
├── visuals/
│   ├── chart_playtime_boxplot.png  # Playtime comparison chart
│   └── chart_genre_dist.png        # Genre distribution chart
└── README.md
