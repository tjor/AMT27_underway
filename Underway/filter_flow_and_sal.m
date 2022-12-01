function amt_optics_postQC = filter_flow_and_sal(amt_optics, flow_threshold, sal_threshold)

	% Function to filter-out flow-rate and salinity anomalies (during mQ intervals)
	% Default settings: flow_threshold = 20, sal_threshold = 32
   
        #
	flow = amt_optics.flow;
	sal = amt_optics.ctd.sal;
	
	# apply thresholds
	i_keep = find(flow > flow_threshold & sal > sal_threshold);    # index of data to be kept (not used explictly)
	i_reject = find(flow < flow_threshold | sal < sal_threshold);  # index of data below threhsold (set elements to nan)
	i_nan = find(isnan(flow) == 1 | isnan(sal) == 1);  # index of data where flow or sal are undefined (also set elements to nan)

	# ACS elements to set to NaN 
        amt_optics.acs.chl(i_reject) = NaN;
	amt_optics.acs.ap_u(i_reject,:) = NaN;
	amt_optics.acs.bp(i_reject,:) = NaN;
	amt_optics.acs.bp_u(i_reject,:) = NaN;
	amt_optics.acs.cp(i_reject,:) = NaN;
	amt_optics.acs.cp_u(i_reject,:) = NaN;
        
        amt_optics.acs.chl(i_nan) = NaN;
        amt_optics.acs.ap_u(i_nan,:) = NaN;
	amt_optics.acs.bp(i_nan,:) = NaN;	
	amt_optics.acs.bp_u(i_nan,:) = NaN;
	amt_optics.acs.cp(i_nan,:) = NaN;
	amt_optics.acs.cp_u(i_nan,:) = NaN;
	
        # AC9 elements to set to NaN 
        amt_optics.ac9.chl(i_reject) = NaN;
	amt_optics.ac9.ap_u(i_reject,:) = NaN;
	amt_optics.ac9.bp(i_reject,:) = NaN;
	amt_optics.ac9.bp_u(i_reject,:) = NaN;
	amt_optics.ac9.cp(i_reject,:) = NaN;
	amt_optics.ac9.cp_u(i_reject,:) = NaN;
        
        amt_optics.ac9.chl(i_nan) = NaN;
        amt_optics.ac9.ap_u(i_nan,:) = NaN;
	amt_optics.ac9.bp(i_nan,:) = NaN;	
	amt_optics.ac9.bp_u(i_nan,:) = NaN;
	amt_optics.ac9.cp(i_nan,:) = NaN;
	amt_optics.ac9.cp_u(i_nan,:) = NaN;
	
	
	# bb3 elements to set to NaN  
	amt_optics.bb3.bbp(i_reject,:) = NaN;
        amt_optics.bb3.bbp_err(i_reject,:) = NaN;
    	amt_optics.bb3.bb02(i_reject,:) = NaN;
    	amt_optics.bb3.bb02_err(i_reject,:) = NaN;
    	amt_optics.bb3.bbp_corr(i_reject,:) = NaN;
	amt_optics.bb3.bdgt.X(i_reject,:) = NaN;
	amt_optics.bb3.bdgt.SF(i_reject,:) = NaN;
	amt_optics.bb3.bdgt.C(i_reject,:) = NaN;
	amt_optics.bb3.bdgt.Bw(i_reject,:) = NaN;
	amt_optics.bb3.bdgt.DC(i_reject,:) = NaN;
	amt_optics.bb3.bdgt.WE(i_reject,:) = NaN;
        
        # bb3 elements to set to NaN  
	amt_optics.bb3.bbp(i_nan,:) = NaN;
        amt_optics.bb3.bbp_err(i_nan,:) = NaN;
    	amt_optics.bb3.bb02(i_nan,:) = NaN;
    	amt_optics.bb3.bb02_err(i_nan,:) = NaN;
    	amt_optics.bb3.bbp_corr(i_nan,:) = NaN;
        amt_optics.bb3.bdgt.X(i_nan,:) = NaN;
	amt_optics.bb3.bdgt.SF(i_nan,:) = NaN;
	amt_optics.bb3.bdgt.C(i_nan,:) = NaN;
	amt_optics.bb3.bdgt.Bw(i_nan,:) = NaN;
	amt_optics.bb3.bdgt.DC(i_nan,:) = NaN;
	amt_optics.bb3.bdgt.WE(i_nan,:) = NaN;
        
	# cstar elements to set to NaN 
 	amt_optics.cstar.cp(i_reject) = NaN;
 	amt_optics.cstar.cp_err(i_reject) = NaN;
 	
 	amt_optics.cstar.cp(i_nan) = NaN;
 	amt_optics.cstar.cp_err(i_nan) = NaN;

        # define output var
	amt_optics_postQC = amt_optics;



