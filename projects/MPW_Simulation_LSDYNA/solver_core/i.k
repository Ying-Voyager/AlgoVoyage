$# LS-DYNA Keyword file created by LS-PrePost(R) V4.10.8-26Oct2023
$# Created on Jan-7-2025 (09:41:30)
$-----------------------------------------------------------------------------
$
$ Example provided by Iñaki (LSTC)
$
$ E-Mail: info@dynamore.de
$ Web: http://www.dynamore.de
$
$ Copyright, 2015 DYNAmore GmbH
$ Copying for non-commercial usage allowed if
$ copy bears this notice completely.
$
$X------------------------------------------------------------------------------
$X
$X 1. Run file as is.
$X    Requires LS-DYNA MPP R8.0.0 (or higher) with double precision 
$X
$X------------------------------------------------------------------------------
$X------------------------------------------------------------------------------
$X
*KEYWORD
$
$--- EM
$
$ Conductivity of coil
$ Conductivity of flyer
$--- STRUC
$
$--- THERMAL
$
$
$--- EM
$
$ Conductivity of coil
$ Conductivity of flyer
$--- STRUC
$
$--- THERMAL
$
$
$--- EM
$
$ Conductivity of coil
$ Conductivity of flyer
$--- STRUC
$
$--- THERMAL
$
$
$--- EM
$
$ Conductivity of coil
$ Conductivity of flyer
$--- STRUC
$
$--- THERMAL
$
$
$--- EM
$
$ Conductivity of coil
$ Conductivity of flyer
$--- STRUC
$
$--- THERMAL
$
*TITLE
$#                                                                         title
EM Tube expansion
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             PARAMETERS                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*PARAMETER
$#   prmr1      val1     prmr2      val2     prmr3      val3     prmr4      val4
R    T_end1e-4                                                                  
R  dt_plot2e-6                                                                  
$
$--- EM
$
R    em_dt1e-6                                                                  
Iem_bemmtx25                                                                    
Iem_femmtx25                                                                    
$ Conductivity of coil
R em_cond158                                                                    
$ Conductivity of flyer
R em_cond230                                                                    
R   em_res5.96                                                                  
R   em_cap2.0e-7                                                                
R   em_ind230e-6                                                                
R    em_v07.0e9                                                                 
$--- STRUC
$
R struc_dt2e-6                                                                  
Rstruc_ro18.940e-3                                                              
Rstruc_ro22.7e-3                                                                
R  struc_E6.89e10                                                               
R struc_nu0.33                                                                  
Rstruc_sig2.1e8                                                                 
$--- THERMAL
$
R therm_dt5e-5                                                                  
Rtherm_hc1900.e6                                                                
Rtherm_tc1200.e6                                                                
Rtherm_hc2385.e6                                                                
Rtherm_tc2391.e6                                                                
R therm_ti25.                                                                   
*PART
$HWCOLOR COMPS       1      58
$NAME
$#                                                                         title
coil
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         1         1         1         0         0         0         0         0
$
$--- EM
$
$ Conductivity of coil
$ Conductivity of flyer
$--- STRUC
$
$--- THERMAL
$
*PART
$HWCOLOR COMPS       1      58
$NAME
$#                                                                         title
FS2
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         2         1         3         0         0         0         0         0
*PART
$HWCOLOR COMPS       1      58
$NAME
$#                                                                         title
FS1
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         3         1         3         0         0         0         0         0
*PART
$HWCOLOR COMPS       2      19
$NAME
$#                                                                         title
tubeAl
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
         4         1         2         0         0         0         0         0
*INCLUDE
em.k
*INCLUDE
mesh.k
*END
