import csv
import os
import argparse
from qscript import CaptureVideo_Magento, PATH_TO_VIDEO_FOLDER

def main():

    parser = argparse.ArgumentParser(description="CSV-driven Browser Automation Video Recorder")
    parser.add_argument("--csv", default="input.csv", help="Path to input CSV file")
    parser.add_argument("--server", default=None, help="Base URL of the video web service (e.g., http://127.0.0.1:8000)")
    parser.add_argument("--view-seconds", type=int, default=3, help="Seconds to keep preview browser open (>0 for seconds, 0 for Enter)")
    args = parser.parse_args()

    if args.server:
        import video_client

    os.makedirs(PATH_TO_VIDEO_FOLDER, exist_ok=True)
    csv_file = args.csv

    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        return

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        for row in reader:
            company_name = row.get("Company Name", "")
            print(f"Processing company: {company_name}...")

            video_path = CaptureVideo_Magento(
                url=row.get("URL", ""),
                company_name=company_name,
                language=row.get("Language", ""),
                country=row.get("Country", ""),
                postcode=row.get("Postcode", ""),
                city=row.get("City", ""),
                street=row.get("Street", ""),
                house_no=row.get("HouseNo", "")
            )

            if video_path and os.path.exists(video_path):
                print(f"Video successfully saved: {video_path}")

                if args.server:
                    try:
                        print(f"Uploading video for {company_name} to server {args.server}...")
                        video_url = video_client.UploadVideo(args.server, video_path, company_name)
                        print(f"Uploaded successfully! Video URL: {video_url}")

                        print(f"Opening preview in Chromium...")
                        from playwright.sync_api import sync_playwright
                        import time
                        with sync_playwright() as p:
                            browser = p.chromium.launch(headless=False)
                            context = browser.new_context(viewport={"width": 1280, "height": 720})
                            page = context.new_page()
                            page.goto(video_url)
                            page.wait_for_load_state("load")

                            if args.view_seconds > 0:
                                time.sleep(args.view_seconds)
                            else:
                                input("Preview open. Press Enter to close and continue...")
                            browser.close()
                    except Exception as e:
                        print(f"Error during upload or preview for {company_name}: {e}")

            else:
                print(f"Failed to record video for {company_name}")

if __name__ == "__main__":
    main()