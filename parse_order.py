"""Fisher Orders parse script.

This script allows the user to enter a txt file converted from a order 
confirmation email as a commandline parameter. 

The txt file is parsed for specific data and that data is then written to a csv 
file which is placed in the user's home directory in a directory labelled 
'fisher_orders'.
"""

import argparse
import csv
import os.path
import unicodedata

from pathlib import Path


def create_parser():
    """Creates a parser object to accept input file parameter"""
    
    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument('file', help='.txt file used to generate .csv file.')
    
    # Returns the object with file as an attribute
    return parser.parse_args()

def parse_file(file):
    """Parse file for CSV file data and return data as a dictionary"""
    
    # Dictionary to hold CSV file data
    csv_data = {}
    
    # Arrays to hold repeated row data
    quantity = []
    unit_price = []
    line_total = []
    description = []
    
    with open(file, 'r') as reader:
        
        for line in reader:
            if line == '\n':
                continue
            # Date
            if line.startswith('Placed:'):
                csv_data['Order Date'] = get_date(line.split(': ')[1])
            # Order Number
            if line.startswith('Fisher Scientific Order'):
                csv_data['Order Number'] = line.split(': ')[1].strip('\n')
            # Name
            if line.startswith('Attention:'):
                full_name = get_name(line.split(': ')[1].split('/'))
                csv_data['First Name'] = full_name[0]
                csv_data['Last Name'] = full_name[1]
            # Account
            if line.startswith('Credit Card:'):
                csv_data['Card Account'] = line.split(': ')[2].strip('\n')
            # Quantity, Unit Price, Line Total
            if line.startswith('Cat No.'):
                data_array = extract_catalog_data(line)
                quantity.append(float(data_array[0]))
                unit_price.append(float(data_array[2]))
                line_total.append(float(data_array[4]))
            # Description
            if line.startswith('Description: '):
                description.append(line.split('Description: ')[1].strip('\n'))
            # Order Total
            if line.startswith('*Estimated Order'):
                order_total = float(next(reader).strip('$\n'))
                csv_data['Order Total'] = order_total
        
        # Add repeated row data to csv_data dictionary
        csv_data['Quantity Shipped'] = quantity
        csv_data['Unit Price'] = unit_price
        csv_data['Amount'] = line_total
        csv_data['Description'] = description                
        
        return csv_data

def extract_catalog_data(line):
    """Returns array of quantity, unit price, and line total data"""
    
    # Normalize line data
    line_data = line.split('Qty: ')[1].split(' ')
    data_array = list(map(normalize_data, line_data))
    
    # Pull out order data
    for index, element in enumerate(data_array):
        data_array[index] = element.split(' ')[0].strip('\n$')
        
    return data_array

def get_date(date_string):
    """Returns date: mm/dd/yyyy"""
    
    date_array = date_string.split(' ')
    
    month = get_month_num(date_array[1])
    
    return f"{month}/{date_array[2]}/{date_array[5]}"
    
def get_month_num(month_string):
    """Return month parameter as a number (string)"""
    
    months = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr':'4', 'May':'5', 'Jun':'6',
              'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10', 'Nov':'11', 
              'Dec':'12'}
    
    return months[month_string]

def get_name(name_string):
    """Return array of first initial [0] and last name [1]"""

    name = name_string[0].split(' ')

    # Test for length of name
    if len(name) > 1:
        full_name = [name[0], name[1]]
    else:
        # If order only has one name, return first name as a blank string
        # and last name as name
        full_name = [' ', name[0]]

    return full_name

def normalize_data(data):
    """Return normalized data"""
    
    return unicodedata.normalize('NFKD', data).strip(' ')

def write_csv(data_dictionary):
    """Writes dictionary to CSV file"""
    
    # CSV file path and name
    csv_file_path = get_csv_file_path()
    file_name = csv_file_path.joinpath(data_dictionary['Last Name'] + '.csv')
    
    # Column names
    fieldnames = ['First Name', 'Last Name', 'Description', 'Quantity Shipped', 
                'Unit Price', 'Amount', 'Order Total', 'Order Date', 
                'Card Account', 'Order Number']

    # Write dictionary data to csv file
    with open(file_name, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for index, element in enumerate(data_dictionary['Quantity Shipped']):
            writer.writerow({'First Name': data_dictionary['First Name'], 
                'Last Name': data_dictionary['Last Name'], 
                'Description': data_dictionary['Description'][index], 
                'Quantity Shipped': element, 
                'Unit Price': data_dictionary['Unit Price'][index],
                'Amount': data_dictionary['Amount'][index],
                'Order Total': data_dictionary['Order Total'], 
                'Order Date': data_dictionary['Order Date'], 
                'Card Account': data_dictionary['Card Account'], 
                'Order Number': data_dictionary['Order Number']})

def get_csv_file_path():
    """Returns file path for CSV file"""

    csv_file_path = Path.home().joinpath('Desktop', 'fisher_orders')
    csv_file_path.mkdir(exist_ok=True)
    return csv_file_path
    
if __name__ == "__main__":
    
    args = create_parser()
    data_dictionary = parse_file(args.file)
    write_csv(data_dictionary)