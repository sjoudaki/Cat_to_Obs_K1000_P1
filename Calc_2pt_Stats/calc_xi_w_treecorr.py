# ----------------------------------------------------------------
# File Name:           calc_xi_w_treecorr.py
# Author:              Catherine Heymans (heymans@roe.ac.uk)
# Description:         short python script to run treecorr to calculate xi_+/- 
#                      given a KiDS fits catalogue
#                      script will need to change if keywords in KIDS cats are updated
# ----------------------------------------------------------------

import treecorr
import sys
import numpy as np
import astropy.io.fits as fits


def subtractNoise(g_1, g_2, eps_1, eps_2):
    g   = g_1 + 1j * g_2
    g_c = g_1 - 1j * g_2
    eps = eps_1 + 1j * eps_2
    
    e = (eps - g) / (1.0 - g_c*eps)
    e = np.array([e.real, e.imag])
    return e

if __name__ == '__main__':
        
    # Read in user input to set the nbins, theta_min, theta_max, lin_not_log, fitscat1, fitscat2, outfilename
    if len(sys.argv) <7: 
        #print("Usage: %s nbins theta_min(arcmin) theta_max(arcmin) lin_not_log? catalogue1.fits \
        #        catalogue2.fits outfilename" % sys.argv[0]) 
        #print "Usage: %s nbins theta_min(arcmin) theta_max(arcmin) lin_not_log(true or false)? \
        #       catalogue1.fits catalogue2.fits outfilename" % sys.argv[0] 
        sys.exit(1)
    else:
        nbins = int(sys.argv[1]) 
        theta_min = float(sys.argv[2]) 
        theta_max = float(sys.argv[3]) 
        lin_not_log = sys.argv[4] 
        fitscat1 = sys.argv[5]
        fitscat2 = sys.argv[6]
        outfile = sys.argv[7]

    # prepare the catalogues

    if 'MFP_galCat' in fitscat1:
        S1_data = fits.getdata(fitscat1, 1)
        S1_RA   = S1_data.field('ALPHA_J2000')
        S1_DEC  = S1_data.field('DELTA_J2000')
        S1_g1   = S1_data.field('g1')
        S1_g2   = S1_data.field('g2')
        S1_eps1 = S1_data.field('e1')
        S1_eps2 = S1_data.field('e2')
        S1_wgt  = S1_data.field('weight')
        
        S2_data = fits.getdata(fitscat2, 1)
        S2_RA   = S2_data.field('ALPHA_J2000')
        S2_DEC  = S2_data.field('DELTA_J2000')
        S2_g1   = S2_data.field('g1')
        S2_g2   = S2_data.field('g2')
        S2_eps1 = S2_data.field('e1')
        S2_eps2 = S2_data.field('e2')
        S2_wgt  = S2_data.field('weight')
        
        if 'obs' in outfile:
            cat1 = treecorr.Catalog(ra=S1_RA, dec=S1_DEC, g1=S1_eps1, g2=S1_eps2, w=S1_wgt, ra_units='deg', dec_units='deg')
            cat2 = treecorr.Catalog(ra=S2_RA, dec=S2_DEC, g1=S2_eps1, g2=S2_eps2, w=S2_wgt, ra_units='deg', dec_units='deg')
        elif 'signal' in outfile:
            cat1 = treecorr.Catalog(ra=S1_RA, dec=S1_DEC, g1=S1_g1, g2=S1_g2, w=S1_wgt, ra_units='deg', dec_units='deg')
            cat2 = treecorr.Catalog(ra=S2_RA, dec=S2_DEC, g1=S2_g1, g2=S2_g2, w=S2_wgt, ra_units='deg', dec_units='deg')
        elif 'noShear' in outfile:
            S1_e = subtractNoise(S1_g1, S1_g2, S1_eps1, S1_eps2)
            S2_e = subtractNoise(S2_g1, S2_g2, S2_eps1, S2_eps2)
            cat1 = treecorr.Catalog(ra=S1_RA, dec=S1_DEC, g1=S1_e[0], g2=S1_e[1], w=S1_wgt, ra_units='deg', dec_units='deg')
            cat2 = treecorr.Catalog(ra=S2_RA, dec=S2_DEC, g1=S2_e[0], g2=S2_e[1], w=S2_wgt, ra_units='deg', dec_units='deg')
        else:
            raise ValueError('Houston, we have a problem.')
        
    else:
        cat1 = treecorr.Catalog(fitscat1, ra_col='ALPHA_J2000', dec_col='DELTA_J2000', ra_units='deg', dec_units='deg', g1_col='e1', g2_col='e2', w_col='weight')
        cat2 = treecorr.Catalog(fitscat2, ra_col='ALPHA_J2000', dec_col='DELTA_J2000', ra_units='deg', dec_units='deg',  g1_col='e1', g2_col='e2', w_col='weight')

    # the value of bin_slop
    fine_binning = True

    if fine_binning:
        # when using fine bins I find this is suitable
        inbinslop = 1.5
    else:
        # when using broad bins it needs to be much finer
        inbinslop = 0.08

    # Define the binning based on command line input
    if(lin_not_log=='true'): 
        gg = treecorr.GGCorrelation(min_sep=theta_min, max_sep=theta_max, nbins=nbins, sep_units='arcmin',\
            bin_type='Linear', bin_slop=inbinslop)
    else: # Log is he default bin_type for Treecorr
        gg = treecorr.GGCorrelation(min_sep=theta_min, max_sep=theta_max, nbins=nbins, sep_units='arcmin', \
            bin_slop=inbinslop)

    ## Linc likes to use only 8 processors
    if 'MFP_galCat' in fitscat1:
        num_threads = 8
    else:
        num_threads = None

    # Calculate the 2pt correlation function
    gg.process(cat1, cat2, num_threads=num_threads)

    # Write it out to a file and praise-be for Jarvis and his well documented code
    gg.write(outfile, precision=12)

