import concurrent.futures
from openpyxl import Workbook
from apps.namaz_timing.utils.muslim_pro_prayer import scrap_prayer_timing_page
from apps.namaz_timing.utils.constants import month_names
import os

class App:
    def __init__(self, city_name):
        
        # Create 'outputs' folder if it doesn't exist
        output_folder = "outputs"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.excel_path = os.path.join(output_folder, f"{city_name}.xlsx")
        
        self.month_data = {}
        self.city_name = city_name
        
    def _write_to_excel(self):
        wb = Workbook()
        sheet = wb.active
        sheet.title = self.city_name
        
        current_row = 1  # Start from first row
        
        # Get the first month's data to extract headers
        if not self.month_data:
            return
            
        first_month_data = next(iter(self.month_data.values()))
        headers = list(first_month_data[0].keys())
        
        # Write column headers
        for col, header in enumerate(headers, 1):
            sheet.cell(row=current_row, column=col, value=header)
        
        # Write all months' data
        current_row = 2  # Start data from second row
        for month_index, data in sorted(self.month_data.items()):
            for entry in data:
                for col, key in enumerate(headers, 1):
                    sheet.cell(row=current_row, 
                             column=col, 
                             value=entry[key])
                current_row += 1

        wb.save(self.excel_path)
    
    def get_namaz_timings(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for month_index, tabledata in scrap_prayer_timing_page(self.city_name):
                month_name = month_names[month_index]
                
                self.month_data[month_index] = tabledata
                print(f"Page {month_name} processed!")
                print("------------------------------------------------------")
            
            print("Writing all data to Excel...")
            self._write_to_excel()
            print(f"Excel file saved at: {self.excel_path}")

