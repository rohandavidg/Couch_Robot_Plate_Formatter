#!/cygdrive/c/Users/m149947/AppData/Local/Continuum/Anaconda2-32/python

"""
formats the database sheet
to a robot form
"""


import sys
sys.setrecursionlimit(1500)
import xlrd
import xlwt
import logging
import re
import datetime
import csv
import itertools
from collections import defaultdict
import collections
import pandas as pd
import pprint
import os
import openpyxl
import re


version = "v1.0"

#Database_ID_(database_id)
#CARRIERS_ID_(carriers_id)
#DNA_Failed_QC_(caqc_fail)
#Sequencing_Protocol_(sub_seq_protocol)
#DNA Buffer_(cast_buffer)
#Plate_Barcode_(cast_plate_barcode)
#Plate_Location_in_Couch Lab_(cast_plate_lab_location)
#Plate_Coordinate_(sub_plate_coordinate)
#Plate_Volume_(uL)(sub_plate_vol)
#Plate_Concentration_(ng/uL)_(sub_plate_conc)
#Quibit Result_(ng/uL)_(caqc_qubit)
#Was_stock_sample_modified_(caqc_mod)
#Date_Working_Plate_Created_(cawk_plate_date)
#Working_Plate_Barcode_(cawk_plate_barcode)
#Working_Plate_Coordinate_(cawk_plate_coordinate)
#Working_Plate_Volume_Water_Added_(uL)_(cawk_plate_vol_water)
#Working_Plate_Volume_Sample_Added_(uL)_(cawk_plate_vol_stock)
#Working_Plate_Total_Volume_(uL)_(cawk_plate_vol)
#Working_Plate_Final_Concentration_(ng/uL)_(cawk_plate_conc)
#Working_Plate_Location_in_Couch_Lab_(cawk_plate_lab_location)
#Working_Plate_Complete_(cawk_complete)Send_sample_to_UPenn_(caup_upenn)


def main():
    database_manifest_csv = sys.argv[1]
    run(database_manifest_csv)


def run(databse_manifest_csv):
    database_working_plate_dict = parse_database_manifest(databse_manifest_csv)
    sorted_database_working_plate_dict = collections.OrderedDict(sorted(database_working_plate_dict.items()))
    generate_robot_csv = write_output(sorted_database_working_plate_dict)
    
    
class record(object):
    """
    using built in dictionary and grabbing
    each row
    """
    def __init__(self, mapping):
        self.__dict__.update(mapping)


    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)


def configure_logger(logger_filename):
    """
    setting up logging
    """
    logger = logging.getLogger('Couchlab_database_to_robot')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(time.strftime("database_to_robot-%Y%m%d.log"))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s'\t'%(name)s'\t'%(levelname)s'\t'%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger



class parse_csv(object):

    def __init__(self, csv_file):
        self.csv_file = open(csv_file,'rb')
        self.writer = csv.writer(self.csv_file, delimiter=',')
        
        
    def __iter__(self):
        return self

    
    
    def close(self):
        self.csv_file.close()


#    def show_headers(self):
#        self.header = self.csv_file.next()
#        self.new_header = self.header.replace(" ", "_")
#        return self
#        self.csv_file.close()
        
        
    def create_dict(self):
#        new_header = self.header.replace(" ", "_")
        reader = csv.DictReader(self.csv_file, delimiter=',')
        return reader



def parse_database_manifest(database_manifest_csv):
    database_manifest_dict = {}
    f = parse_csv(database_manifest_csv)
    csv_dict = f.create_dict()

    for row in csv_dict:
        r = {k.replace(" ","_"): v for k, v in row.iteritems()}
        cawk_plate_coordinate = r['Working_Plate_Coordinate_(cawk_plate_coordinate)']
        sub_plate_coordinate = r['Plate_Coordinate_(sub_plate_coordinate)']
        edit_cawk_plate_coordinate = "".join([i[0] + i[2]  if len(i) == 3 and i[1] == '0' else i for i in cawk_plate_coordinate.split()])
        edit_sub_plate_coordinate = "".join([i[0] + i[2]  if len(i) == 3 and i[1] == '0' else i for i in sub_plate_coordinate.split()])
        database_manifest_dict[r['CARRIERS_ID_(carriers_id)']] = [r['Working_Plate_Barcode_(cawk_plate_barcode)'] , edit_sub_plate_coordinate, edit_cawk_plate_coordinate,
                                                                   r['Working_Plate_Volume_Sample_Added_(uL)_(cawk_plate_vol_stock)'],
                                                                   r['Working_Plate_Volume_Water_Added_(uL)_(cawk_plate_vol_water)']]

    return database_manifest_dict
    f.close()


def plate_barcode_dict(database_manifest_dict):
    plate_well_dict = defaultdict(list)
    for key, value in database_manifest_dict.items():
        plate_well_dict[value[0]].append(['',value[1], value[3],'',value[2],value[4]])
    return plate_well_dict




def write_output(database_manifest_dict):
    plate_robot_well_dict = plate_barcode_dict(database_manifest_dict)
    for key, value in plate_robot_well_dict.items():
        with open(key + "_output.csv", 'wb') as csvfile:
            robot_writer =  csv.writer(csvfile, delimiter=',')
            robot_writer.writerow(['Name of Source', 'Well', 'Volume', 'Name of Dest Plate', 'Well', 'Volume'])
            for i in value:
                robot_writer.writerow(i)
            
            
if __name__ == "__main__":
    main()
