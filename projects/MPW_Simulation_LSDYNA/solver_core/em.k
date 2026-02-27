$# LS-DYNA Keyword file created by LS-PrePost(R) V4.10.8-26Oct2023
$# Created on Jan-7-2025 (09:41:30)
$-----------------------------------------------------------------------------
$X------------------------------------------------------------------------------
$X------------------------------------------------------------------------------
$X
*KEYWORD
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             STUC CONTROL                                     $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*CONTROL_SOLUTION
$$    SOLN
$#    soln       nlq     isnan     lcint     lcacc     ncdcf     nocop
         0         0         0       100         0         1         0
*CONTROL_TERMINATION
$$  ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
$#  endtim    endcyc     dtmin    endeng    endmas     nosol
8.00000E-5         0       0.0       0.0       0.0         0
*CONTROL_TIMESTEP
$$  DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS      LCTM     ERODE     MSIST
$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st
1.00000E-7       0.1         0       0.0       0.0         0         0         0
$#  dt2msf   dt2mslc     imscl    unused    unused     rmscl     emscl      ihdo
       0.0         0         0                           0.0       0.0         0
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             STUC OUTPUT                                      $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*DATABASE_GLSTAT
$#      dt    binary      lcur     ioopt
1.00000E-6         3         0         1
*DATABASE_MATSUM
$#      dt    binary      lcur     ioopt
1.00000E-6         3         0         1
*DATABASE_BINARY_D3PLOT
$#      dt      lcdt      beam     npltc    psetid
1.00000E-6         0         0         0         0
$#   ioopt      rate    cutoff    window      type      pset
         1       0.0       0.0       0.0         0         0
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             STRUC BOUNDARY                                   $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*BOUNDARY_SPC_SET
$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz
         4         0         1         1         1         1         1         1
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             STUC MAT                                         $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*MAT_RIGID_TITLE
coil
$#     mid        ro         e        pr         n    couple         m     alias
         1     0.0099.70000E10       0.3       0.0       0.0       0.0          
$#     cmo      con1      con2
       1.0         7         7
$#lco or a1        a2        a3        v1        v2        v3
       0.0       0.0       0.0       0.0       0.0       0.0
*MAT_SIMPLIFIED_JOHNSON_COOK_TITLE
flyer
$#     mid        ro         e        pr        vp
         2    0.00276.90000E10      0.33       0.0
$#       a         b         n         c    psfail    sigmax    sigsat      epso
3.240000E81.141000E8      0.42     0.0021.00000E171.00000E281.00000E28       1.0
*MAT_RIGID_TITLE
FS
$#     mid        ro         e        pr         n    couple         m     alias
         3    0.00276.90000E10      0.33       0.0       0.0       0.0          
$#     cmo      con1      con2
       1.0         7         7
$#lco or a1        a2        a3        v1        v2        v3
       0.0       0.0       0.0       0.0       0.0       0.0
*SECTION_SOLID
$#   secid    elform       aet    unused    unused    unused    cohoff   gaskeit
         1         1         0                                     0.0       0.0
*DEFINE_CURVE
$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint
         1         01.50000E-6   1000000       0.0       0.0         0         0
$#                a1                  o1
                 0.0               4.222
                 1.0                8.62
                 2.0              23.299
                 3.0              44.045
                 4.0              67.344
                 5.0              89.536
                 6.0             113.935
                 7.0             133.205
                 8.0             154.297
                 9.0             169.714
                10.0             185.316 
                11.0             201.833
                12.0             211.368
                13.0             220.165
                14.0             228.623
                15.0             228.992
                16.0             228.992
                17.0             228.992
                18.0             220.719
                19.0             211.737
                20.0             202.018
                21.0             185.678
                22.0             169.345
                23.0             151.552
                24.0             132.474
                25.0             113.012
                26.0              91.182
                27.0              70.097
                28.0              48.428
                29.0              26.606
                30.0               6.236
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             EM CONTROL                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_CONTROL
$#   emsol     numls   macrodt   dimtype    nperio         -   ncylfem   ncylbem
         1         0       0.0         0         2                   1         1
*EM_CONTROL_TIMESTEP
$#  tstype    dtcons      lcid    factor     tsmin     tsmas     rlcsf    mecats
         11.00000E-7         1       1.0       0.0       0.0        25         0
*EM_CIRCUIT_ROGO
$ #  rogoid     setid   settype    curtyp
$#  rogoid     setid   settype    curtyp
         1         1         1         1
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             EM SOLVER                                        $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_SOLVER_BEM
$#  reltol    maxite     stype    precon   uselast  ncyclbem
1.00000E-6      1000         2         2         1      5000
*EM_SOLVER_FEMBEM
$#  reltol    maxite    forcon
1.00000E-4       200         0
*EM_SOLVER_FEM
$#  reltol    maxite     stype    precon   uselast  ncyclfem
     0.001       200         1         1         1      5000
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             EM OUTPUT                                        $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8 
*EM_OUTPUT
$#    mats      matf      sols      solf      mesh       mem    timing
         2         2         2         2         0         0         0
*EM_DATABASE_CIRCUIT
$#   outlv     dtout
         1       0.0
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             EM MAT and EOS                                   $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_MAT_001
$#     mid     mtype     sigma     eosid    unused  eplambda    deatht   rdltype
         1         2      58.0         0                 0.0       0.0         1
*EM_MAT_001
$#     mid     mtype     sigma     eosid    unused  eplambda    deatht   rdltype
         2         4      23.0         0                 0.0       0.0         1
*EM_MAT_001
$#     mid     mtype     sigma     eosid    unused  eplambda    deatht   rdltype
         3         4      23.0         0                 0.0       0.0         1
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$                                                                              $
$                             EM CIRCUIT                                       $
$                                                                              $
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
*EM_CIRCUIT
$#  circid   circtyp      lcid       r/f       l/a      c/t0        v0        t0
         1         1         1      5.962.03000E-42.00000E-78.999999E9       0.0
$# sidcurr    sidvin   sidvout    partid
         0         1         2         0
*END
