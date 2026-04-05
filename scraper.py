import os
import pandas as pd
from icrawler.builtin import BingImageCrawler # Google ki jagah Bing use kar rahe hain

def start_scraping():
    # 1. Apni CSV file ka naam yahan check karein
    csv_file = 'indian_food.csv' 
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} file nahi mili! Please check file name.")
        return

    try:
        df = pd.read_csv(csv_file)
        # Column name check karein: 'name' hai ya 'dish_name'? 
        # Agar error aaye toh niche 'name' ko change kar dein.
        dish_list = df['name'].tolist() 
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    base_dir = 'dataset_images'

    for dish in dish_list:
        print(f"\n--- Downloading: {dish} ---")
        
        folder_name = dish.replace(" ", "_").lower()
        save_path = os.path.join(base_dir, folder_name)
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # Bing Crawler zyada reliable hai
        bing_crawler = BingImageCrawler(storage={'root_dir': save_path})
        
        # Search query
        search_query = f"{dish} indian food dish"
        
        # 30 images per dish
        bing_crawler.crawl(keyword=search_query, max_num=30)

if __name__ == "__main__":
    start_scraping()