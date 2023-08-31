"""Apply ANTs generated transformations to vertices of a GIfTI file.

This script transforms a surface mesh, given as a GIfTI file, from one space to another. It is specifically designed for 3D brain surface mesh data. The transformations are generated using the ANTs normalization tools.

Authors:
    Rui Gong, Alexander Woodward - 2023/09/27
"""

import SimpleITK as sitk
import nibabel as nib


def transform_gifti_between_spaces(in_filename, out_filename, affine_tfm, inv_warp_tfm):
    """Transform the vertices in a GIfTI file from one space to another.

    Args:
        in_filename (str): The input filename of the GIfTI file.
        out_filename (str): The output filename of the transformed GIfTI file.
        affine_tfm (str): The filename of the affine component of the transform.
        inv_warp_tfm (str): The filename of the non-linear warp component of the transform.

    Returns:
        None

    Example:
        ```python
        transform_gifti_between_spaces(
            "./input/brain_in_space_1.rh.white.surf.gii",
            "./transforms/tfm_0GenericAffine.mat",
            "./transforms/tfm_1InverseWarp.nii.gz",
            "./output/brain_in_space_2.rh.white.surf.gii",
        )
        ```
    """
    # Load the GIfTI file in world coordinate system 1:
    surf = nib.load(in_filename)

    # Read the transformation components:
    tfm_aff = sitk.ReadTransform(affine_tfm)
    tfm_inv_warp = sitk.DisplacementFieldTransform(sitk.ReadImage(inv_warp_tfm))

    # Create the composite transformation:
    t_new = sitk.CompositeTransform([tfm_inv_warp, tfm_aff.GetInverse()])

    # Transform each vertex in the GIfTI file:
    for i in range(len(surf.darrays[0].data)):
        v_1, v_2, v_3 = surf.darrays[0].data[i]

        # Be careful to account for differences in the anatomical spaces of each dataset
        vnew = (v_1, v_2, v_3)

        # Apply the transformation to the vertex:
        vtransform = t_new.TransformPoint(vnew)

        # Update the transformed vertex in the GIfTI file:
        surf.darrays[0].data[i] = vtransform

    # Save the transformed GIfTI file in world coordinate system 2:
    nib.save(surf, out_filename)


if __name__ == "__main__":
    # Example call:
    transform_gifti_between_spaces(
        "./input/brain_in_space_1.rh.white.surf.gii",
        "./transforms/tfm_0GenericAffine.mat",
        "./transforms/tfm_1InverseWarp.nii.gz",
        "./output/brain_in_space_2.rh.white.surf.gii",
    )
