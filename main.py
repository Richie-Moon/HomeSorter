import os.path

import numpy as np
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("sheets", "v4", credentials=creds)

# The ID and range the sheet.
SHEET_ID = "11l1PgIoVsQoaAPCs1DL6ajYNnmRP0_EBM1dRXQoWWiM"
ranges = ["A", 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']  # Each generation
# Call the Sheets API
SHEET = service.spreadsheets()


def find_box():
    mons = []

    for col in ranges:
        range_ = f"Names!{col}:{col}"
        result = SHEET.values().get(spreadsheetId=SHEET_ID, range=range_).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        values.pop(0)
        this_gen_mons = []
        for mon in values:
            this_gen_mons.append(mon[0])

        repeated = []
        for mon in this_gen_mons:
            repeated.extend([mon, "Shiny " + mon])

        count = len(repeated)
        while count % 30 != 0:
            repeated.append("BLANK")
            count = len(repeated)
        mons.extend(repeated)

    while True:
        search_mon = input("Search for Pokemon: ").title()
        if search_mon == "0" or search_mon == "Quit" or search_mon == "":
            return

        layout = np.arange(30).reshape(5, 6)
        for mon in mons:
            if search_mon in mon:
                index = mons.index(mon)
                box = index // 30 + 1
                remainder = index % 30

                location = np.where(layout == remainder)
                x, y = location[1][0], location[0][0]

                print(f"{mon} is in box {box}, row {y + 1} and column {x + 1}")
                print(f"     BOX {box}")
                visual = np.zeros((5, 6), int)
                visual[y, x] = 1
                print(visual.view())
                print()


def stats():
    total, locked, not_caught, caught = 0, 0, 0, 0
    for i in range(1, 11):
        if i == 10:
            sheet = "Other"
        else:
            sheet = f"Gen {i}"

        num_mons = len(SHEET.values().get(spreadsheetId=SHEET_ID, range=f"{sheet}!A2:A").execute().get("values", []))

        result = SHEET.values().get(spreadsheetId=SHEET_ID, range=f"{sheet}!C2:C{2+num_mons}").execute()
        values = result.get("values", [])

        total += num_mons
        for date in values:
            if not date:
                not_caught += 1
            elif date[0] == "LOCKED":
                locked += 1
            else:
                caught += 1

    print(f"\nTotal: {total}")
    print(f"Total excluding shiny-locked: {total-locked}")
    print(f"Total caught: {caught}")
    print(f"Total not caught: {not_caught}")
    print(f"Percent caught: {round(caught/(total-locked)*100, 2)}%\n")


def update():

    pass

def calculate_within_encounters():
    try:
        num_encounters = int(input("\nEnter number of encounters: "))
        rate = 1/int(input("Enter rate: "))

        if num_encounters <= 0 or rate <= 0:
            raise ValueError

        total: float = 0.0
        for i in range(1, num_encounters+1):

            total += rate * (1-rate)**(i-1)

        print(f"There is a {round(total*100, 2)}% chance of encountering the shiny after {num_encounters} encounters. \n")

    except ValueError:
        print("Please enter a valid number.\n")


def main():
    try:
        while True:
            print("1. Find Box")
            print("2. Get stats")
            print("3. Update data")
            print("4: Calculate chance within encounters")
            print("5. Exit")
            try:
                choice = int(input("Choice: "))
            except ValueError:
                choice = None

            match choice:
                case 1:
                    find_box()
                case 2:
                    stats()
                case 3:
                    update()
                case 4:
                    calculate_within_encounters()
                case 5:
                    quit()
                case _:
                    print("Invalid choice\n")
    except HttpError as e:
        print(f"HTTPError: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
