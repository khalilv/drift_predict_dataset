import datetime
import numpy as np
import pandas as pd
import os
import re
import netCDF4 as nc

#function to extract latitude, longitude, and timestamps for each darpa drifter
#filename: csv darpa drifter filename
#returns an array of objects containing {latitude, longitude, timestamps, name} for each drifter   
def process_darpa_drifter_data(filename):
    drifters = []
    df = pd.read_csv(filename)
    spotterIds = df['spotterId'].values
    longitudes = df['longitude'].values
    latitudes = df['latitude'].values
    timestamps = [datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.000Z') for timestamp in df['timestamp'].values]
    change_indices = np.where(spotterIds[:-1] != spotterIds[1:])[0] + 1
    for index,value in enumerate(change_indices):
        prev = 0 if index == 0 else change_indices[index-1]
        drifter = {'lons': longitudes[prev:value], 'lats': latitudes[prev:value], 'timestamps': timestamps[prev:value], 'name': spotterIds[prev]}
        drifters.append(drifter)
    last_val = change_indices[-1]
    last_drifter = {'lons': longitudes[last_val:], 'lats': latitudes[last_val:], 'timestamps': timestamps[last_val:], 'name': spotterIds[last_val]}
    drifters.append(last_drifter)
    return drifters

#function to slice drifter data to just include trajectories in the input time range
#start: start datetime
#end: end datetime
#returns an array of objects containing {latitude, longitude, timestamps, name} for each drifter
def slice_darpa_drifter_data(start,end,data):
    sliced_drifters = []
    for drifter in data: 
        start_index = -1
        end_index = -1
        for i,time in enumerate(drifter['timestamps']):
            if time > start and start_index == -1: 
                start_index = i
            if time < end: 
                end_index = i
        if start_index != -1 and end_index != -1 and start_index <= end_index: 
            sliced_drifters.append({'lons': drifter['lons'][start_index:end_index+1], 'lats': drifter['lats'][start_index:end_index+1], 'timestamps': drifter['timestamps'][start_index:end_index+1], 'name': drifter['name']})
    return sliced_drifters

#concatenate single time wind data files into a single netCDF file
#need to have CDO installed for this to work
def concatenate_wind_files(filenames, outfile):
    files = ""
    for file in filenames:
        files = files + "p_" + file + " "
        date = re.search(r'\d{4}_\d{2}_\d{2}', file).group(0).replace("_","-")
        time = re.search(r'__\d{2}', file).group(0).replace("__","")
        os.system('cdo -r -f nc -settaxis,{date},{time}:00:00,6hours {file} p_{file}'.format(date=date,time=time,file=file))
    os.system('cdo mergetime {files}{outfile}'.format(files=files, outfile=outfile))
    projected_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for pfile in projected_files: 
        if pfile.startswith("p_"):
            os.remove(pfile)
    return

#check if a concatenated wind file already exists in the input time range 
def concatenated_wind_file_exists(start,end):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files: 
        dates = re.findall(r'\d{4}_\d{2}_\d{2}',f)
        if dates and len(dates) == 2:
            file_start = datetime.datetime.strptime(dates[0], "%Y_%m_%d")
            file_end = datetime.datetime.strptime(dates[1], "%Y_%m_%d")
            if file_start <= start and end <= file_end: 
                return f
    return None

#check to make sure requested dates are in the range of the dataset 
def check_valid_dates(start,end):
    start_min = datetime.datetime(2021,11,2)
    end_max = datetime.datetime(2021,12,3)
    if(start < start_min or end > end_max or start > end):
        return False
    return True

#for viewing and verifying netCDF files 
def read_nc_file(filename):
    ds = nc.Dataset(filename)
    print(ds)


def start_of_day(datetime):
    if datetime.hour == 0 and datetime.minute == 0 and datetime.second == 0: 
        return True
    else:
        return False
        
