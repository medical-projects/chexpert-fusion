#!/bin/bash

cd /home/suo/dev/chexpert-fusion/fusion_experiments
python func_run.py train_baselines \
    --dataset-class PairedOnlyCustomSplit \
    --label-class paper \
    --view frontal \
    --map-unobserved-to-negative \
    --evaluate-once \
    --use-test-set \
    --shuffle \
    --cuda-benchmark \
    --num-gpus 1 \
    --num-epochs 10 \
    --num-workers 16 \
    --train-batch-size 8 \
    --val-batch-size 8 \
    --train-data /home/suo/data/CheXpert-v1.0 \
    --val-data /home/suo/data/CheXpert-v1.0 \
    --outdir /home/suo/experiments/chexpert_test/baseline_frontal_focal_loss \
    --checkpoint /home/suo/experiments/chexpert_train/baseline_frontal_focal_loss/models/model_best.pth.tar \
