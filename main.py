import os.path

import numpy as np
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def main():
    mons = []
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # The ID and range the sheet.
        SHEET_ID = "11l1PgIoVsQoaAPCs1DL6ajYNnmRP0_EBM1dRXQoWWiM"
        ranges = ["A", 'B', 'C', 'D', 'F', 'G', 'H', 'I']

        # Call the Sheets API
        sheet = service.spreadsheets()
        for col in ranges:
            range_ = f"Names!{col}:{col}"

            result = sheet.values().get(spreadsheetId=SHEET_ID,
                                        range=range_).execute()
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

        search_mon = input("Search for Pokemon: ").title()
        total_mons = len(mons)
        layout = np.arange(30).reshape(5, 6)

        for mon in mons:
            if search_mon in mon:
                index = mons.index(mon)
                box = index // 30 + 1
                remainder = index % 30

                location = np.where(layout == remainder)
                x, y = location[1][0], location[0][0]

                print(f"{mon} is in box {box}, row {y+1} and column {x+1}")
                print(f"     BOX {box}")
                visual = np.zeros((5, 6), int)
                visual[y, x] = 1
                print(visual.view())
                print("\n")

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
