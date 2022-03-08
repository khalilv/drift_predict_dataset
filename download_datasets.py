from urllib import request
import datetime
import os
from utils import concatenate_wind_files, concatenated_wind_file_exists

#automation to download hindcast global current data from https://ncss.hycom.org/thredds/ncss/grid/GLBy0.08/expt_93.0/uv3z/dataset.html
#start: start datetime
#end: end datetime
#returns filenames containing the requested data
#subsets data one day at a time
def download_hindcast_current_data(start, end):
    variables = ['water_u','water_v'] #current variables
    filedir = os.path.dirname(__file__) #change directory to opendrift/data/hindcast/current
    os.chdir(filedir)
    os.chdir("./data/hindcast/current")
    filenames = []
    while(start < end): #subset data one day at a time
        subset_start = start
        subset_end = start + datetime.timedelta(days=1)
        filename = "current_{start:s}__{end:s}.nc4".format(start=subset_start.strftime("%Y_%m_%d"), end=subset_end.strftime("%Y_%m_%d")) 
        filenames.append(filename)
        if os.path.isfile("./{filename:s}".format(filename = filename)): #check if file exists
            start = subset_end
            continue
        request_url = 'https://ncss.hycom.org/thredds/ncss/GLBy0.08/expt_93.0/uv3z?'
        for v in variables:
            query = 'var={v:s}&'.format(v=v)
            request_url = request_url + query
        subset_start_str = subset_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        subset_end_str = subset_end.strftime("%Y-%m-%dT%H:%M:%SZ")
        time = 'time_start={start:s}&time_end={stop:s}&'.format(start=subset_start_str, stop=subset_end_str)
        depth = 'vertCoord=0&'
        file_info = 'accept=netcdf4'
        request_url = request_url + time + depth + file_info
        print('Downloading current data file from {start:s} to {end:s}'.format(start=subset_start.strftime("%Y-%m-%d"), end=subset_end.strftime("%Y-%m-%d")))
        request.urlretrieve(request_url,filename=filename)
        start = subset_end
    return filenames

#automation to download hindcast global wind data from https://www.ncei.noaa.gov/thredds/catalog/model-gfs-g4-anl-files/catalog.html
#start: start datetime
#end: end datetime
#returns the filename containing the requested data
def download_hindcast_wind_data(start,end):
    variables = ['u-component_of_wind_planetary_boundary','v-component_of_wind_planetary_boundary'] #wind variables
    filedir = os.path.dirname(__file__) #change directory to opendrift/data/hindcast/wind
    os.chdir(filedir)
    os.chdir("./data/hindcast/wind")
    file = concatenated_wind_file_exists(start,end) #check if concatenated wind file exists for given time range
    if file: 
        return [file] #return concatenated wind file 
    file = "h_wind_{start}__{end}.nc".format(start=start.strftime("%Y_%m_%d"), end=end.strftime("%Y_%m_%d")) #concatenated file does not exist so we need to create one
    filenames = []
    cycles = ['00','06','12','18']
    while(start < end): #subset data one day at a time
        year = start.strftime('%Y')
        month = start.strftime('%m')
        day = start.strftime('%d')
        for cycle in cycles:
            filename = "h_wind_{start}__{cycle}.nc".format(start=start.strftime("%Y_%m_%d"), cycle=cycle) 
            filenames.append(filename)
            if os.path.isfile("./{filename:s}".format(filename = filename)): #check if file exists
                continue
            request_url = 'https://www.ncei.noaa.gov/thredds/ncss/model-gfs-g4-anl-files/{year}{month}/{year}{month}{day}/gfs_4_{year}{month}{day}_{cycle}00_000.grb2?'.format(year=year, month=month, day=day, cycle=cycle) 
            for v in variables:
                query = 'var={v:s}&'.format(v=v)
                request_url = request_url + query
            start_str = start.strftime("%Y-%m-%dT{cycle}:%M:%SZ".format(cycle=cycle))
            time = 'time_start={start:s}&time_end={stop:s}'.format(start=start_str, stop=start_str)
            request_url = request_url + time
            print('Downloading wind data file on {start:s}, cycle {cycle}'.format(start=start_str, cycle = cycle))
            request.urlretrieve(request_url,filename=filename)
        start = start + datetime.timedelta(days=1)
    concatenate_wind_files(filenames=filenames, outfile=file)
    return [file]


# tool to download DARPA drifter data from https://oceanofthings.darpa.mil/data#tab-all
# filename: filename of data to download from site
# mostly interested in these files https://oceanofthings.darpa.mil/data#tab-fft-challenge
def download_darpa_drifer_data():
    filename = 'challenge_30-day_sofar_20211102_csv.csv'
    filedir = os.path.dirname(__file__) #change directory to opendrift/data/drifters/darpa
    os.chdir(filedir)
    os.chdir("./data/drifters/darpa")
    request_url = 'https://oceanofthings.darpa.mil/docs/Sample%20Data/{filename}'.format(filename=filename)
    if not os.path.isfile("./{filename:s}".format(filename = filename)): #check if file exists
        print(request_url)
        request.urlretrieve(request_url,filename=filename)
    return filename

