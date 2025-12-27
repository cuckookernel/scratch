
https://github.com/sovit-123/fastercnn-pytorch-training-pipeline.git

Commands to be run from repo fastercnn-pytorch-training-pipeline repo!

```bash
# python train.py --data <path to the data config YAML file> \
#    --epochs 10 \
#    --model <model name (defaults to fasterrcnn_resnet50)>\
#    --name <folder name inside output/training/> \
#    --batch 16 \ 
#    --label-type <pascal_voc or yolo>

export MYREPO_DIR="/Users/mrestrepo/git/_personal/scratch"
python train.py --data  $MYREPO_DIR/contar_palmas/fastercnn_pipeline/data_config_20250519.yaml \
    --label-type yolo \
     --epochs 10 \
    --name model_20250519 \
    --batch 16 \
    --disable-wandb \
    --device cpu  # for mac computers only. For actual gpu, remove this option.
```




