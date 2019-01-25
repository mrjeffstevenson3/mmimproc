* convert phantom parrec B1, SPGR, IRs etc to single slice MNI. should be done on SDM server to download
* model_pipeline *Determines expected T1 values. stays local. How do we update new temps??

* collect_gilad_phantoms *Moves Todds gilad-fitted phantom files

* fitting_phantoms *operates on pickle file created by phantom convert OR collect_gilad_phantoms
    * replace sdm rootfs with local rootfs
* coregister_phantoms
* atlassing (phantoms) generates tsv data for correction factors by date, method, vial

* brain_fitting glob of subj dirs for SPGRs
* correction_brains
    * work on saturation recovery correction factor and apply

