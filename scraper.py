import os
import pandas as pd
from icrawler.builtin import BingImageCrawler

def start_scraping():
    # 1. CSV file path
    csv_file = 'indian_food.csv' 
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} file nahi mili! Please check file name.")
        return

    try:
        df = pd.read_csv(csv_file)
        # Column 'name' se list nikalna
        dish_list = df['name'].tolist() 
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    base_dir = 'dataset_images'

    for dish in dish_list:
        # ✅ FIX 1: Agar dish ka naam empty (NaN) hai ya string nahi hai, toh skip karein
        if pd.isna(dish) or not isinstance(dish, (str, bytes)):
            print(f"Skipping invalid dish entry: {dish}")
            continue

        # ✅ FIX 2: Dish name ko saaf karein aur string mein convert karein
        dish_str = str(dish).strip()
        print(f"\n--- Downloading: {dish_str} ---")
        
        folder_name = dish_str.replace(" ", "_").lower()
        save_path = os.path.join(base_dir, folder_name)
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # Bing Crawler config
        bing_crawler = BingImageCrawler(
            storage={'root_dir': save_path},
            log_level=50 # Sirf errors dikhane ke liye taaki terminal saaf rahe
        )
        
        # Search query
        search_query = f"{dish_str} indian food dish"
        
        # 30 images download karein
        try:
            bing_crawler.crawl(keyword=search_query, max_num=30)
        except Exception as e:
            print(f"Could not download {dish_str}: {e}")

if __name__ == "__main__":
    start_scraping()