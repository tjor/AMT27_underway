function tmp = rd_seatech_gga_discovery(fn_gps, fn_att, fn_depth);
   # Function reads & combines meta data from 3 different files (gps, att, depth) into a single stucture: tmp
 
   # This function was modfied by tjor (Aug 2022) - key changes:
   # (i) function takes 3 separate filenames as input arguement
   # (ii) internal loops removed (previously function acted on set of files for cruise). Note: loops just act on element 1,
   # but keeps previous snytax to avoid any errors.
    
    
   pkg load netcdf
 
   # 1) gps
   for inc = 1:1 % note - this loops over one file 
       ncfile = fn_gps;
       if inc == 1
        
           % Time must be first element of tmp!!!
           % (otherwise error in step2h_underway_amt27_make_processed.m)
           % Assumes time is in dats (matlab format)
           tmp.time = ncread(ncfile,'time')+datenum([1899,12,30,0,0,0]);

           tmp.long = ncread(ncfile,'long');
           tmp.lat = ncread(ncfile,'lat');
           tmp.gndcourse = ncread(ncfile,'gndcourse'); % Course (dir ship is moving)
           tmp.heading = ncread(ncfile,'heading');     % Heading (dir ship is pointing)
           tmp.gndspeed = ncread(ncfile,'gndspeed');   % Ground speed
       else
           _time = ncread(ncfile,'time')+datenum([1899,12,30,0,0,0]);
           % Add a NaN between the two series (so that interpolation leaves a gap)
           midtime = (_time(1)-tmp.time(end))/2;
           tmp.time = [tmp.time; tmp.time(end)+midtime; _time];
           tmp.long = [tmp.long; NaN; ncread(ncfile,'long')];
           tmp.lat = [tmp.lat; NaN; ncread(ncfile,'lat')];
           tmp.gndcourse = [tmp.gndcourse; NaN; ncread(ncfile,'gndcourse')];
           tmp.heading = [tmp.heading; NaN; ncread(ncfile,'heading')];
           tmp.gndspeed = [tmp.gndspeed; NaN; ncread(ncfile,'gndspeed')];
       endif
   endfor


   # 2) att 
   for inc = 1:1
       ncfile = fn_att;
       if inc == 1
           timeatt = ncread(ncfile,'time')+datenum([1899,12,30,0,0,0]);
           tmp.roll = ncread(ncfile,'roll');
           tmp.pitch = ncread(ncfile,'pitch');
           tmp.heave = ncread(ncfile,'heave'); 
       else
           _time = ncread(ncfile,'time')+datenum([1899,12,30,0,0,0]);
           % Add a NaN between the two series (so that interpolation leaves a gap)
           midtime = (_time(1)-timeatt(end))/2;
           timeatt = [timeatt; timeatt(end)+midtime; _time];
           % Add a NaN between the two series (so that interpolation leaves a gap)
           tmp.roll = [tmp.roll; NaN; ncread(ncfile,'roll')];
           tmp.pitch = [tmp.pitch; NaN; ncread(ncfile,'pitch')];
           tmp.heave = [tmp.heave; NaN; ncread(ncfile,'heave')];
       endif
   endfor

   % Interpolate ATT variables to GPS (not on same time)
   tmp.roll = interp1(timeatt,tmp.roll,tmp.time);
   tmp.pitch = interp1(timeatt,tmp.pitch,tmp.time);
   tmp.heave = interp1(timeatt,tmp.heave,tmp.time);

   # 3) depth
   for inc = 1:1
       ncfile = fn_depth;
       if inc == 1
           tt = ncread(ncfile,'time');
           timed = ncread(ncfile,'time')+datenum([1899,12,30,0,0,0]);
           tmp.depthm = ncread(ncfile,'depthm');
       else
           _time = ncread(ncfile,'time')+datenum([1899,12,30,0,0,0]);
           % Add a NaN between the two series (so that interpolation leaves a gap)
           midtime = (_time(1)-timed(end))/2;
           timed = [timed; timed(end)+midtime; _time];
           % Add a NaN between the two series (so that interpolation leaves a gap)
           tmp.depthm = [tmp.depthm; NaN; ncread(ncfile,'depthm')];
       endif
   endfor
   % Interpolate ATT variables to GPS (not on same time)
   % need to remove nans from timed
   igood = find(~isnan(timed));
   tmp.depthm = interp1(timed(igood),tmp.depthm(igood),tmp.time);


   %    % this is to deal with change in format through the cruise ?? tjor: maybe check with GrG?
   %    if length(tmp.time==1)
   %
   %        fmt = "%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,,\n";
   %
   %        fid = fopen(fn, "r");
   %
   %            d = fscanf(fid, fmt, [11, Inf])'; 
   %       
   %        fclose(fid);   
   %
   %
   %        tmp.time = y0(d(1))-1+d(:,2);
   %
   %        tmp.lat = d(:,6); % [degN]
   %        tmp.lon = d(:,7); % [degE]
   %            
   %
   %
   %    end%if

   endfunction
