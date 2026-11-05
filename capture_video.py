import csv
import os
from qscript import CaptureVideo_Magento, PATH_TO_VIDEO_FOLDER

def main():
    
    os.makedirs(PATH_TO_VIDEO_FOLDER, exist_ok=True)
    
    csv_file = "input.csv"
    
    
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        
        for row in reader:
            print(f"Processing company: {row['Company Name']}...")
            
           
            video_path = CaptureVideo_Magento(
                url=row["URL"],
                company_name=row["Company Name"],
                language=row["Language"],
                country=row["Country"],
                postcode=row["Postcode"],
                city=row["City"],
                street=row["Street"],
                house_no=row["HouseNo"]
            )
            
            if video_path:
                print(f"Video successfully saved: {video_path}")
            else:
                print(f"Failed to record video for {row['Company Name']}")

if __name__ == "__main__":
    main()