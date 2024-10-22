from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import re

# Set Chrome options to disable SSL errors
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')

# Automatically manage ChromeDriver and create a new service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL of the standings page
url = 'https://www.cmsasoccer.com/Season/2024CMSAFallLeagueSaturdayBoys/League/U102015Boys7v7/Calendar'
driver.get(url)

# Explicitly wait for the page to load and for the calendar items to appear
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'seasonCalendarItem')))

# Open a CSV file to write the data
with open('cmsa_schedule.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Add headers for team and game info
    csvwriter.writerow(['Date', 'Team 1', 'Team 2', 'Team 1 Score', 'Team 2 Score', 'Game Time', 'Location', 'Game Status', 'Winner', 'Loser', 'Tie'])

    # Initialize current_date variable
    current_date = ""

    # Find all elements that contain either the date header or game items
    items = driver.find_elements(By.XPATH, "//div[@class='sac-eventlistheaderdate' or contains(@class, 'seasonCalendarItem')]")

    # Loop through each item
    for item in items:
        # Check if the current item is a date header
        if 'sac-eventlistheaderdate' in item.get_attribute("class"):
            current_date = item.text.strip()  # Update the current date
            print(f"Date detected: {current_date}")  # Log the date detected
        else:  # Process game items
            try:
                # Get game time
                game_time_elements = item.find_elements(By.CLASS_NAME, 'calendarEventStartTime')
                game_time = game_time_elements[0].text.strip() if game_time_elements else "Unknown"

                # Get game location
                location_element = item.find_element(By.CLASS_NAME, 'calendarEventLocation')
                location = location_element.text.replace('Location:', '').strip()

                # Get game status
                status_element = item.find_element(By.CLASS_NAME, 'calendarEventGameStatus')
                status = status_element.text.strip() if status_element else "Unknown"

                # Debug: Print the detected game status
                print(f"Game status detected: '{status}'")  # Log detected game status

                # Process completed games
                if "COMPLETED" in status or "TIME CHANGE" in status:
                    print(f"Completed game detected: {status}")  # Log detection
                    
                    # Extract teams and scores from the event game element
                    event_game_element = item.find_element(By.CLASS_NAME, 'eventGame')
                    event_game_text = event_game_element.text.strip()

                    # Extract team names and scores
                    match = re.search(r'(.+?)\s-\s(\d+)\svs\s(.+?)\s-\s(\d+)', event_game_text)
                    if match:
                        team1 = match.group(1).strip()
                        team1_score = match.group(2).strip()
                        team2 = match.group(3).strip()
                        team2_score = match.group(4).strip()

                        # Determine winner and loser
                        if team1_score > team2_score:
                            winner = team1
                            loser = team2
                            tie = ""
                        elif team1_score < team2_score:
                            winner = team2
                            loser = team1
                            tie = ""
                        else:
                            winner = "Tied"
                            loser = "Tied"
                            tie = "Tied"

                        # Write to CSV
                        csvwriter.writerow([current_date, team1, team2, team1_score, team2_score, game_time, location, status, winner, loser, tie])
                        print(f"Written to CSV: {current_date}, {team1}, {team2}, {team1_score}-{team2_score}, {game_time}, {location}, {status}, {winner}, {loser}, {tie}")

                # Check for "Not Yet Played" games
                elif "NOT YET PLAYED" in status.upper():
                    print("Not Yet Played game detected.")  # Log detection
                    
                    # Get opponent teams from the eventGame class
                    opponent_element = item.find_element(By.CLASS_NAME, 'eventGame')
                    opponent_text = opponent_element.text.strip()

                    # Extract both teams using regex
                    match = re.search(r'(.+?) vs (.+)', opponent_text)
                    if match:
                        team1 = match.group(1).strip()
                        team2 = match.group(2).strip()

                        # Print the teams to the terminal
                        print(f"Teams: {team1} vs {team2}")

                        # Write the data to CSV
                        csvwriter.writerow([current_date, team1, team2, "N/A", "N/A", game_time, location, status, "N/A", "N/A", "N/A"])
                        print(f"Written to CSV: {current_date}, {team1}, {team2}, N/A, N/A, {game_time}, {location}, {status}, N/A, N/A, N/A")  # Log successful write

            except Exception as e:
                print(f"Error occurred: {e}")

# Close the browser after scraping
driver.quit()

print("Schedule has been written to CSV.")
