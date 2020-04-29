#!/bin/bash

nlens=5                              # How many bins the lenses are divided into 
SOURCE_TYPE="K1000"                  # K1000 or MICE2_KV450
LENS_TYPE="BOSS_data"                # BOSS_data or MICE2_BOSS/MICE2_GAMA

                                     # ONLY USED FOR ANALYSIS WITH MICE
Realisation="Fid"                    # Which MICE realisation to use?
                                     # "Fid" is the single 343sqdeg realisation 
Mag_OnOff="on"                       # only used if SOURCE_TYPE is MICE2_KV450
Pz="Estimated"                       # only used if SOURCE_TYPE is MICE2_KV450

                                     # ONLY USED FOR ANALYSIS WITH K1000
SOMFLAGNAME="noDEEP2"                # The type of SOM used TO ESTIMATE n(Z)
BLIND="A"                            # Which Blind to use


if [ "$SOURCE_TYPE" == "K1000" ]; then
    OUTDIR=Dls_over_Ds_data/SOURCE-${SOURCE_TYPE}_LENS-${LENS_TYPE}
elif [ "$SOURCE_TYPE" == "MICE2_KV450" ]; then

    if [ "$Realisation" == "Fid" ]; then
	OUTDIR=Dls_over_Ds_data/SOURCE-${SOURCE_TYPE}_LENS-${LENS_TYPE}_Pz${Pz}_mag${Mag_OnOff}
    elif [ "$Realisation" == "Octant" ]; then
	OUTDIR=Dls_over_Ds_data/SOURCE-${SOURCE_TYPE}_LENS-${LENS_TYPE}_Pz${Pz}_mag${Mag_OnOff}_Octant
    else
        echo "Realisation must be set to Fid or Octant. Currently it's set to $Realisation. EXITING."
        exit
    fi
	
fi
    
if [ ! -d ${OUTDIR} ]; then
    mkdir -p $OUTDIR
fi

    
JZBIN=1
for tomochar in 01t03 03t05 05t07 07t09 09t12
do
    if [ "$SOURCE_TYPE" == "K1000" ]; then
	# This is the old DIR-Estimated n(z)
	#source_nofz=/home/cech/public_html/KiDS/KiDS-VIKING-450/BLINDED_NZ/KiDS_2018-07-26_deepspecz_photoz_10th_BLIND_specweight_1000_4_ZB${tomochar}_blind${BLIND}_Nz.asc
	# This is the new SOM-Estimated n(z)
	source_nofz=/disk09/KIDS/K1000_TWO_PT_STATS/SOM_NofZ/K1000_NS_V1.0.0A_ugriZYJHKs_photoz_SG_mask_LF_svn_309c_2Dbins_DIRcols_${SOMFLAGNAME}_blind${BLIND}_TOMO${JZBIN}_Nz.fits
	LENS_DIR=LENSCATS/${LENS_TYPE}/
	
    elif [ "$SOURCE_TYPE" == "MICE2_KV450" ]; then

	if [ "$Realisation" == "Fid" ]; then
	    source_nofz=/home/bengib/MICE2_Mocks/MICE2_KV450/nofz_CATS_Pz${Pz}/Nz_mag${Mag_OnOff}_120bins_${tomochar}.asc
	    LENS_DIR=LENSCATS/${LENS_TYPE}_mag${Mag_OnOff}/
	else
	    source_nofz=/home/bengib/MICE2_Mocks/MICE2_KV450/nofz_CATS_Pz${Pz}_Octant/Nz_mag${Mag_OnOff}_120bins_${tomochar}.asc
	    LENS_DIR=LENSCATS/${LENS_TYPE}_mag${Mag_OnOff}_Octant/
	fi
	
    fi
    
 
    for IZBIN in 1 2 3 4 5 
    do
	echo "----- Running Dls_over_Ds.py with Source bin $JZBIN, Lens bin $IZBIN -----"
	specz_fitsfile=${LENS_DIR}/lens_cat_${nlens}Z_${IZBIN}.fits
        outfile=${OUTDIR}/Dls_over_Ds_DIR_6Z_source_${JZBIN}_${nlens}Z_lens_${IZBIN}.asc
        python Dls_over_Ds.py $specz_fitsfile $source_nofz > $outfile
    done
    JZBIN=$[$JZBIN +1]
done

