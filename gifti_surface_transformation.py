""" Apply ANTs generated transformations to vertices of a GIfTI file.

This script allows the user to transform a surface mesh, given as a GIfTI file, 
from one space to another. The code has been used on 3D brain surface 
mesh data. The transforms were generated from registering one 3D brain volume 
(where the surface was defined) to another using the ANTs normalization tools.

Authors:
    Rui Gong, Alexander Woodward - 2023/09/27
"""
import SimpleITK as sitk
import nibabel as nib


def transform_gifti_between_spaces(in_filename, out_filename, affine_tfm, inv_warp_tfm):
    """Transform the vertices in a gifti file from one space to another.

    Parameters:
    in_filename -- the input filename.
    out_filename -- the output filename.
    affine_tfm -- The filename of the affine component of the transform.
    inv_warp_tfm -- The filename of the non-linear warp component of the transform.
    """
    # Data in world coordinate system 1:
    surf = nib.load(in_filename)

    tfm_aff = sitk.ReadTransform(affine_tfm)
    tfm_inv_warp = sitk.DisplacementFieldTransform(
        sitk.ReadImage(inv_warp_tfm))

    # Pass the points through the inverse transformation path:
    t_new = sitk.CompositeTransform([tfm_inv_warp, tfm_aff.GetInverse()])

    for i in range(len(surf.darrays[0].data)):
        v_1 = surf.darrays[0].data[i][0]
        v_2 = surf.darrays[0].data[i][1]
        v_3 = surf.darrays[0].data[i][2]

        # Be careful to account for differences in the anatomical spaces of each dataset
        vnew = (v_1, v_2, v_3)

        vtransform = t_new.TransformPoint(vnew)

        surf.darrays[0].data[i][0] = vtransform[0]
        surf.darrays[0].data[i][1] = vtransform[1]
        surf.darrays[0].data[i][2] = vtransform[2]

    # Data in world coordinate system 2:
    nib.save(surf, out_filename)


if __name__ == "__main__":
    transform_gifti_between_spaces(
        "./input/brain_in_space_1.rh.white.surf.gii",
        "./transforms/tfm_0GenericAffine.mat",
        "./transforms/tfm_1InverseWarp.nii.gz",
        "./output/brain_in_space_2.rh.white.surf.gii",
    )
