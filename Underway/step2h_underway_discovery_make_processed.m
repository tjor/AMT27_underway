function step2h_underway_discovery_make_processed(doy, date_str, FUNC_GGA, DIR_GPS, FN_GPS, DIR_ATT, FN_ATT, DIR_DEPTH, FN_DEPTH, DIR_TS, FN_SURF, FN_METDATA, FN_LIGHT, DIR_TSG, FN_TSG)


   # The aim of this function is to combine step2h_underway_make_processed (2022 version of processing file)
   # with combine step2h_underway_make_processed
   
   # likely mods:

   % Global variables from step2
   global din
   global proc_dir
   global YYYY

   % din_anc = glob([din '../../Ship_uway/ancillary/' num2str(YYYY) '*']);
   % Get total files saved (uses Surfmetv3; GPS and TSG will have same number of files)
   
   din_gps = glob([DIR_GPS date_str FN_GPS]); % used in GGA function
   din_att = glob([DIR_ATT date_str FN_ATT]);
   din_depth = glob([DIR_DEPTH date_str FN_DEPTH]); %  
   
   din_surf = glob([DIR_TS date_str FN_SURF]); %
   din_met = glob([DIR_TS date_str FN_METDATA]); %
   din_light = glob([DIR_TS date_str FN_LIGHT]); %
   din_tsg = glob([DIR_TSG date_str FN_TSG]); %
  
   disp(din_gps{1})
   disp(din_depth{1})
   disp(din_att{1})
  
   disp(din_surf{1})
   disp(din_met{1})
   disp(din_light{1})
   disp(din_tsg{1})

   disp('Processing ship''s underway data...')

   % Load GPS files
   tmp1 = rd_seatech_gga_discovery(din_gps{1}, din_att{1}, din_depth{1});
   tmp2 = rd_oceanlogger_discovery(din_surf{1}, din_met{1}, din_light{1}, din_tsg{1});
  
   keyboard % note for resuming: this function needs to be cross-referenced with the AMT28 version (i.e. I think we need to copy the time
   %interpolation from there over?)%

       
       keyboard
     % tmp1 = FNC_GPS([din_gps{1} '/' FN_GPS]);

      %tmp1 = FNC_GPS([din_gps{1}])
      %keyboard
      %tmp2 = FNC_METDATA([din_met{1} '/' FN_METDATA]);
      %tmp1 = rd_seatech_gga_discovery(date_str);
      keyboard
      %tmp1 = rd_seatech_gga([din_anc{idin} '/seatex-gga.ACO']);
     % tmp2 = rd_oceanlogger_discovery(date_str);
      %tmp2 = rd_oceanloggerJCR([din_anc{idin} '/oceanlogger.ACO']);

      tmp.time = y0(yr(idin))-1+jday(idin)+[0:1440-1]'/1440; % create daily time vector with one record per minute of the day (24*60=1440)

      %interpolate underway data to one-minute samples
      flds1 = fieldnames(tmp1);
      for ifld1=2:length(flds1) % skips time field
         tmp.(flds1{ifld1}) = nan(size(tmp.time));
         if ~isempty(tmp1.time)
            tmp.(flds1{ifld1}) = interp1(tmp1.time, tmp1.(flds1{ifld1}), tmp.time);
         end%if
      end%for

      flds2 = fieldnames(tmp2);
      for ifld2=2:length(flds2) % skips time field
         tmp.(flds2{ifld2}) = nan(size(tmp.time));
         if ~isempty(tmp2.time)
            tmp.(flds2{ifld2}) = interp1(tmp2.time, tmp2.(flds2{ifld2}), tmp.time);
         end%if
      end%for

      % save underway ship's data to optics file
      savefile = [proc_dir,'proc_optics_amt27_' jday_str(idin,:) '.mat'];
      if (exist(savefile))
         load(savefile);
      end%if

      out.uway = tmp;

      save('-v6', savefile , 'out' );

   %end%for

   disp('...done')
   disp(' ')

   endfunction
