rsync --dry-run -e ssh -avP --include '*/' --include '*raw.fif' --exclude '*' \
    . jasper@kasga.ilabs.uw.edu:/data06/jasper/bbc


rsync --dry-run -e ssh -avP --include '*/' --include '*.pos' --exclude '*' \
    jasper@kasga.ilabs.uw.edu:/data06/jasper/bbc .
