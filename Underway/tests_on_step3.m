% This file tests re-formated (step 3) data with previous processing done at time of cruise
%-----------------------------

# Paths to step 1 output (n==new, o==old)
# Path_n_1 = '/users/rsg/tjor/scratch_network/AMT_underway/AMT27/Processed/Underway/Step1/optics_amt27_267.mat';
# Path_n_15 = '/users/rsg/tjor/scratch_network/AMT_underway/AMT27/Processed/Underway/Step1/optics_amt27_281.mat';

# Data_1 = load(Path_n_1);
# Data_15 = load(Path_n_15);
# looks ok.

# Paths to step 2 output (n==new, o==old)
#Path_n_1 = '/users/rsg/tjor/scratch_network/AMT_underway/AMT27/Processed/Underway/Step2/proc_optics_amt27_267.mat';
#Path_n_15 = '/users/rsg/tjor/scratch_network/AMT_underway/AMT27/Processed/Underway/Step2/proc_optics_amt27_281.mat';

#Data_1 = load(Path_n_1);
#Data_15 = load(Path_n_15);
# looks ok.




# Paths to step 3 output (n==new, o==old)
Path_n = '/users/rsg/tjor/scratch_network/AMT_underway/AMT27/Processed/Underway/Step3/amt27_optics.mat';
Path_o = '/data/datasets/cruise_data/active/AMT27/Public_Read_Only_Copy/AMT27_DY084/Optics_group/Processed/Underway/Processed/Final/amt27_optics.mat';

# Read step 3 data structures
Data_n = load(Path_n);
Data_o = load(Path_o);


time_n = Data_n.amt27.time
lat_n = Data_n.amt27.uway.lat
chl_n = Data_n.amt27.acs.chl

time_o = Data_o.amt27.time
lat_o = Data_o.amt27.uway.lat
chl_o = Data_o.amt27.acs.chl

#length(time_n)
#length(time_o)

#figure
#plot(lat_o, time_o)
#hold on
#plot(lat_n, time_n)



figure
plot(lat_n, log10(chl_n),'r')
hold on
plot(lat_o, log10(chl_o),'b:')
legend ("new processing", "old processing");
ylabel('log(Chl)')
xlabel('Latiude (deg)')
xlim([30 50])
ylim([-2 0])

#figure
#plot(lat_n, log10(chl_n),'r')
#hold on
#plot(lat_o, log10(chl_o),'b:')
#legend ("new processing", "old processing");
#ylabel('log(Chl)')
#xlabel('Latiude (deg)')
#axis ([-32 -30])


keyboard


keyboard


