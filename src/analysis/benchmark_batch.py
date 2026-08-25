"""Build truthful, replayable payloads for the ML batch benchmark."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import numpy as np

from config.constants import BENCHMARK_EVALUATION_IOU_THRESHOLD
from src.analysis.benchmark_snapshot import sha256_file
from src.analysis.detection_metrics import (
    evaluate_detection_dataset,
    legacy_count_agreement,
    normalize_benchmark_class,
    unavailable_evaluation,
)


METHODS = ("quick_analysis", "deep_analysis", "ml_benchmark")


def _bbox_prediction(feature: Mapping[str, Any], index: int, *, ml: bool) -> Dict[str, Any]:
    bbox = feature.get("bbox_global") if ml else feature.get("bounding_box")
    if bbox is None:
        bbox = feature.get("bounding_box")
    class_value = feature.get("ml_class") if ml else feature.get("shape")
    return {
        "prediction_id": feature.get("source_prediction_id", feature.get("id", index + 1)),
        "class_name": normalize_benchmark_class(class_value) or "Unknown",
        "raw_class": class_value,
        "confidence": float(feature.get("ml_confidence", 1.0)),
        "bbox_xywh": list(bbox) if bbox is not None else None,
    }


def _method_predictions(result: Any, *, ml: bool) -> List[Dict[str, Any]]:
    if ml and getattr(result, "raw_detections", None) is not None:
        return [
            {
                "prediction_id": item.get("prediction_id", index + 1),
                "class_name": normalize_benchmark_class(item.get("class_name")) or "Unknown",
                "raw_class": item.get("class_name"),
                "confidence": float(item.get("confidence", 1.0)),
                "bbox_xywh": list(item.get("bbox_xywh") or []),
            }
            for index, item in enumerate(result.raw_detections)
        ]
    return [
        _bbox_prediction(feature, index, ml=ml)
        for index, feature in enumerate(result.features or [])
    ]


def _features(result_entry: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    return result_entry["result"].features or []


def _distribution(result_entries: Sequence[Mapping[str, Any]], *, ml: bool) -> Dict[str, Any]:
    shapes: Counter = Counter()
    colors: Counter = Counter()
    areas: List[float] = []
    postprocessed = 0
    for entry in result_entries:
        result = entry["result"]
        features = _features(entry)
        postprocessed += len(features)
        if ml:
            for raw in getattr(result, "raw_detections", []) or []:
                label = normalize_benchmark_class(raw.get("class_name")) or "Unknown"
                shapes[label] += 1
        else:
            for feature in features:
                label = normalize_benchmark_class(feature.get("shape")) or "Unknown"
                shapes[label] += 1
        for feature in features:
            colors[str(feature.get("color", "Unknown"))] += 1
            area = feature.get("area")
            if area is not None:
                areas.append(float(area))
    detected_total = sum(shapes.values())
    return {
        "shape_distribution": dict(shapes),
        "color_distribution": dict(colors),
        "area_distribution": areas,
        "color_evaluated_count": postprocessed,
        "detected_total": detected_total,
        "postprocessed_total": postprocessed,
        "color_coverage": postprocessed / detected_total if detected_total else None,
    }


def _ground_truth_distribution(images_data: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    shapes: Counter = Counter()
    colors: Counter = Counter()
    areas: List[float] = []
    for image in images_data:
        for particle in image.get("ground_truth_data") or []:
            shapes[normalize_benchmark_class(particle.get("shape")) or "Unknown"] += 1
            colors[str(particle.get("color_label", "Unknown"))] += 1
            if particle.get("area") is not None:
                areas.append(float(particle["area"]))
    return {
        "shape_distribution": dict(shapes),
        "color_distribution": dict(colors),
        "area_distribution": areas,
    }


def build_ml_batch_payload(
    images_data: Sequence[Mapping[str, Any]],
    results: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    timestamp: str,
    model_path: str,
    confidence_threshold: float,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Return the HTML report payload and its reproducibility evidence."""
    image_ids = [str(image["name"]) for image in images_data]
    ground_truth_sets = [list(image.get("ground_truth_data") or []) for image in images_data]
    errors = [
        f"{image['name']}: {image.get('ground_truth_error')}"
        for image in images_data if image.get("ground_truth_error")
    ]
    declared_total = sum(int(image.get("ground_truth", 0)) for image in images_data)
    parsed_total = sum(len(items) for items in ground_truth_sets)
    if declared_total != parsed_total:
        errors.append(
            f"declared GT total ({declared_total}) differs from parsed bbox total ({parsed_total})"
        )

    prediction_sets: Dict[str, List[List[Dict[str, Any]]]] = {}
    evaluations: Dict[str, Dict[str, Any]] = {}
    legacy: Dict[str, Dict[str, Any]] = {}
    distributions: Dict[str, Dict[str, Any]] = {}
    for method in METHODS:
        ml = method == "ml_benchmark"
        method_sets = [
            _method_predictions(entry["result"], ml=ml)
            for entry in results[method]
        ]
        prediction_sets[method] = method_sets
        legacy[method] = legacy_count_agreement(method_sets, ground_truth_sets)
        evaluations[method] = (
            unavailable_evaluation("; ".join(errors))
            if errors else
            evaluate_detection_dataset(
                method_sets,
                ground_truth_sets,
                image_ids=image_ids,
                iou_threshold=BENCHMARK_EVALUATION_IOU_THRESHOLD,
            )
        )
        distributions[method] = _distribution(results[method], ml=ml)

    ground_truth_average = parsed_total / len(images_data) if images_data else None
    payload: Dict[str, Any] = {
        "timestamp": timestamp,
        "num_images": len(images_data),
        "ground_truth": ground_truth_average,
        "total_ground_truth": parsed_total,
        "evaluation_method": {
            "name": "class-aware one-to-one bbox matching",
            "matching": "confidence-descending greedy",
            "iou_threshold": BENCHMARK_EVALUATION_IOU_THRESHOLD,
            "classes": ["Microbead/Pellet", "Fiber/Filament", "Irregular"],
            "availability": "available" if not errors else "unavailable",
            "unavailable_reasons": errors,
        },
        "ground_truth_distributions": _ground_truth_distribution(images_data),
    }
    for method in METHODS:
        times = [float(entry["time"]) for entry in results[method]]
        method_payload = {
            **distributions[method],
            **evaluations[method],
            "detected": distributions[method]["detected_total"] / len(images_data) if images_data else 0.0,
            "ground_truth": ground_truth_average,
            "processing_time": float(np.mean(times)) if times else 0.0,
            "legacy_count_diagnostic": legacy[method],
        }
        if method == "ml_benchmark":
            method_payload.update({
                "model_name": Path(model_path).name,
                "confidence_threshold": float(confidence_threshold),
            })
        payload[method] = method_payload

    model = Path(model_path).resolve()
    evidence = {
        "run": {
            "timestamp": timestamp,
            "relation_to_pre_fix_baseline": (
                "New inference run using the same dataset/model/config; the pre-fix HTML has no "
                "prediction sidecar, so its predictions cannot be replayed."
            ),
        },
        "inputs": {
            "ordered_images": [
                {
                    "image_id": image["name"],
                    "source_path": image.get("source_path"),
                    "source_sha256": sha256_file(Path(image["source_path"])) if image.get("source_path") else None,
                    "ground_truth_path": image.get("ground_truth_path"),
                    "ground_truth_sha256": sha256_file(Path(image["ground_truth_path"])) if image.get("ground_truth_path") else None,
                }
                for image in images_data
            ],
            "model_path": str(model),
            "model_sha256": sha256_file(model),
            "confidence_threshold": float(confidence_threshold),
            "iou_threshold": BENCHMARK_EVALUATION_IOU_THRESHOLD,
        },
        "evaluation": evaluations,
        "legacy_count_diagnostic": legacy,
        "predictions": {
            method: prediction_sets[method] for method in METHODS
        },
        "ml_lineage": [
            {
                "image_id": image["name"],
                "raw_yolo_predictions": list(getattr(result["result"], "raw_detections", []) or []),
                "postprocessed_features": list(result["result"].features or []),
                "rejected_postprocessing": list(getattr(result["result"], "rejected_detections", []) or []),
            }
            for image, result in zip(images_data, results["ml_benchmark"])
        ],
        "report_payload": payload,
    }
    return payload, evidence
