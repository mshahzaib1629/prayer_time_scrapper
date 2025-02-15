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
        
        for month_index, data in sorted(self.month_data.items()):
            month_name = month_names[month_index]
            if month_name == "January":
                sheet = wb.active
                sheet.title = month_name
            else:
                sheet = wb.create_sheet(month_name)
            
            # Write month name as header
            sheet['A1'] = month_name
            
            # Write column headers
            headers = list(data[0].keys())
            for col, header in enumerate(headers, 1):
                sheet.cell(row=3, column=col, value=header)
            
            # Write data rows
            for row, entry in enumerate(data, 4):
                for col, key in enumerate(headers, 1):
                    sheet.cell(row=row, column=col, value=entry[key])
        
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

