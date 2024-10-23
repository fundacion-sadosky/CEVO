import nnunet
import glob
import os
import nibabel as nib

def predict_all_images(model_path, image_folder_path, output_folder_path):
    # Load the nnU-Net model
    model = nnunet.inference.model_loading.load_model_and_checkpoint_files(model_path, 0)

    # Iterate over all the seg.nii.gz files in the folder
    for image_path in glob.glob(os.path.join(image_folder_path, '*seg.nii.gz')):
        # Load the image
        image = nib.load(image_path).get_fdata()

        # Predict the segmentation
        segmentation = nnunet.inference.predict.predict_simple(image, model, 'cuda', False, False, None)

        # Save the segmentation as a NIfTI file
        output_path = os.path.join(output_folder_path, os.path.basename(image_path))
        nib.save(nib.Nifti1Image(segmentation, None), output_path)