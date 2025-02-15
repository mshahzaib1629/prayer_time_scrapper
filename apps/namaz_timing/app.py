import concurrent.futures
from apps.namaz_timing.utils.muslim_pro_prayer import scrap_prayer_timing_page

class App:
    
    def get_namaz_timings(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for epoch, page, data in scrap_prayer_timing_page():
                
                print(f"Page {page} processed!")
            
    