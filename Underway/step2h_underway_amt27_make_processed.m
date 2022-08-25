function step2h_underway_amt27_make_processed(first_day, last_day, path_ts, ship_uway_fname)

   % Global variables from step2
   global din
   global proc_dir
   global YYYY

   %din_anc = glob([din '../../Ship_uway/ancillary/' num2str(YYYY) '*']);
   % Get total files saved (uses Surfmetv3; GPS and TSG will have same number of files)
   din_anc = glob([path_ts num2str(YYYY) ship_uway_fname]);

   % Get date and convert to jday
   yr = str2num(cell2mat(din_anc)(:,end-39:end-36));
   mm = str2num(cell2mat(din_anc)(:,end-35:end-34));
   day = str2num(cell2mat(din_anc)(:,end-33:end-32));
   jday = jday(datenum([yr,mm,day]));
   jday_str = num2str(jday);

   fn_saved = glob([din '*mat']);

   istart = find(str2num(jday_str) == str2num(strsplit(fn_saved{first_day}, '_.'){end-1}) );
   istop = find(str2num(jday_str) == str2num(strsplit(fn_saved{last_day}, '_.'){end-1}) );

   disp('Processing ship''s underway data...')

   %for idin = 1:length(din_anc)
   for idin = istart:istop

      disp(din_anc{idin})
      fflush(stdout);

      %if strcmp(din_anc{idin}, '../../data/Underway/saved/../../Ship_uway/ancillary/2016277')
      %    keyboard
      %end%if

      % read ship's underway data
      % Identify the date
      date_str = datestr(datenum([yr(idin),mm(idin),day(idin)]),'yyyymmdd');
      % Load GPS files
      tmp1 = rd_seatech_gga_discovery(date_str);
      %tmp1 = rd_seatech_gga([din_anc{idin} '/seatex-gga.ACO']);
      tmp2 = rd_oceanlogger_discovery(date_str);
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

   end%for

   disp('...done')
   disp(' ')

   endfunction
