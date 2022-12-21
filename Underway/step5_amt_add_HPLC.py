#!/usr/bin/env python
# coding: utf-8

# ### ay data need to be in the NetCDF before the debiasing the ACS chl
# #### Note: this is based on the NASA HPLC xls file for AMT29

# In[1]:


# this is to make the Jupyter notebook as wide as the screen (on the Mac at least)
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))
get_ipython().run_line_magic('config', "InlineBackend.figure_format ='retina'")


# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from scipy import signal as sg
from datetime import datetime as dt


# In[3]:


get_ipython().run_line_magic('matplotlib', 'notebook')


# In[4]:


def prcrng(x):
    return (np.nanpercentile(x,84) - np.nanpercentile(x,16))/2.


# In[5]:
DIN_hplc = "/data/datasets/cruise_data/active/AMT27/HPLC/"
DIN_acs = "~/scratch_network/AMT_underway/AMT27/Processed/Underway/Step3/"


# In[6]:


fn_hplc =  "Results DAN_2018_019.xlsx"
fn_meta = "AMT27_Station_log_Tilstone_forBODC.xlsx"
fn_optics = "amt27_final.nc"


# In[7]: # for AMT 27, the hplc spreadsheet was in different format, so file reading was modified
    
df_hplc = pd.read_excel(DIN_hplc + fn_hplc, sheet_name = "csv", header = 0, engine = 'openpyxl', nrows=51) # nrows used, so that only hplc data with corresponding meta data us selected
df_hplc = df_hplc.drop(labels=[0,1,2], axis=0)
df_hplc = df_hplc.rename(columns={"Unnamed: 0": "Label"})    # Label == sample ID 
df_hplc = df_hplc.rename(columns={"Unnamed: 1": "vol"})      
df_hplc = df_hplc.rename(columns={"Unnamed: 2": "DHI no"})   
df_hplc = df_hplc.reset_index(drop=True)
for i in range(len(df_hplc)): # convert to same Label format as AMT27 metadata
       df_hplc["Label"][i] =  'UW' + str(df_hplc["Label"][i][-3:])
  
    
# In[8]: # AMT27 metadata needed signficant adjustment to match previous fields

df_meta = pd.read_excel(DIN_hplc + fn_meta, sheet_name = "AMT27_Underway_HPLC", header = 1, engine = 'openpyxl')

# fields to rename
df_meta = df_meta.rename(columns={"Description": "Label"})  # Description == label == sample ID 
df_meta = df_meta.rename(columns={"Time at surface": "Time"})
df_meta = df_meta.rename(columns={"lat": "Lat"}) # this is decimal lat, lon 
df_meta = df_meta.rename(columns={"lon": "Lon"})
df_meta = df_meta.rename(columns={"Julian Day": "SDY"})
df_meta = df_meta.rename(columns={"HPLC, Vol filtered (litres)": "Volum"})


# fields to remove
df_meta = df_meta.drop('Latitude', axis=1) # integer latitude
df_meta = df_meta.drop('minutes', axis=1) # arc mins 
df_meta = df_meta.drop('Decimal', axis=1) # arc secs
df_meta = df_meta.drop('Unnamed: 3', axis=1) # redudant
df_meta = df_meta.drop('Unnamed: 4', axis=1) # redudant
df_meta = df_meta.drop('Longitude', axis=1) # integer longitude 
df_meta = df_meta.drop('minutes.1', axis=1) # arc mins 
df_meta = df_meta.drop('Decimal.1', axis=1) # arc secs
df_meta = df_meta.drop('Unnamed: 8', axis=1) # redudant
df_meta = df_meta.drop('Unnamed: 9', axis=1) # redudant
df_meta = df_meta.drop('Time at depth', axis=1) #  blanks in xls - Time surface used for time
df_meta = df_meta.drop('Time on deck', axis=1) #  blanks in xls
df_meta = df_meta.drop('time', axis=1) #  decimal time: not used
# df_meta


# In[9]:


# merge two tables to extract info from df_meta
df_hplc = pd.merge(df_hplc, df_meta, on=['Label'])

# df_hplc.keys()


# In[10]:


# convert DHI pigment names to NASA pigment names for submission
#                            DHI  :  NASA
dhi2nasa = {      "Chlorophyll c3":"Chl_c3",
#                 "Chlorophyll c2":"Chl c1c2", # these two successive pigments need to be merged (see below)
#           "Chlorophyll c1+MgDVP":"Chl c1c2",
                "Chlorophyllide a":"Chlide_a",
                  "Pheophorbide a":"Phide_a",
                       "Peridinin":"Perid",
              "19-but-fucoxanthin":"But-fuco",
                     "Fucoxanthin":"Fuco",
                      "Neoxanthin":"Neo",
                  "Prasinoxanthin":"Pras",
                    "Violaxanthin":"Viola",
              #"19-Hex-fucoxanthin":"Hex-fuco", AMT 28
              "19-hex-fucoxanthin":"Hex-fuco", # AMT 27
                     "Astaxanthin":"DHI_only_Astaxanthin",
                  "Diadinoxanthin":"Diadino",
            "Myxoxanthophyll-like":"DHI_only_Myxoxanthophyll-like",
                     "Alloxanthin":"Allo",
                    "Diatoxanthin":"Diato",
                      "Zeaxanthin":"Zea",
                          "Lutein":"Lut",
                     "Chl C2 MGDG":"DHI_only_Chl_C2_MGDG",
                   "Chlorophyll b":"Tot_Chl_b",
                "DV chlorophyll a":"DV_Chl_a",
               # "MV chlorophyll a":"MV_Chl_a", # AMT28 - DHI correctly spelt
                 "MV chlorphyll a":"MV_Chl_a",  #  AMT27 - DHI incorrect spelling?
                    "Pheophytin a":"Phytin_a"}
#                     "a-carotene":"Alpha-beta-Car", # these two successive pigments need to be merged (see below)
#                     "b-carotene":"Alpha-beta-Car"}

# rename DHI columns with NASA names
df_hplc = df_hplc.rename(columns = dhi2nasa)


# Create merged pigments
# "Alpha-beta-Car", 
# df_hplc["Alpha-beta-Car"] = df_hplc["a-carotene"] + df_hplc["b-carotene"] # this was used to merge for AMT28
# df_hplc = df_hplc.drop(columns=["a-carotene", "b-carotene"])
df_hplc = df_hplc.rename(columns={'a+b-carotene': "Alpha-beta-Car"})  # for AMT27, already merged & we simpy rename 

           
# "Chl c1c2"
# df_hplc["Chl_c1c2"] = df_hplc["Chlorophyll c2"] + df_hplc["Chlorophyll c1+MgDVP"]  # this was used to merge for AMT28
# df_hplc = df_hplc.drop(columns=["Chlorophyll c2", "Chlorophyll c1+MgDVP"])
df_hplc = df_hplc.rename(columns={'Chlorophyll c1+c2': "Chl_c1c2"})   # for AMT27, already merged & we simpy rename 


# "Tot_Chl_a" = DV_Chl_a + MV_Chl_a + Chlide_a (+ Chl_a allomers + Chl_a epimers)
df_hplc["Tot_Chl_a"] = df_hplc["DV_Chl_a"] + df_hplc["MV_Chl_a"] + df_hplc["Chlide_a"]

# "Tot_Chl_c" = Tot_Chl_a + Tot_Chl_b + Tot_Chl_c
df_hplc["Tot_Chl_c"] = df_hplc["Chl_c3"] + df_hplc["Chl_c1c2"]

# "Tchl" = Tot_Chl_a + Tot_Chl_b + Tot_Chl_c
df_hplc["Tchl"] = df_hplc["Tot_Chl_a"] + df_hplc["Tot_Chl_b"] + df_hplc["Tot_Chl_c"]

# "PPC" (photoprotective carotenoids) = allo + diadino + diato + zea + alpha-beta-car)
df_hplc["PPC"] = df_hplc["Allo"] + df_hplc["Diadino"] + df_hplc["Diato"] + df_hplc["Zea"] + df_hplc["Alpha-beta-Car"]

# "PSC" (photosynthetic carotenoids) = but-fuco + fuco + hex-fuco + perid)
df_hplc["PSC"] = df_hplc["But-fuco"] + df_hplc["Fuco"] + df_hplc["Hex-fuco"] + df_hplc["Perid"] 

# "PSP" (phosynthetic pigments) = PSC + TChl
df_hplc["PSP"] = df_hplc["PSC"] + df_hplc["Tchl"] 

# "Tcar" (total carotenoids) = PPC + PSC
df_hplc["Tcar"] = df_hplc["PPC"] + df_hplc["PSC"] 

# "Tacc" (total accessory pigments) = PPC + PSC + Tot_Chl_b + Tot_Chl_c 
df_hplc["Tacc"] = df_hplc["PPC"] + df_hplc["PSC"] + df_hplc["Tot_Chl_b"] + df_hplc["Tot_Chl_c"] 

# "Tpg" (total pigments) = TAcc + Tot_Chl_a
df_hplc["Tpg"] = df_hplc["Tacc"] + df_hplc["Tot_Chl_a"] 

# "DP" (total diagnostic pigments) = PSC + allo + zea + Tot_Chl_b
df_hplc["DP"] = df_hplc["PSC"] + df_hplc["Allo"] + df_hplc["Zea"] + df_hplc["Tot_Chl_b"]


# new dictionary with additional pigments
derived_pigs = {"Alpha-beta-Car":"Alpha-beta-Car",
                "Chl_c1c2":"Chl_c1c2",
                "Tot_Chl_a":"Tot_Chl_a",
                "Tot_Chl_c":"Tot_Chl_c",
                "Tchl":"Tchl",
                "PPC":"PPC",
                "PSC":"PSC",
                "PSP":"PSP",
                "Tcar":"Tcar",
                "Tacc":"Tacc",
                "Tpg":"Tpg",
                "DP":"DP"      }

# df_hplc.keys()



# In[11]:


# merge dictonaries with names of all pigments
all_pigs = dict(dhi2nasa, **derived_pigs)


# In[12]:


# find matching keys and merge them into a single one
for key in df_hplc.keys():
    if "_x" in key:
        print(key)
        if ~(np.all(df_hplc[key] == df_hplc[key[:-1]+"y"])):
            print([key, " not matching"])
        else:
            # drop *_x key
            print(["droppping " + key ])
            df_hplc = df_hplc.drop(columns = [key])
            # rename *_y key
            print(["renaming " + key ])
            df_hplc = df_hplc.rename(columns = {key[:-1]+"y" : key[:-2]})
            


# In[13]:


# convert date (numpy.datetime64) and time (datetime.time) to a single datetime object
from datetime import datetime as dt

# convert date from (numpy.datetime64) to (datetime.time) 
ts = (df_hplc.Date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
newts = [dt.utcfromtimestamp(tsi) for tsi in ts]

# add Time object to Date object to get DateTime object
mydatetime = [dt.combine(newts[i], df_hplc.Time.values[i]) for i,j in enumerate(df_hplc.Time)  ]

# create "Time" key in df_hplc
df_hplc['time'] = mydatetime

# drop Date and Time
df_hplc = df_hplc.drop(columns = ["Date", "Time"])
                       
df_hplc = df_hplc.sort_values(by = ['time'])
df_hplc = df_hplc.reset_index(drop = True)

df_hplc


# In[14]: # step 14 is commented out for AMT 27, as Lat, Lon are already
# given in degrees

# clean up lat
# tmpla = df_hplc['Lat'].values
# for i,la in enumerate(tmpla):
#    if (type(la) != float) & (type(la) != int):
#         print(type(la))
#         print(i, "    ", la)
        # assume the string is similar to "31°31.784'W"
        
        # replace "º" by "°"
#        la = la.replace("º", "°")
        
#        degrees = float(la.split("°")[0]) 
#        minutes = float(la.split("°")[-1].split("'")[0])
#        NoS = la.split("°")[-1].split("'")[-1]
#        sign = -1
#        if (NoS.upper() == "N"):
#           sign = 1
#        df_hplc.at[i, 'Lat'] = sign*(degrees + minutes/60.)

# clean up lon
# tmplo = df_hplc['Lon'].values
# for i,lo in enumerate(tmplo):
#    if (type(lo) != float) & (type(lo) != int):
#         print(type(lo))
#         print(i, "    ", lo)
        # assume the string is similar to "31°31.784'"
        
        # replace "º" by "°"
#        lo = lo.replace("º", "°")
        
#        degrees = float(lo.split("°")[0]) 
#        minutes = float(lo.split("°")[-1].split("'")[0])
#        EoW = lo.split("°")[-1].split("'")[-1]
#        sign = -1
#        if (EoW.upper() == "E"):
#            sign = 1
#        df_hplc.at[i, 'Lon'] = sign*(degrees + minutes/60.)


# In[15]:


# extract surface data

# replace UND label with nominal depth of rUNDerway measurements
df_hplc.Depth[df_hplc.Depth=="UND"] = 7

isurf = df_hplc["Depth"] < 10
df_hplc_surf = df_hplc[isurf]
df_hplc_surf = df_hplc_surf.set_index("time")
df_hplc_surf



# In[16]:


# read ACS data
fn_acs = fn_optics
acs = xr.open_dataset(DIN_acs+fn_acs)
acs.close()


# replace uway_long with uway_lon
if "uway_long" in acs.keys():
  #  acs.uway_lon = acs.uway_long # tjor - command did not work using spyder..?
    acs['uway_lon'] = acs['uway_long']
    acs = acs.drop(labels="uway_long")

acs


# In[17]:


# fig, ax = plt.subplots(2,1, figsize=[12,6], sharex=True)
# ax[0].plot(acs.time, acs.uway_lon, '.')
# ax[1].plot(acs.time, acs.uway_lat, '.')


# In[18]:


# 


# ### Add HPLC data to NetCDF file

# In[19]:


# convert to lower case some keys in hplc dataframe
if "Lon" in  df_hplc_surf:
    df_hplc_surf = df_hplc_surf.rename(columns = {"Lon":"lon"})
if "Lat" in  df_hplc_surf:
    df_hplc_surf = df_hplc_surf.rename(columns = {"Lat":"lat"})
if "Time" in  df_hplc_surf:
    df_hplc_surf = df_hplc_surf.rename(columns = {"Time":"time"})
if "Depth" in  df_hplc_surf:
    df_hplc_surf = df_hplc_surf.rename(columns = {"Depth":"depth"})


# In[20]:


df_hplc_surf.keys()


# In[21]:


# create hplc_time coordinate
acs = acs.assign_coords(coords={'hplc_time' : (['hplc_time'], df_hplc_surf.index, {'time zone' : 'UTC'}) })
acs.hplc_time.encoding['units'] = "seconds since 1970-01-01 00:00:00"
acs.hplc_time.encoding['calendar'] = "proleptic_gregorian"


# In[22]:


# #### read HPLC metadata on pigments (if NASA)
# hplc_pignm = pd.read_excel(DIN_hplc + fn_hplc, sheet_name = "information", header = 4, engine = 'openpyxl',
#                         nrows = 38, usecols = [1, 3, 4, 12, 13, 14], dtype=str)

# # shift info around in original table
# df1 = hplc_pignm.iloc[:, [0,1,2]]
# df2 = hplc_pignm.iloc[:, [3,4,5]] 
# df2 = df2.rename(columns={ df2.keys()[0]: 'abbreviation',
#                      df2.keys()[1]: 'name',
#                      df2.keys()[2]: 'notes'
#                     })
# df1 = df1.rename(columns={ df1.keys()[0]: 'abbreviation',
#                      df1.keys()[1]: 'name',
#                      df1.keys()[2]: 'notes'
#                     })
# # concatenate to subsets of attributes
# df1 = df1.append(df2, ignore_index=True)

# # find indices with empty abbreviations and drop them
# ind = []
# for irow in range(len(df1['abbreviation'].values)):
#     if type(df1['abbreviation'].values[irow])==float:
#         ind.append(irow)
    
# df_hplc_pignm = df1.drop(ind)    


# In[23]:


# df_hplc.plot.scatter(x='lat', y='DV_Chl_b', xlim=(-60,60), ylim=(0,0.3), marker='o', grid='on', alpha=0.5)


# In[24]:


### add HPLC variables to acs dataset
# drop time-related columns
if 'year' in df_hplc_surf.keys():
    df_hplc_surf = df_hplc_surf.drop(columns=['year', 'month', 'day', 'sdy',
                               'water_depth', 'name of water body' ])
df_hplc_surf.keys()


# In[25]:


## for NASA only
# df_hplc_pignm.abbreviation.values


# In[26]:


# if NASA

# # find names of hplc vars
# hplc_cols = df_hplc_surf.keys()
# #add attributes to each variable and add it to acs xr dataset
# _var = ()
# _attrs = {}
# for ivar in hplc_cols:
# #     print(ivar)
#     lbl = ivar.replace(" ", "_").replace("__", "_") # repalce spaces with _
#     print(lbl)
    
#     if 'diameter' in ivar:
#         lbl = lbl[:-5]
#         _attrs = {'units': 'mm'}
#         _var = (['hplc_time'], df_hplc[ivar] ) 
    
#     elif lbl in df_hplc_pignm['abbreviation'].values:
#         # find index of df_hplc_pignm ivar
#         ik = list(df_hplc_pignm['abbreviation']).index(lbl)
# #         print("^^^^^^^^^^^this is a pigment")
#         _attrs = {'units' : 'mg/m3',
#                   'full_pigment_name' : df_hplc_pignm['name'].values[ik],
#                   'notes' : df_hplc_pignm['notes'].values[ik]}
#         _var = (['hplc_time'], df_hplc[ivar])
# #             print(_var)
#     else:
# #         print('nothing to do: ' + ivar)
#         _attrs = {}
#         _var = (['hplc_time'], df_hplc[ivar]) 
        
        
#     acs['hplc_'+lbl] = _var
#     acs['hplc_'+lbl].attrs = _attrs
    
#     # reset _var and _attrs
#     _var = ()
#     _attras = {}
    
# #     print(lbl)


# ## HOW TO CHECK THAT ALL PIGMENTS HAVE HAD THEIR ATTRIBUTES?


# In[27]:


pigs_names = {value:key for key, value in all_pigs.items()} 
# pigs_names


# In[28]:


# find names of hplc vars
hplc_cols = df_hplc_surf.keys()
#add attributes to each variable and add it to acs xr dataset
_var = ()
_attrs = {}
for ivar in hplc_cols:
#     print(ivar)
    lbl = ivar.replace(" ", "_").replace("__", "_") # repalce spaces with _

    
    if 'diameter' in ivar:
        lbl = lbl[:-5]
        _attrs = {'units': 'mm'}
        _var = (['hplc_time'], df_hplc_surf[ivar] ) 
        acs['hplc_'+lbl.lower()] = _var
        acs['hplc_'+lbl.lower()].attrs = _attrs
#         print(["NOT A PIGM: "+lbl.lower()])
        
    elif lbl in pigs_names.keys():
#         print("^^^^^^^^^^^this is a pigment")
        _attrs = {'units' : 'mg/m3'}
        _var = (['hplc_time'], df_hplc_surf[ivar])
#             print(_var)
        acs['hplc_pigs_'+lbl] = _var
        acs['hplc_pigs_'+lbl].attrs = _attrs
#         print(lbl)
        
    else:
#         print('nothing to do: ' + ivar)
        _attrs = {}
        _var = (['hplc_time'], df_hplc_surf[ivar]) 
        acs['hplc_'+lbl.lower()] = _var
        acs['hplc_'+lbl.lower()].attrs = _attrs
#         print(["NOT A PIGM: "+lbl.lower()])
        
    
    # reset _var and _attrs
    _var = ()
    _attras = {}
    
#     print(lbl)


## HOW TO CHECK THAT ALL PIGMENTS HAVE HAD THEIR ATTRIBUTES?


# In[29]:


# var = 'hplc_filter_storage_before_shipment_to_GFC'
# ty = [type(acs[var].values[i]) for i,tmp in enumerate(acs[var].values)]

# if ~np.all([ty[i]==ty[0] for i,tmp in enumerate(ty)]):
#     print(ty)


# In[30]:


"hplc_ctd" in acs.keys()


# In[32]:


# ensure that hplc_variables with text and numbers in are arrays of strings
if "hplc_comments" in acs.keys():
    new_comments = [str(acs.hplc_comments.values[i]) for i in range(len(acs.hplc_comments.values))]
    acs['hplc_comments'] = (['hplc_time'], new_comments)

if "hplc_comments_x" in acs.keys():
    new_comments = [str(acs.hplc_comments_x.values[i]) for i in range(len(acs.hplc_comments_x.values))]
    acs['hplc_comments_x'] = (['hplc_time'], new_comments)

if "hplc_comments_y" in acs.keys():
    new_comments = [str(acs.hplc_comments_y.values[i]) for i in range(len(acs.hplc_comments_y.values))]
    acs['hplc_comments_y'] = (['hplc_time'], new_comments)

if "hplc_station" in acs.keys():
    new_st = [str(acs.hplc_station.values[i]) for i in range(len(acs.hplc_station.values))]
    acs['hplc_station'] = (['hplc_time'], new_st)

if "hplc_ctd" in acs.keys():
    new_st = [str(acs.hplc_ctd.values[i]) for i in range(len(acs.hplc_ctd.values))]
    acs['hplc_ctd'] = (['hplc_time'], new_st)

if "hplc_bottle" in acs.keys(): # this was not in AMT 27, so if conditional added - to check
    new_btl = [str(acs.hplc_bottle.values[i]) for i in range(len(acs.hplc_bottle.values))]
    acs['hplc_bottle'] = (['hplc_time'], new_btl)

for ikey in acs.keys():
    if 'hplc' not in ikey:
        continue
    acs[ikey].dtype


# In[33]:


# add extra metadata
acs['hplc_file'] = fn_hplc


# In[34]:


# fig, ax = plt.subplots(1)
# ax.scatter(acs['hplc_lat'].values, acs['hplc_Diato'].values, marker='o', alpha=0.5)
# ax.set_xlim([-60, 60])
# ax.set_ylim([0, 0.06])
# ax.grid('on', ls='--')


# In[35]:


# fig, ax = plt.subplots(1, figsize=(10, 4))
# # ax.plot(acs.time, acs.acs_chl/acs.acs_ap[:,acs.wv==490], 'k.', lw=0.5, ms=1, alpha=0.5)
# ax.plot(acs.time, acs.ay_slope, 'r.', lw=0.5, ms=1)
# ax.plot(acs.time, acs.cy_slope, 'k.', lw=0.5, ms=1)
# ax.grid('on', ls='--', lw=0.5)


# In[36]:


acs['acs_chl'].attrs


# In[37]:


# create acx_chl variable that merges the ac9_chl and acs_chl if available
if 'ac9_chl_adj' in acs.keys():
    acs["acx_chl"] = (['time'], np.nanmean(np.asarray([acs['ac9_chl_adj'].values, acs['acs_chl'].values]), axis=0) )
    acs["acx_chl"].attrs = {"acx_chl_units":"mg/m3",
                           "acx_chl_comment":"merged the ac9_chl and acs_chl",
                           }

# plot it
fig,ax = plt.subplots(2,1, figsize=[13,6])
# ax[0].semilogy(acs.time, acs.acx_chl, 'ro', lw=0.5, ms=5, mfc='none', alpha=0.05)
ax[0].semilogy(acs.time, acs.acs_chl, '.', lw=0.5, ms=1, mfc='none', alpha=0.15)
# ax[0].semilogy(acs.time, acs.ac9_chl_adj, 'k.', lw=0.5, ms=1, mfc='none', alpha=0.15)

# ax[1].semilogy(np.arange(len(acs.time)), acs.acx_chl, 'ro', lw=0.5, ms=5, mfc='none', alpha=0.15)
ax[1].semilogy(np.arange(len(acs.time)), acs.acs_chl, '.', lw=0.5, ms=1, mfc='none', alpha=0.15)
# ax[1].semilogy(np.arange(len(acs.time)), acs.ac9_chl_adj, 'k.', lw=0.5, ms=1, mfc='none', alpha=0.15)


# In[38]:
acs


# In[39]:


# manually identify (using plot above) noisy parts of the acx_chl timeseries
print(' check this manual step for each cruise')
#i2rm = [  [34104, 35027], # start and end index of noisy period 1 # AMT28
#          [39190, 39714], # start and end index of noisy period 2
#          [46767, 46861]  # start and end index of noisy period 3
#       ]
i2rm = []
 

# set values to nan inside the above intervals
for istart,tmp in enumerate(i2rm):
#     print(istart, tmp[0], tmp[1])
    if 'acx_chl' in  acs.keys():
        acs['acx_chl'].values[tmp[0]:tmp[1]] = np.nan
    else:
        acs['acs_chl'].values[tmp[0]:tmp[1]] = np.nan # 
    acs['acs_ap'].values[tmp[0]:tmp[1], :] = np.nan
    acs['acs_ap_u'].values[tmp[0]:tmp[1], :] = np.nan


# In[40]:


# filter acs data for MQ and noisy events - tjor - done in STEP 3 from AMT 27 onwards - ok to leave in here?
MIN_FLOW_RATE = 25
MIN_SAL = 33

i2f = np.where(  (acs.flow>MIN_FLOW_RATE) & (acs.uway_sal>MIN_SAL)   )[0]

fig, ax = plt.subplots(3,1, figsize=(13, 12), sharex=True)
ax[0].plot(acs.time, acs.flow, '.-', lw=0.5, ms=1, alpha=0.5)
ax[0].plot(acs.time[i2f], acs.flow[i2f], 'ro', lw=0.5, ms=5, mfc='none', alpha=0.15)
ax[0].set_ylabel('flow')
ax[0].grid('on')
ax[0].set_ylim([-1, 60])

fig0, ax0 = plt.subplots(1, figsize=(15, 5))
ax[1].plot(acs.time, acs.uway_sal, '.-', lw=0.5, ms=1, alpha=0.5)
ax[1].plot(acs.time[i2f], acs.uway_sal[i2f], 'r.', lw=0.1, ms=3, mfc='none', alpha=0.15)
ax[1].set_ylabel('salinity')
ax[1].grid('on')

fig2, ax2 = plt.subplots(1, figsize=(15, 5))
#ax[2].semilogy(acs.time, acs.acx_chl, '.-', lw=0.5, ms=1, alpha=0.5)
#ax[2].semilogy(acs.time[i2f], acs.acx_chl[i2f], 'r.', lw=0.1, ms=3, mfc='none', alpha=0.15)
ax[2].semilogy(acs.time, acs.acs_chl, '.-', lw=0.5, ms=1, alpha=0.5)
ax[2].semilogy(acs.time[i2f], acs.acs_chl[i2f], 'r.', lw=0.1, ms=3, mfc='none', alpha=0.15)
ax[2].set_ylabel('acs_chl')
ax[2].grid('on')
plt.ylim([1e-6, 10])


# In[ ]:





# In[41]:


#df_UND = df_hplc_surf.loc[(df_hplc_surf['CTD'] == "UND") & (df_hplc_surf['Bottle'] == "UND")]  - specific to AMT 28? - fields not present in AMT27 meta
#df_CTD = df_hplc_surf.loc[(df_hplc_surf['CTD'] != "UND") & (df_hplc_surf['Bottle'] != "UND")] -  specific to AMT 28? - fields not present in AMT27 meta
df_UND = df_hplc_surf
df_CTD = df_hplc_surf

# In[42]: - switc


# median filter data
MEDFILT_WIN = 31
if 'acx_chl' in  acs.keys():
    innan = np.where(~np.isnan(acs.acx_chl[i2f]))[0] # need to remove nans to prevent medfilt to be spiky near edges
    fig2, ax2 = plt.subplots(1, figsize=(13, 4))
    ax2.semilogy(acs.time[i2f][innan], acs.acx_chl[i2f][innan], 'r.-', lw=0.1, ms=1, mfc='none')
    ax2.semilogy(acs.time[i2f][innan], sg.medfilt(acs.acx_chl[i2f][innan], kernel_size=MEDFILT_WIN), 'bo', lw=1, ms=3, mfc='none', alpha = 0.05)
    ax2.grid('on')
    # plt.ylim([1e-6, 10])

else:
    innan = np.where(~np.isnan(acs.acs_chl[i2f]))[0] # added
    fig2, ax2 = plt.subplots(1, figsize=(13, 4))
    ax2.semilogy(acs.time[i2f][innan], acs.acs_chl[i2f][innan], 'r.-', lw=0.1, ms=1, mfc='none')
    ax2.semilogy(acs.time[i2f][innan], sg.medfilt(acs.acs_chl[i2f][innan], kernel_size=MEDFILT_WIN), 'bo', lw=1, ms=3, mfc='none', alpha = 0.05)
    ax2.grid('on')
    # plt.ylim([1e-6, 10])



# ax2.semilogy(acs.hplc_time, acs.hplc_pigs_Tot_Chl_a, 'go', ms=5, alpha=1)#, mfc='none')
#ax2.semilogy(df_CTD.index, df_CTD.Tot_Chl_a, 'ko', ms=7, alpha=1, mfc='none', zorder=60)
#ax2.scatter(df_CTD.index, df_CTD.Tot_Chl_a, c=df_CTD.Bottle.values, s=30, alpha=1, zorder=60, cmap = plt.get_cmap('inferno'), vmin=2, vmax=24)
#ax2.semilogy(df_UND.index, df_UND.Tot_Chl_a, 'ks', ms=7, alpha=0.85, mfc='c')


# In[44]:


#df_CTD.keys()


# In[45]:


# # merge HPCL and ACS data
# # see https://stackoverflow.com/questions/26517125/combine-two-pandas-dataframes-resample-on-one-time-column-interpolate

# # create pandas series with HPLC Tot_Chl_a data
# ds_hplc_surf = pd.Series(df_hplc_surf.Tot_Chl_a.values, index = df_hplc_surf.index)

# # averages duplicate values
# ds_hplc_surf = ds_hplc_surf.groupby('date').mean() 

# # create pandas series with medfilt ACS data
# df_acs = pd.Series(sg.medfilt(acs.acs_chl[i2f][innan], kernel_size=31), index = acs.time.values[i2f][innan])


# df_hplc_acs = pd.DataFrame({'Tot_Chl_a': ds_hplc_surf, 'acs_chl': df_acs})

# df_hplc_acs = df_hplc_acs.interpolate('index').reindex(ds_hplc_surf.index)
# df_hplc_acs


# In[46]:


# compare lat and lon of hplc and acs datasets
fig, ax = plt.subplots(2, 1, figsize = (14, 8), sharex = True)

ax[0].plot(acs.time, acs.uway_lat, '.', ms = 1, mfc = 'none')
ax[0].plot(acs.hplc_time, acs.hplc_lat, 'ro', ms = 4, mfc = 'none', alpha = 0.5)
ax[0].set_ylabel("latitude")
ax[1].plot(acs.time, acs.uway_lon, '.', ms = 1, mfc = 'none')
ax[1].plot(acs.hplc_time, acs.hplc_lon, 'ro', ms = 4, mfc = 'none', alpha = 0.5)
ax[1].set_ylabel("longitude")


# In[47]:


#df_CTD.keys()


# In[48]:


df_hplc_surf_new = df_UND
# merge HPCL and ACS data
# see https://stackoverflow.com/questions/26517125/combine-two-pandas-dataframes-resample-on-one-time-column-interpolate
# here made with dataframe instead of series

# averages duplicate values
#df_hplc_surf_new = df_hplc_surf_new.groupby('time').mean()  - swicthed off for AMT 27

# create pandas series with medfilt ACS data
if 'acx_chl' in  acs.keys():
    df_acs = pd.Series(sg.medfilt(acs.acx_chl[i2f][innan], kernel_size=31), index = acs.time.values[i2f][innan])
    df_hplc_acs = pd.DataFrame({'Tot_Chl_a': df_hplc_surf_new.Tot_Chl_a, 'acx_chl': df_acs})
else: 
    df_acs = pd.Series(sg.medfilt(acs.acs_chl[i2f][innan], kernel_size=31), index = acs.time.values[i2f][innan])
    df_hplc_acs = pd.DataFrame({'Tot_Chl_a': df_hplc_surf_new.Tot_Chl_a, 'acs_chl': df_acs})

df_hplc_acs = df_hplc_acs.interpolate('index').reindex(df_hplc_surf_new.index)
    


# In[49]:


# compute residuals and stats
if 'acx_chl' in  acs.keys():
    rres = df_hplc_acs.acx_chl.values / df_hplc_acs.Tot_Chl_a.values - 1
else:
   rres = df_hplc_acs.acs_chl.values / df_hplc_acs.Tot_Chl_a.values - 1

delta = np.nanmedian(rres)
sigma = prcrng(rres)
N = len(rres)

print(delta, sigma, N)


# In[50]:


fig, ax = plt.subplots(1,2, figsize=(10, 4))

if 'acx_chl' in  acs.keys():
    ax[0].loglog(df_hplc_acs.Tot_Chl_a.values, df_hplc_acs.acx_chl.values, 'o', ms=4, alpha=0.25)
else: 
    ax[0].loglog(df_hplc_acs.Tot_Chl_a.values, df_hplc_acs.acs_chl.values, 'o', ms=4, alpha=0.25)
    
x = np.logspace(np.log10(0.01), np.log10(10), 100)
ax[0].loglog(x, x, 'r-', lw=1)
ax[0].grid('on', ls='--')
ax[0].set_xlabel('HPLC Tot_Chl_a [mg/m3]', fontweight='bold')
ax[0].set_ylabel('ACx Chl_a [mg/m3]', fontweight='bold')

ax[1].semilogx(df_hplc_acs.Tot_Chl_a.values, rres, 'o', ms=4, alpha=0.25)
ax[1].semilogx(x, x*0, 'r-', lw=1)
ax[1].grid('on', ls='--')
ax[1].set_xlabel('HPLC Tot_Chl_a [mg/m3]', fontweight='bold')
ax[1].set_ylabel('ACx/HPLC-1 [-]', fontweight='bold')
ax[1].set_ylim([-1, 1])
ax[1].text(2, 0.8, r'$\delta$='+f'{delta:+0.3}', fontweight='bold')
ax[1].text(2, 0.7, r'$\sigma$='+f'{sigma: 0.3}', fontweight='bold')
ax[1].text(2, 0.6, f'N = {N: 0}', fontweight='bold')


# In[51]:


fig, ax = plt.subplots(1,1, figsize=(13, 4))
ax.semilogx(df_hplc_acs.index.values, rres, 'o', ms=10, alpha=0.25, zorder=60)
ax.plot(df_hplc_acs.index.values, rres*0, 'k-', lw=2, zorder=1)
ax.set_ylabel('rres = ACx_chl/HPLC_chl-1 [-]', fontweight='bold')
ax.grid('on', ls='--')
ax.set_ylim([-1, 1])


# In[52]:


ilrg_rres = np.where(abs(rres)>0.5)[0]
print(rres[ilrg_rres])
df_hplc_surf_new.iloc[ilrg_rres]


# In[53]:


df_hplc_surf_new.iloc[ilrg_rres].index.dayofyear
# tt.tm_yday


# In[54]:


df_hplc_surf_new.iloc[ilrg_rres].keys()


# In[55]:


# find dates of large rres
if 'acx_chl' in  acs.keys():
    r = df_hplc_acs.acx_chl / df_hplc_acs.Tot_Chl_a - 1
else:
    r = df_hplc_acs.acs_chl / df_hplc_acs.Tot_Chl_a - 1
ii = np.where(abs(r)>0.4)[0]
print(r[ii])
# iss = 2
# [df_hplc_acs.Tot_Chl_a[ii][iss], df_hplc_acs.acx_chl[ii][iss]]


# In[56]:


# # de-bias ACS-chl following eq 3 in Graban et al., 2020 (https://doi.org/10.1364/OE.397863)
# df_hplc_acs.acs_chl_debiased = df_hplc_acs.acs_chl*(1-delta)


# In[57]:


# fit data to power law
from scipy.optimize import curve_fit

def func(x, a, b):
    return a * x**b
if 'acx_chl' in  acs.keys():
    popt, pcov = curve_fit(func, 0.014*df_hplc_acs.acx_chl.values, df_hplc_acs.Tot_Chl_a.values)
else:
    popt, pcov = curve_fit(func, 0.014*df_hplc_acs.acs_chl.values, df_hplc_acs.Tot_Chl_a.values)
perr = np.sqrt(np.diag(pcov)) # parameter uncertainty 

print("chl_HPLC = a * chl_ACS^b " )

print("a = " + f'{popt[0]:.1f} ' + "+/- " + f'{perr[0]:.1f}' )
print("b = " + f'{popt[1]:.3f} ' + "+/- " + f'{perr[1]:.3f}' )


# In[58]:


# # compute resuduals and stats
# rres = df_hplc_acs.acs_chl_debiased.values/df_hplc_acs.Tot_Chl_a.values-1

# delta = np.nanmedian(rres)
# sigma = prcrng(rres)
# N = len(rres)

# print(delta, sigma, N)


# In[59]:


# fig, ax = plt.subplots(1,2, figsize=(10, 4))

# ax[0].loglog(df_hplc_acs.Tot_Chl_a.values, df_hplc_acs.acs_chl_debiased.values, 'o', ms=4, alpha=0.25)
# x = np.logspace(np.log10(0.01), np.log10(10), 100)
# ax[0].loglog(x, x, 'r-', lw=1)
# ax[0].grid('on', ls='--')
# ax[0].set_xlabel('HPLC Tot_Chl_a [mg/m3]', fontweight='bold')
# ax[0].set_ylabel('ACS Chl_a [mg/m3]', fontweight='bold')

# ax[1].semilogx(df_hplc_acs.Tot_Chl_a.values, rres, 'o', ms=4, alpha=0.25)
# ax[1].semilogx(x, x*0, 'r-', lw=1)
# ax[1].grid('on', ls='--')
# ax[1].set_xlabel('HPLC Tot_Chl_a [mg/m3]', fontweight='bold')
# ax[1].set_ylabel('ACS/HPLC-1 [-]', fontweight='bold')

# ax[1].text(2, 0.8, r'$\delta$='+f'{delta:+0.3}', fontweight='bold')
# ax[1].text(2, 0.7, r'$\sigma$='+f'{sigma: 0.3}', fontweight='bold')
# ax[1].text(2, 0.6, f'N = {N: 0}', fontweight='bold')


# In[60]:


# de-bias ACS-chl following eq 3 in Graban et al., 2020 (https://doi.org/10.1364/OE.397863)
if 'acx_chl' in acs.keys(): # case with merged acs ac9
    innan = np.where(~np.isnan(acs.acx_chl[i2f]))[0]
    acs['acx_chl_debiased'] = acs.acx_chl*(1-delta)
    # acs['acs_chl_debiased'] = acs.acs_chl*(1-delta)
    acs_out = pd.DataFrame(data = {'lat [degN]': acs.uway_lat[i2f][innan],
                                   'lon [degE]': acs.uway_lon[i2f][innan],
                                   'acs_chl_debiased [mg_m3]': acs.acx_chl_debiased[i2f][innan]
                                  }  ,
                          index = acs.time.values[i2f][innan])
    acs_out.index.rename('date_time [UTC]', inplace = True)
else:
    innan = np.where(~np.isnan(acs.acs_chl[i2f]))[0]
    acs['acs_chl_debiased'] = acs.acs_chl*(1-delta)
    # acs['acs_chl_debiased'] = acs.acs_chl*(1-delta)
    acs_out = pd.DataFrame(data = {'lat [degN]': acs.uway_lat[i2f][innan],
                                   'lon [degE]': acs.uway_lon[i2f][innan],
                                   'acs_chl_debiased [mg_m3]': acs.acs_chl_debiased[i2f][innan]
                                  }  ,
                          index = acs.time.values[i2f][innan])
    acs_out.index.rename('date_time [UTC]', inplace = True)


# In[61]:


# add attributes to acs_chl_debiased
if 'acx_chl' in acs.keys(): # case with merged acs ac9
    acs.acx_chl_debiased.attrs["debiasing_equation"] = "acs.acx_chl_deiased = acs.acx_chl*(1-delta)"
    acs.acx_chl_debiased.attrs["delta"] = delta
    acs.acx_chl_debiased.attrs["sigma"] = sigma
    acs.acx_chl_debiased.attrs["units"] = "mg/m3"
    acs.acx_chl_debiased.attrs["comments"] = "delta=np.nanmedian(rres), sigma=prcrng(rres), rres=acx_chl/HPLC_Tot_Chl_a-1, based on surface data"
    acs.acx_chl_debiased.attrs["HPLC_Tot_chla"] = df_hplc_acs.Tot_Chl_a.values
    acs.acx_chl_debiased.attrs["HPLC_Tot_chla_units"] = "mg/m3"
    acs.acx_chl_debiased.attrs["acx_chl"] = df_hplc_acs.acx_chl.values
    acs.acx_chl_debiased.attrs["acx_chl_units"] = "mg/m3"
    acs.acx_chl_debiased.attrs["processed_on"] = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    acs.acx_chl_debiased.attrs["match_up_dates"] = df_hplc_acs.index.format()
else: # just acs
    acs.acs_chl_debiased.attrs["debiasing_equation"] = "acs.acs_chl_deiased = acs.acs_chl*(1-delta)"
    acs.acs_chl_debiased.attrs["delta"] = delta
    acs.acs_chl_debiased.attrs["sigma"] = sigma
    acs.acs_chl_debiased.attrs["units"] = "mg/m3"    
    acs.acs_chl_debiased.attrs["comments"] = "delta=np.nanmedian(rres), sigma=prcrng(rres), rres=acs_chl/HPLC_Tot_Chl_a-1, based on surface data"
    acs.acs_chl_debiased.attrs["HPLC_Tot_chla"] = np.array(list(df_hplc_acs.Tot_Chl_a.values)) # issues with d-type; this removes obejct class.
    acs.acs_chl_debiased.attrs["HPLC_Tot_chla_units"] = "mg/m3"    
    acs.acs_chl_debiased.attrs["acs_chl"] = df_hplc_acs.acs_chl.values
    acs.acs_chl_debiased.attrs["acs_chl_units"] = "mg/m3"
    acs.acs_chl_debiased.attrs["processed_on"] = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    acs.acs_chl_debiased.attrs["match_up_dates"] = df_hplc_acs.index.format()
        

# In[62]:


# create new filtered acs dataframe - turned off for AMT-27
#acs2 = acs.reset_index('time') # this is needed only for AMT29

# i2kp = np.where(  (acs.acs_ap[i2f,10][innan]>0) | (np.isreal(acs.ay440))  )[0]         # this removes ay data
# i2kp = np.where((acs2.acs_ap[:,10] > 0)   ) [0]
# i2kp = np.where(  acs.acs_ap[i2f,10][innan]>0  )[0]         # this removes ay data
# ix = xr.DataArray(acs.time[i2f][innan][i2kp], dims=['time'])
# ix = xr.DataArray(acs2.time[i2kp], dims=['time'])
# acs_filtered = acs2.sel(time=ix)


# In[63]:


#acs_filtered2 = acs_filtered
#acs_filtered2 = acs_filtered2.rename_vars({'time_': 'time'}, )


# In[64]:


# plot to check                   
#iwv = np.where(acs_filtered.acs_wv==490)[0]
#fig, [ax, ax2] = plt.subplots(2,1, figsize=(13, 4), sharex=True)

# ax.semilogy(acs_filtered.time_[:], acs_filtered.acs_ap[:,iwv], 'b.', ms=1)
# ax.semilogy(acs_filtered.time_[:], sg.medfilt(x, 151), 'b.', ms=1)
#ax.semilogy(acs_filtered2.time, acs_filtered2.acs_ap[:,iwv], 'ro', ms=1, mfc='none', alpha=0.5)
#ax.grid('on')

#ax2.grid('on')


# In[65]:


# save to file for Silvia
# acs_out.to_csv('AMT29_ACS_chl_debiased.csv')
#acs_filtered2


# In[66]:


# save updated NetCDF file

#acs_filtered2.to_netcdf(DIN_acs+fn_acs[:-3]+'_with_debiased_chl.nc')
#acs_filtered2.close()

acs.to_netcdf(DIN_acs+fn_acs[:-3]+'_with_debiased_chl.nc')
acs.close()


plt.figure()
plt.plot(acs.acs_chl_debiased)

