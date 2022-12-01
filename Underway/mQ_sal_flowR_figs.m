# Plots related to mQ filtering (removal of pure-water references)  
# based on salinity & flow rate 
######################################################################

Path =  '/users/rsg/tjor/scratch_network/AMT_underway/AMT27/Processed/Underway/Step3/amt27_optics.mat';

Data = load(Path);

timestamp = Data.amt27.time
lat = Data.amt27.uway.lat
chl = Data.amt27.acs.chl
flow = Data.amt27.flow
sal = Data.amt27.ctd.sal

plot(amt_optics.time, log10(amt_optics.acs.chl),'b')
keyboard

# filter by salinity and flow-rate
pure_index = find(flow < 15 & sal < 25) # data to be rejected
# pure_index_flow_only = find(abs(flow) < 20) # data to be rejected in absence of CTD
sal_index = find(flow > 20 & sal > 33) # data to be kept
# pure_index_sal_only = find(abs(flow) > 20) # data to be kept

pkg load signal
med_chl_10 = medfilt1(chl, 61,'omitnan')
med_sal_index = find(abs(med_chl_10 - chl) < 0.5 & flow > 20 & sal > 34) # data to be kept

graphics_toolkit("gnuplot")
# scatter plot showing good/bad data with N values
clf;
figure(1,'visible','off')
scatter(flow, sal,"b");
hold on
scatter(flow(sal_index),sal(sal_index),"r");
legend({strcat("Saline (keep): N = ", num2str(length(sal_index))), strcat("Pure (filter-out): N= ", num2str(length(pure_index)))});
legend boxoff
legend boxon
xlabel("Flow rate [-]",'fontsize', 16); # legends don't work in scatter plots
ylabel("Salinity [PSU]",'fontsize', 16);
fnameout = ['AMT27_flowrateVSsalscattter'];
print('-f1',fnameout,'-dpng','-r150')
close('all')

clf;
figure(1,'visible','off')
plot(lat, flow,'b');
hold on;
plot(lat(sal_index), flow(sal_index),'r');
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('Flow rate [-]','fontsize', 16);
xlabel('Latitude [deg]','fontsize', 16);
legend boxon
set(gca, "fontsize", 16);
fnameout = ['AMT27_flowrate'];
print('-f1',fnameout,'-dpng','-r150')

clf;
figure(1,'visible','off')
plot(lat, sal,'b')
hold on
plot(lat(sal_index), sal(sal_index),'r')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('Salinity rate [PSU]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
legend boxon
fnameout = ['AMT27_sal'];
print('-f1',fnameout,'-dpng','-r150')
close('all')

clf;
figure(1,'visible')
plot(lat, log10(chl),'b')
hold on
plot(lat(sal_index), log10(chl(sal_index)),'r')
hold on
#plot(lat(med_sal_index), log10(chl(med_sal_index)),'g')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), 
        strcat("Filtered (sal & flow): N= ", num2str(length(sal_index))), 
       strcat("Filtered (sal, flow & med): N= ", num2str(length(med_sal_index)))})
ylabel('log Chl [mg/m^3]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
legend boxon
fnameout = ['AMT27_chl'];
print('-f1',fnameout,'-dpng','-r150')
close('all')


clf;
figure(1,'visible','off')
plot(lat, flow,'b')
hold on
plot(lat(sal_index), flow(sal_index),'r')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('Flow rate [-]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
xlim([20 25])
legend boxon
fnameout = ['AMT27_flowrate_zoom'];
print('-f1',fnameout,'-dpng','-r150')
close('all')

clf;
figure(1,'visible','off')
plot(lat, sal,'b')
hold on
plot(lat(sal_index), sal(sal_index),'r')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('Salinity [PSU]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
xlim([20 25])
legend boxon
fnameout = ['AMT27_sal_zoom'];
print('-f1',fnameout,'-dpng','-r150')
close('all')

clf;
figure(1,'visible','off')
plot(lat, log10(chl),'b')
hold on
plot(lat(sal_index), log10(chl(sal_index)),'r')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('log Chl [mg/m^3]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
xlim([20 25])
legend boxon
fnameout = ['AMT27_ch_zoom'];
print('-f1',fnameout,'-dpng','-r150')
close('all')


clf;
figure(1,'visible','off')
plot(lat, flow,'b')
hold on
plot(lat(sal_index), flow(sal_index),'r')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('Flow rate [-]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
xlim([-35 30])
legend boxon
fnameout = ['AMT27_flowrate_zoom2'];
print('-f1',fnameout,'-dpng','-r150')
close('all')

clf;
figure(1,'visible','off')
plot(lat, sal,'b')
hold on
plot(lat(sal_index), sal(sal_index),'r')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), strcat("Filtered: N= ", num2str(length(sal_index)))});
ylabel('Salinity [PSU]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
xlim([-35 30])
legend boxon
fnameout = ['AMT27_sal_zoom2'];
print('-f1',fnameout,'-dpng','-r150')
close('all')




clf;
figure(1,'visible','off')
plot(lat, log10(chl),'b')
hold on
plot(lat(sal_index), log10(chl(sal_index)),'r')
hold on
plot(lat(med_sal_index), log10(chl(med_sal_index)),'g')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), 
        strcat("Filtered (sal & flow): N= ", num2str(length(sal_index))), 
        strcat("Filtered (sal, flow & med): N= ", num2str(length(med_sal_index)))});
ylabel('log Chl [mg/m^3]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
xlim([20 25])
legend boxon
fnameout = ['AMT27_ch_zoom2'];
print('-f1',fnameout,'-dpng','-r150')
close('all')


clf;
figure(1,'visible','off')
plot(lat, log10(chl),'b')
hold on
plot(lat(sal_index), log10(chl(sal_index)),'r')
#hold on
#plot(lat(med_sal_index), log10(chl(med_sal_index)),'g')
legend({strcat("Unfiltered: N = ", num2str(sum(~isnan(flow)))), 
        strcat("Filtered (sal & flow): N= ", num2str(length(sal_index))), 
        strcat("Filtered (sal, flow & med): N= ", num2str(length(med_sal_index)))});
ylabel('log Chl [mg/m^3]','fontsize', 16)
xlabel('Latitude [deg]','fontsize', 16)
legend boxon
fnameout = ['AMT27_chl_zoom3'];
xlim([35 40])
print('-f1',fnameout,'-dpng','-r150')
close('all')
