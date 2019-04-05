# -*- coding: utf-8 -*-
# @Author: Nuullll
# @Date:   2019-04-03 14:31:23
# @Last Modified by:   Nuullll
# @Last Modified time: 2019-04-03 16:15:45
# @Description: Generates .spikes file for tester c program.

import torch
from torchvision.datasets import MNIST
from torchvision import transforms
from torch.utils.data import Sampler, DataLoader

from random import choice


class SubsetSampler(Sampler):
    """Subset Sampler"""
    def __init__(self, indices):
        self.indices = indices

    def __iter__(self):
        return iter(self.indices)

    def __len__(self):
        return len(self.indices)
        

def load_mnist():
    
    train_set = MNIST('dataset/', train=True, download=True, transform=transforms.Compose([
        transforms.Resize((11, 11)),
        transforms.ToTensor()
    ]))

    test_set = MNIST('dataset/', train=False, download=True, transform=transforms.Compose([
        transforms.Resize((11, 11)),
        transforms.ToTensor()
    ]))

    return train_set, test_set


def subset(dataset, include_labels):

    include_indices = []

    for i, (image, label) in enumerate(dataset):
        if label in include_labels:
            include_indices.append(i)

    return DataLoader(dataset, sampler=SubsetSampler(include_indices))


def normalize(image):
    return image.squeeze() / image.sum()


def generate_spike(image):
    rand = torch.rand_like(image, dtype=torch.float)
    activated = rand <= image

    # choose one activated neuron
    n = activated.sum()
    if n > 1:
        selected_i = choice(range(n))
        activated = activated.view(-1).nonzero()[selected_i].item()
    elif n == 0:
        activated = -1
    else:
        activated = activated.view(-1).nonzero().item()

    return activated


if __name__ == '__main__':
    cats = [0, 1]

    train_set, test_set = load_mnist()
    train_loader = subset(train_set, cats)
    test_loader = subset(test_set, cats)

    for image, label in train_loader:
        generate_spike(normalize(image) / 2)
