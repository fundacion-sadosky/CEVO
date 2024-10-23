import os
import subprocess
import nibabel as nib
import numpy as np

from nibabel.processing import conform
from pyrobex.robex import robex

def save_standarized(image, filename):
    data = image.get_fdata()
    data = data.astype(np.int16)
    
    standarized_image = nib.Nifti1Image(data, affine=np.eye(4))
    
    nib.save(standarized_image, filename)
    
def do_conform(path_to_file, output_file, order=3):
    img = nib.load(path_to_file)
    conformed_img = conform(img, out_shape=(240, 240, 155), voxel_size=(1.0, 1.0, 1.0), order=order)
    save_standarized(conformed_img, output_file)
    
def run_flirt_with_conform(input_dir, brainstrip = False):
    sequence_files = []
    t1gd_files = []
    seg_files = []
    
    output_dir = os.path.join(input_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Classify the input files according to whether it is a t1gd file (0001), sequence file (0000, 0002, 0003)
    # or seg file (seg).
    for root, _, files in os.walk(input_dir):
        if not 'output' in root:
            for file in files:
                    if file.endswith(("0000.nii.gz", "0002.nii.gz", "0003.nii.gz",)):
                        sequence_files.append(os.path.join(root, file))
                    elif file.endswith("0001.nii.gz"):
                        t1gd_files.append(os.path.join(root, file))
                    elif file.endswith("seg.nii.gz"):
                        seg_files.append(os.path.join(root, file))

    print("Conforming all T1GD files ...")
    
    # Apply the conform to the '0001' files (t1gd) files.
    for f in t1gd_files:
        output_t1gd_filename = f.replace(os.path.split(f)[0], output_dir)
        do_conform(f, output_t1gd_filename, order=3)
        
    print("Conforming all Seg files ...")

    # Apply the conform to the 'seg' files and change its name to 
    for f in seg_files:
        bname = os.path.split(os.path.split(f)[0])[1]
        output_seg_filename = os.path.join(output_dir, bname + "_seg.nii.gz")
        do_conform(f, output_seg_filename, order=0)

    # Register every other sequence to the conformed t1gd
    print("Registering sequence files...")
    
    # Sequence files to be registered
    sequence_files = ["0000.nii.gz", "0002.nii.gz", "0003.nii.gz"]

    for f in t1gd_files:
        # get the conformed_filename that will be used as reference
        reference_filename = f.replace(os.path.split(f)[0], output_dir)
        
        # suffix of files that will be registered to the reference

        for sequence_file in sequence_files:
            input_filename = f.replace("0001.nii.gz", sequence_file)
            output_filename = input_filename.replace(os.path.split(input_filename)[0], output_dir)
            mat_filename = output_filename.replace(sequence_file, sequence_file.replace(".nii.gz","_mat"))
            cmd = f"flirt -in {input_filename} -ref {reference_filename} -out {output_filename} -omat {mat_filename} -dof 12 -cost mutualinfo -interp trilinear"
            print("Processing command: ")
            print(cmd)
            
            subprocess.run(cmd, shell=True, check=True)
            
            # Re-open the registered image and re-save it with the same name with a standarized header
            aux_img = nib.load(output_filename)
            save_standarized(aux_img, output_filename)

    if brainstrip:
        print("Brainstripping all sequence files and the segmentation file...")
        
        # Add the segmentation file so that it is also stripped
        sequence_files_strip = sequence_files + ["seg.nii.gz"]
        
        for f in t1gd_files:
            t1gd_filename = f.replace(os.path.split(f)[0], output_dir)
            print("Running Robex for : " + t1gd_filename)
            # Load the image and run robex
            image = nib.load(t1gd_filename)
            stripped, mask = robex(image)
            
            # Get the data array from the mask to be applied as a mask to the rest of the sequences
            mask_data = mask.get_fdata()
            # Save the mask file
            mask_filename = t1gd_filename.replace("0001.nii.gz", "brainmask.nii.gz")
            save_standarized(mask, mask_filename)
            
            
            # Save the T1GD stripped file with the suffix stripped_0001.nii.gz
            save_standarized(stripped, t1gd_filename.replace("0001.nii.gz", "stripped_0001.nii.gz"))
 
            # For every sequence 0000, 0002, 0003 and the seg file
            for sequence_file in sequence_files_strip:
                
                print("Stripping sequence : " + str(sequence_file))
                input_filename = t1gd_filename.replace("0001.nii.gz", sequence_file)
                sequence_img = nib.load(input_filename)
                data = sequence_img.get_fdata()
                
                sequence_img_data = data.copy()
                sequence_img_data[mask_data == 0] = 0
                
                stripped_image = nib.Nifti1Image(sequence_img_data, sequence_img.affine, sequence_img.header)
                
                # Writte the stripped file
                stripped_sequence_filename = t1gd_filename.replace("0001.nii.gz", "stripped_" + sequence_file)
                save_standarized(stripped_image, stripped_sequence_filename) 

run_flirt_with_conform('/home/amatys/code/data/glioma_alto_original', brainstrip=True)