import os
import re

# Mapping from original terms to standardized categories (lowercase for matching)
term_to_category = {
    "mri": "mri techniques & modalities",
    "mri scans": "mri techniques & modalities",
    "magnetic resonance imaging": "mri techniques & modalities",
    "structural mri": "mri techniques & modalities",
    "structural magnetic resonance imaging": "mri techniques & modalities",
    "t2w": "mri techniques & modalities",
    "diffusion mri": "diffusion imaging & features",
    "diffusion magnetic resonance imaging": "diffusion imaging & features",
    "diffusion weighted imaging": "diffusion imaging & features",
    "diffusion model": "diffusion imaging & features",
    "rish feature": "diffusion imaging & features",
    "nadaraya-watson head": "diffusion imaging & features",
    "echo planar imaging": "echo planar imaging & artifacts",
    "reversed phase-encoding": "echo planar imaging & artifacts",
    "susceptibility artifacts": "echo planar imaging & artifacts",
    "distortion correction": "echo planar imaging & artifacts",
    "3d medical images": "3d medical imaging",
    "3d medical imaging": "3d medical imaging",
    "3d deep learning": "3d medical imaging",
    "brain segmentation": "brain segmentation",
    "image segmentation": "medical image segmentation",
    "medical image segmentation": "medical image segmentation",
    "segmentation": "medical image segmentation",
    "segmentation model": "medical image segmentation",
    "cortical surface reconstruction": "cortical surface reconstruction",
    "reconstruction of cortical surface": "cortical surface reconstruction",
    "cortex parcellation": "cortex parcellation",
    "registration": "registration techniques",
    "linear registration": "registration techniques",
    "nonlinear registration": "registration techniques",
    "image synthesis": "image synthesis & inpainting",
    "lesion inpainting tool": "image synthesis & inpainting",
    "neural radiance fields": "neural radiance & view synthesis",
    "view synthesis": "neural radiance & view synthesis",
    "3d reconstruction": "structure-from-motion & volumetric modeling",
    "volumetric reconstruction": "structure-from-motion & volumetric modeling",
    "structure from motion": "structure-from-motion & volumetric modeling",
    "scene representation": "structure-from-motion & volumetric modeling",
    "conditional generative network": "generative models",
    "fondation model": "generative models",
    "deep learning": "general deep learning",
    "convolutional neural network": "cnns & fully convolutional networks",
    "fully convolutional neural networks": "cnns & fully convolutional networks",
    "geometric deep learning": "geometric deep learning",
    "geometric deep neural network": "geometric deep learning",
    "transformer": "transformers & attention models",
    "multiscale transformer decoder": "transformers & attention models",
    "unidirectional causal attention mechanism": "transformers & attention models",
    "vision transformer": "vision transformers",
    "supervised learning": "supervised learning",
    "training": "supervised learning",
    "unsupervised learning": "unsupervised learning",
    "few-shot learning": "few-shot & active learning",
    "active learning": "few-shot & active learning",
    "noisy labels": "label quality & robustness",
    "robust loss": "label quality & robustness",
    "consistency regularization": "consistency regularization techniques",
    "click-based interactive image segmentation": "interactive segmentation methods",
    "interactive 3d image segmentation": "interactive segmentation methods",
    "automatic landmark detection": "automatic landmark detection",
    "alzheimer": "disease-focused imaging",
    "tumor": "disease-focused imaging",
    "dementia": "disease-focused imaging",
    "fetal brain": "developmental brain imaging",
    "children": "developmental brain imaging",
    "neurodevelopmental disorders": "neurodevelopmental disorders",
    "joint label fusion": "atlas-based methods & fusion",
    "multi-atlas": "atlas-based methods & fusion",
    "functional atlas": "functional & nested atlases",
    "nested hierarchy": "functional & nested atlases",
    "freesurfer": "freesurfer & ecosystem tools",
    "workflow manager": "workflow management & platforms",
    "platform": "workflow management & platforms",
    "online platform": "workflow management & platforms",
    "preprocessing": "preprocessing & data sampling",
    "patch-based sampling": "preprocessing & data sampling",
    "python library": "programming libraries & frameworks",
    "pytorch lightning": "programming libraries & frameworks",
    "quality control": "quality assurance & control",
    "quality assurance": "quality assurance & control",
    "calibration": "calibration & standardization",
    "standardization": "calibration & standardization",
    "resolution independence": "resolution & distortion correction",
    "computation and language": "computational vision & language",
    "computer vision and pattern recognition": "computational vision & language",
    "vision–language encoders": "computational vision & language",
    "fairness": "ethics & fairness & societal impact",
    "sensitive attributes": "ethics & fairness & societal impact",
    "computers and society": "ethics & fairness & societal impact",
    "study design": "study design & methodology & scalability",
    "methodology": "study design & methodology & scalability",
    "scalability": "study design & methodology & scalability"
}

# Function to process and update a single QMD file
def process_qmd_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        print(f"Reading: {file_path}")
        yaml_text = file.read()

    # Extract and normalize categories from the original YAML
    original_categories = re.search(r'categories:\s*\[(.*?)\]', yaml_text, re.DOTALL)
    if original_categories:
        items = [i.strip().lower() for i in original_categories.group(1).split(",")]
        new_categories = sorted(set(term_to_category.get(item, item) for item in items))
        new_categories_line = "categories: [" + ", ".join(new_categories) + "]"
        yaml_text = re.sub(r'categories:\s*\[.*?\]', new_categories_line, yaml_text)

    # Save the updated content back to the same file or to a new file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(yaml_text)
    print(f"Processed: {file_path}")

# Root directory containing your QMD files and subfolders
root_folder = "/home/bverreman/Documents/website/Neuro-iX.github.io/journalclub/posts"

# Walk through every directory and subdirectory
for folder_name, subfolders, filenames in os.walk(root_folder):
    for filename in filenames:
        print(f"name: {filename}")
        if filename.endswith('.qmd'):  # Process only .qmd files
            file_path = os.path.join(folder_name, filename)
            process_qmd_file(file_path)
