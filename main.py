import datetime
import os
from download_datasets import *
from utils import *

# initialize directory structure required for simulation 
# structure should be as follows after running this method 
# drift_predict_dateset\
#   data\
#       forecast\
#           wind\
#           current\
#       hindcast\
#           wind\
#           current\
#       drifters\ 
#           darpa\
def init_directory_structure(): 
    os.chdir(os.path.dirname(os.path.abspath(__file__))) #change to current directory
    if not os.path.exists('data'): #create data directory
        os.makedirs('data')
    os.chdir('./data') #change to data directory
    if not os.path.exists('forecast'): #create forecast directory
        os.makedirs('forecast')
    if not os.path.exists('hindcast'): #create hindcast directory
        os.makedirs('hindcast')
    if not os.path.exists('drifters'): #create drifters directory
        os.makedirs('drifters')
    os.chdir('./forecast') #switch to forecast direcory
    if not os.path.exists('wind'): #create wind directory
        os.makedirs('wind')
    if not os.path.exists('current'): #create current directory
        os.makedirs('current')
    os.chdir('../hindcast') #switch to hindcast directory
    if not os.path.exists('wind'): #create wind directory
        os.makedirs('wind')
    if not os.path.exists('current'): #create current directory
        os.makedirs('current')
    os.chdir('../drifters') #switch to drifters directory
    if not os.path.exists('darpa'): #create darpa directory 
        os.makedirs('darpa')
    os.chdir(os.path.dirname(os.path.abspath(__file__))) #change back to current directory

#function to get files from dataset in requested range
#start: start datetime
#end: end datetime
#returns an array of relative filepaths of dataset files. 
#the dataset files will be downloaded locally on the machine
def get_dataset(start,end):
    if (check_valid_dates(start,end)):
        dataset_filenames = []
        start_date = datetime.datetime.strptime(start.strftime('%Y-%m-%d'),'%Y-%m-%d')
        if not start_of_day(end): #if its not the start of the day we will need data up to the start of the next day
            end_date = datetime.datetime.strptime(end.strftime('%Y-%m-%d'),'%Y-%m-%d') + datetime.timedelta(days=1)
        else:
            end_date = end
        wind_filenames = download_hindcast_wind_data(start_date,end_date)
        current_filenames = download_hindcast_current_data(start_date,end_date)
        for wfile in wind_filenames: 
            dataset_filenames.append('./data/hindcast/wind/{filename}'.format(filename=wfile))
        for cfile in current_filenames: 
            dataset_filenames.append('./data/hindcast/current/{filename}'.format(filename=cfile))
        os.chdir(os.path.dirname(os.path.abspath(__file__))) #change back to current directory 
        return dataset_filenames
    else:
        print("Requested dates outside range of dataset. Please enter dates in the range 2021-11-02 to 2021-12-03")
        return None

def get_drifter_trajectories(start,end): 
    if (check_valid_dates(start,end)): 
        filename = download_darpa_drifer_data() 
        drifter_data = process_darpa_drifter_data(filename)
        sliced_drifter_data = slice_darpa_drifter_data(start,end,drifter_data)
        os.chdir(os.path.dirname(os.path.abspath(__file__))) #change back to current directory 
        return sliced_drifter_data
    else:
        print("Requested dates outside range of dataset. Please enter dates in the range 2021-11-02 to 2021-12-03")
        return None



def main():
    start = datetime.datetime(2021,11,2)
    end = datetime.datetime(2021,12,3)
    files = get_dataset(start,end) #datafiles in time range
    trajectories = get_drifter_trajectories(start,end) #drifter trajectories in time range
    

if __name__ == "__main__":
    init_directory_structure()
    main()
