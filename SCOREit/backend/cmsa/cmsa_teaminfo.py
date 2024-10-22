import requests
from bs4 import BeautifulSoup
import re
import csv

# URL of the standings page
url = 'https://www.cmsasoccer.com/Season/2024CMSAFallLeagueSaturdayBoys/League/U102015Boys7v7/Calendar'  # Replace with the actual URL

# Send an HTTP request to get the page content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    page_content = response.text
else:
    print(f"Failed to retrieve the page: {response.status_code}")
    exit()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(page_content, 'html.parser')

# Find all headers and their respective tables
headers = soup.find_all('h2')
tables = soup.find_all('table', {'class': 'standingsTable'})

# Loop through each header-table pair
for header, table in zip(headers, tables):
    division_name = header.get_text(strip=True)
    print(f"\nDivision: {division_name}")
    
    # Extract rows from the current table's tbody
    rows = table.find('tbody').find_all('tr')
    
    # Iterate through the rows to extract team names and coach last names
    for row in rows:
        team_name_cell = row.find('td', {'class': 'teamName'})
        if team_name_cell:
            # Extract the text content of the teamName cell
            team_text = team_name_cell.get_text(strip=True)
            
            # Use regex to separate the team name from the coach's last name (inside parentheses)
            match = re.search(r'(.+?)\s*\((.+?)\)', team_text)
            if match:
                team_name = match.group(1)
                coach_last_name = match.group(2)
                print(f"Team: {team_name}, Coach: {coach_last_name}")
            else:
                print(f"Team: {team_text} (No coach last name found)")


# Open a CSV file to write the data
with open('team_info.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    #Coach email will need to be manual input unless access to league data base
    csvwriter.writerow(['Division', 'Team Name', 'Coach Last Name', 'Coach email'])

    # Loop through headers and tables as before
    for header, table in zip(headers, tables):
        division_name = header.get_text(strip=True)
        rows = table.find('tbody').find_all('tr')
        
        # Extract team and coach names and write them to the CSV
        for row in rows:
            team_name_cell = row.find('td', {'class': 'teamName'})
            if team_name_cell:
                team_text = team_name_cell.get_text(strip=True)
                match = re.search(r'(.+?)\s*\((.+?)\)', team_text)
                if match:
                    team_name = match.group(1)
                    coach_last_name = match.group(2)
                    csvwriter.writerow([division_name, team_name, coach_last_name])
                else:
                    csvwriter.writerow([division_name, team_text, 'No coach last name found'])

