from pylabs.qt1.naming import qt1filepath
from copy import copy
import nibabel, numpy


def matchImages(images, query):
    return [i for i in images if set(query.items()).issubset(set(i.items()))]

def createSpgrTseirCorrespondenceImages(t1images, projectdir):
        spgrQuery = {'method':'orig_spgr_mag', 'b1corr':True}
        spgrImages = matchImages(t1images, spgrQuery)
        for i, spgrImage in enumerate(spgrImages):
            msg = 'Creating SPGR / TSEIR corresp image {0} of {1}'
            print(msg.format(i+1, len(spgrImages)))
            tseirQuery = {'date': spgrImage['date'], 'method':'tseir_mag', 
                'b1corr':False}
            tseirImages = matchImages(t1images, tseirQuery)
            assert len(tseirImages) == 1
            tseirImage = tseirImages[0]
            correspImage = copy(spgrImage)
            correspImage['method'] = 'spgrbytseir'
            spgr = qt1filepath(spgrImage, projectdir, 'BIDS')
            tseir = qt1filepath(tseirImage, projectdir, 'BIDS')
            versus = qt1filepath(correspImage, projectdir, 'BIDS')
            spgrImg = nibabel.load(spgr)
            tseirImg = nibabel.load(tseir)
            correspondence = spgrImg.get_data()/tseirImg.get_data()
            ## get rid of divide-by-zero nans
            correspondence = numpy.nan_to_num(correspondence)
            newImg = nibabel.Nifti1Image(correspondence, spgrImg.get_affine())
            nibabel.save(newImg, versus)
            t1images.append(correspImage)









