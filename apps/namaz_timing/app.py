import concurrent.futures
from apps.namaz_timing.utils.muslim_pro_prayer import scrap_prayer_timing_page
from apps.namaz_timing.utils.constants import month_names
class App:
    
    def get_namaz_timings(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for month_index, tabledata in scrap_prayer_timing_page():
                
                print(f"Page {month_names[month_index]} processed!")
                print(tabledata)
                print("------------------------------------------------------")
            
    