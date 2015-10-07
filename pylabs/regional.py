import nibabel


def statsByRegion(image, atlas):
    img = nibabel.load(image)
    atlasImg = nibabel.load(atlas)
    if not img.shape == atlasImg.shape:
        raise ValueError("Input image and atlas must have same dimensions")
