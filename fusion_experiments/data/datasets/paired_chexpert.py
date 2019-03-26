#
#
#


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import torch
import torch.utils.data
import numpy as np
import pandas as pd

from PIL import Image
from lib.utils import to_torch


__all__ = [
    'PairedCheXpertDataset',
]


def load_studies(root, mode, class_names):
    """
    Load a list of studies.

    Args:
        root        (str):  Path to root directory.
        mode        (str):  One of `train` or `val`.
        class_names (list): List of class names.

    Returns:
        (list): List of items containing:
            patient  (str):      Patient identifier.
            study_id (str):      Study ID for the patient.
            frontal  (str):      Path to frontal image, or None.
            lateral  (str):      Path to lateral image, or None.
            masks    (np.array): [14] binary mask array.
            labels   (np.array): [14] binary label array.
    """
    dataset_df = pd.read_csv(os.path.join(root, '{}.csv'.format(mode)))
    dataset_df = dataset_df.applymap(lambda x: None if x == -1. else x)

    masks = dataset_df[class_names].notnull().as_matrix().astype(np.float32)
    labels = dataset_df.fillna(0)[class_names].as_matrix().astype(np.float32)

    patient_to_studies = {}
    for (index, row) in dataset_df.iterrows():
        _, _, patient, study_id, image_fn = row['Path'].split('/')
        if (patient, study_id) not in patient_to_studies:
            patient_to_studies[(patient, study_id)] = {}
            patient_to_studies[(patient, study_id)]['patient'] = patient
            patient_to_studies[(patient, study_id)]['study_id'] = study_id
            patient_to_studies[(patient, study_id)]['mask'] = masks[index]
            patient_to_studies[(patient, study_id)]['labels'] = labels[index]
            patient_to_studies[(patient, study_id)]['frontal'] = None
            patient_to_studies[(patient, study_id)]['lateral'] = None

        is_frontal = row['Frontal/Lateral'] == 'Frontal'
        image_key = 'frontal' if is_frontal else 'lateral'
        patient_to_studies[(patient, study_id)][image_key] = row['Path']

    return patient_to_studies.values()


class PairedCheXpertDataset(torch.utils.data.Dataset):
    """
    CheXpert dataset with paired images.
    """

    def __init__(self,
                 root,
                 mode,
                 classes,
                 transforms):
        """
        Initialization.

        Args:
            root       (str): Path to root directory.
            mode       (str): One of `train` or `val`.
            transforms (list):
        """
        super(PairedCheXpertDataset, self).__init__()

        self.root = root
        self.transforms = transforms
        self.studies = load_studies(root, mode, classes)

    def _load_image(self, image_fn):
        """
        Load image into memory.

        Args:
            image_fn (str): Path to image.

        Returns:
            (PIL.Image, optional): The image, or None if `image_fn == None`.
        """
        if not image_fn:
            return None

        image_fn = os.path.join(os.path.dirname(self.root), image_fn)
        image = Image.open(image_fn).convert('RGB')
        return image

    def __getitem__(self, index):
        """
        Retrieve data for index.

        Args:
            index (int):

        Returns:
            (dict): Dictionary containing:
                patient  (str):          Patient identifier.
                study_id (int):          Study ID for the patient.
                frontal  (PIL.Image):    Frontal image, or None.
                lateral  (PIL.Image):    Lateral image, or None.
                masks    (torch.Tensor): [14] binary mask array.
                labels   (torch.Tensor): [14] binary label array.
        """
        study = self.studies[index]

        patient = study['patient']
        study_id = study['study_id']
        frontal_image = self._load_image(study['frontal'])
        lateral_image = self._load_image(study['lateral'])
        masks = to_torch(study['mask'])
        labels = to_torch(study['labels'])

        if self.transforms:
            frontal_image = self.transforms(frontal_image)
            lateral_image = self.transforms(lateral_image)

        result = {
            'patient' : patient,
            'study_id': study_id,
            'frontal' : frontal_image,
            'lateral' : lateral_image,
            'mask'    : masks,
            'labels'  : labels,
        }
        return result

    def __len__(self):
        """
        Length of the dataset.
        """
        return len(self.studies)


if __name__ == '__main__':
    class_names = [
        'No Finding',
        'Enlarged Cardiomediastinum',
        'Cardiomegaly',
        'Lung Opacity',
        'Lung Lesion',
        'Edema',
        'Consolidation',
        'Pneumonia',
        'Atelectasis',
        'Pneumothorax',
        'Pleural Effusion',
        'Pleural Other',
        'Fracture',
        'Support Devices'
    ]

    dataset = PairedCheXpertDataset(
        '/home/kelvin.wong/Datasets/CheXpert-v1.0',
        'train',
        class_names,
        None
    )
