"""
Tools to transtlate label studio to yolo format annotations for use with this pipeline:
https://github.com/sovit-123/fastercnn-pytorch-training-pipeline.git
"""

from dataclasses import dataclass
from pathlib import Path
from loguru import logger as log


@dataclass
class YoloLabel:
    class_id: int
    center_x: float
    center_y: float
    width: float
    height: float


def translate_annots_from_json_min_fmt(
    lbl_studio_annots: list[dict[str, object]],
    class_to_id: dict[str, int],
    output_dir: Path,
    label_type: str,
    drop_hash_prefix: bool = True,
):
    log.info(f"output_dir: {output_dir!s}")
    labels_fp = output_dir / "darknet.labels"
    log.info(f"writing class names to `{labels_fp}`:---")

    max_label_idx = max(class_to_id.values())
    id_to_class = {id_: name for name, id_ in class_to_id.items()}

    with labels_fp.open("wt") as f_out:
        for idx in range(1, max_label_idx + 1):
            class_name = id_to_class.get(idx)
            if class_name is None:
                raise ValueError(f"No class for idx={idx} in {class_to_id}")
            log.info(f"{idx} {class_name}")
            print(f"{class_name}", file=f_out)
    log.info("---\n")

    log.info(f"Processing: {len(lbl_studio_annots)} label studio annotations")
    log.info(f"Writing labels to `{labels_fp}`")
    for annot_idx, annot in enumerate(lbl_studio_annots):
        image_fpath = Path(annot['image'])
        log.info(f"annot #{annot_idx}: image_fname: {image_fpath.name}  annot.keys: {list(annot.keys())}")

        image_fname = image_fpath.name
        if drop_hash_prefix:
            # drop first part of filename that is a hash added by label studio
            parts = image_fname.split("-")
            parts = parts[1:]
            image_fname = "-".join(parts)

        yolo_labels = translate_one_annot_from_json_min_fmt(annot, class_to_id, label_type=label_type)
        out_fpath = (output_dir / image_fname).with_suffix(".txt")

        log.info(f"annot #{annot_idx}: writing {len(yolo_labels)} labels in yolo text format to: {out_fpath}")

        with out_fpath.open("wt") as f_out:
            for yolo in yolo_labels:
                print(f"{yolo.class_id} {yolo.center_x} {yolo.center_y} {yolo.width} {yolo.height}", file=f_out)


def translate_one_annot_from_json_min_fmt(
    lbl_studio_annot: dict[str, object],  # One item in the top level list of annotations
    class_to_id: dict[str, int],
    label_type: str = "ellipse"
) -> list[YoloLabel]:
    ret = []

    for class_name, class_id in class_to_id.items():
        if class_name not in lbl_studio_annot:
            print(f"WARNING: class_name=`{class_name}` not found in object with keys: {list(lbl_studio_annot.keys())}")
            continue
        labels = lbl_studio_annot[class_name]

        for label in labels:
            assert label_type == "ellipse", f"label_type={label_type} not supported"

            ret.append(translate_ellipse_label(label, class_id=class_id))

    return ret


def translate_ellipse_label(label: dict[str, float | int], class_id: int) -> YoloLabel:
    assert 'radiusX' in label and 'radiusY' in label and 'rotation' in label, f"label={label}"
    assert label['rotation'] == 0, f"rotation={label['rotation'] != 0} not yet supported"

    return YoloLabel(
        class_id=class_id,
        center_x=label['x'] / 100,
        center_y=label['y'] / 100,
        width=(2 * label['radiusX']) / 100,
        height=(2 * label['radiusY']) / 100
    )
