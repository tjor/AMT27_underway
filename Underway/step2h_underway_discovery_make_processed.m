function step2h_underway_discovery_make_processed(doy, date_str, FUNC_GGA, DIR_GPS, FN_GPS, DIR_ATT, FN_ATT, DIR_DEPTH, FN_DEPTH, DIR_METDATA, FN_METDATA)


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
   din_met = glob([DIR_METDATA date_str FN_METDATA]); %
  
   disp(din_gps{1})
   disp(din_depth{1})
   disp(din_att{1})
  
   disp(din_met{1})

   % Get date and convert to jday
  %  yr = str2num(cell2mat(din_anc)(:,end-39:end-36));
  % mm = str2num(cell2mat(din_anc)(:,end-35:end-34));
   %day = str2num(cell2mat(din_anc)(:,end-33:end-32));
   %jday = jday(datenum([yr,mm,day]));
   %jday_str = num2str(jday);

   % tjor -  I think we can remove, as loop is now done outside function
   % fn_saved = glob([din '*mat']);
   % istart = find(str2num(jday_str) == str2num(strsplit(fn_saved{first_day}, '_.'){end-1}) );
   % istop = find(str2num(jday_str) == str2num(strsplit(fn_saved{last_day}, '_.'){end-1}) );

   disp('Processing ship''s underway data...')

   % tjor -  I think we can remove, as loop is now done outside function
   %for idin = 1:length(din_anc)
   %for idin = istart:istop
    
  
      fflush(stdout);

      %if strcmp(din_anc{idin}, '../../data/Underway/saved/../../Ship_uway/ancillary/2016277')
      %    keyboard
      %end%if

      % read ship's underway data
      % Identify the date

      % date_str = datestr(datenum([yr(1),mm(1),day(1)]),'yyyymmdd');

      % Load GPS files
       tmp1 = rd_seatech_gga_discovery(din_gps{1}, din_att{1}, din_depth{1});
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
