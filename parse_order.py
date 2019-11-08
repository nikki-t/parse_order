import argparse
import csv
import os.path

#Create parser object to with input file as command line argument
def create_parser():
    # Create an ArgumentParser object and then input file as an add arguments to the object.
    # parse_args() returns the object with file as an attribute
    parser = argparse.ArgumentParser(description='Input file handle')
    parser.add_argument('file')
    return parser.parse_args()

def open_file(filename):
    in_file = open(filename, 'r')
    return in_file

#Parse file for data needed to write a CSV file
def parse_file(in_file):

    #Rows to return to be written to CSV file
    rows = {}

    #Lists to keep track of data that occurs more than once in an order
    description = []
    quantity = []
    unit_price = []
    line_total = []

    for line in in_file:
        line = line.strip('\n')
        #Retrieve name of person who placed the order
        if line.startswith('Order Created By:'):
            full_name = (line.split(': '))[1]
            first_name = (full_name.split(' '))[0]
            last_name = (full_name.split(' '))[1]
        #Retrieve the date the order was placed
        if line.startswith('Placed: '):
            full_date = (line.split(': '))[1]
            date = create_date(full_date)
        #Retrieve last four of the credit card used to place the order
        if line.startswith('Credit Card:'):
            full_card = (line.split(': ', 1))[1]
            credit_card = (full_card.split(": "))[1]
        #Retrieve quantity, unit price, line total
        if line.startswith('Cat No.: '):
            #Quantity
            full_quantity = (line.split('Qty: '))[1]
            half_quantity = (full_quantity.split('U'))[0]
            quarter_quantity = (half_quantity.split('\xc2'))[0]
            quantity.append(quarter_quantity)
            #Unit price
            full_unit_price = (line.split('Price: $'))[1]
            half_unit_price = (full_unit_price.split('L'))[0]
            quarter_unit_price = (half_unit_price.split('\xc2'))[0]
            unit_price.append(quarter_unit_price)
            #Line total
            line_total.append((line.split('Line Total: $'))[1])
        #Retrieve item description
        if line.startswith('Description: '):
            description.append((line.split('Description: '))[1])
        #Retrieve order total
        if line.startswith('$'):
            order_total = (line.split('$'))[1]
    #Close file
    in_file.close()
    #Create CSV filename using last name and appending _fisher
    filename = last_name.lower() +'_fisher'
    #Create a dictionary of rows so that each row is a tuple containing order data
    for key in range(len(description)):
        rows[key] = (first_name, last_name, description[key], int(quantity[key]), float(unit_price[key]),
                     float(line_total[key]), float(order_total), date, int(credit_card))
    return rows, filename

#Creates a date string
def create_date(date):
    months={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
            7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    month = (date.split(" "))[1]
    for key, value in months.items():
        if month == value:
            month = key
    day = (date.split(" "))[2]
    year = (date.split(" "))[5]
    return str(month) + '/' + str(day) + '/' + str(year)

#Creates a list of column headers
def create_columns():
    return ['First Name', 'Last Name', 'Description', 'Quantity shipped', 'Unit price', 'Amount',
            'Order Total', 'Order Date', 'Card Account #']

#Write CSV file
def write_csv(filename, columns, rows):
        #Create a file to write to
        csv_file = get_file_path(filename);
        #Write to CSV file writing column names first and then row data
        with open(csv_file, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(columns)
            for key, values in rows.items():
                csv_writer.writerow(values)
        #Close CSV file; done writing to it
        csv_file.close()
        print("File written to: ", filename + ".csv")

#Creates path to save CSV file to
def get_file_path(filename):
    save_path = '/Users/ntadmin/Desktop/fisher_orders'
    return os.path.join(save_path, filename + ".csv")

def main():
    args = create_parser()
    contents = open_file(args.file)
    rows, out_file = parse_file(contents)
    columns = create_columns()
    write_csv(out_file, columns, rows)

main()
