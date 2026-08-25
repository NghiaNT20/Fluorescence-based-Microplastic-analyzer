---
title: Hướng dẫn đánh giá benchmark trước và sau chỉnh sửa
description: Quy trình chạy benchmark YOLO có spatial metrics, source-pixel evidence, manifest và hash kiểm chứng
author: Microplastic Analyzer Team
ms.date: 2026-08-24
ms.topic: how-to
keywords:
  - benchmark
  - YOLO26m
  - evidence
  - object detection
estimated_reading_time: 12
---

> [!IMPORTANT]
> Tài liệu này đã được thay bằng bản rút gọn, đúng mục tiêu ban đầu tại
> [BENCHMARK_BEFORE_AFTER_CLEAN.md](BENCHMARK_BEFORE_AFTER_CLEAN.md).
> Các bước source-pixel evidence và fine-tuning bên dưới là công việc tham khảo, chưa cần thực hiện.

## 1. Mục tiêu

Quy trình này tách riêng hai câu hỏi:

1. **Model phát hiện tốt đến đâu?** Đánh giá bằng bounding box, class, IoU và mAP.
2. **Việc sửa benchmark làm thay đổi kết luận ra sao?** So sánh metric cũ dựa trên số lượng với metric mới dựa trên ghép cặp không gian.

Không dùng việc metric tăng sau khi sửa evaluator để kết luận model đã tốt hơn. Model chỉ tốt hơn khi so sánh các model khác nhau trên cùng một bộ dữ liệu, cùng cấu hình và cùng evaluator.

## 2. Trạng thái baseline cũ

Baseline đã chạy:

```text
benchmark_results/ml_benchmark_200images_20260823_232221.html
```

- 200 ảnh, 10.000 đối tượng Ground Truth.
- Model: `src/ml/Yolo26m/best.pt`.
- SHA-256: `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c`.
- 10.179 raw YOLO detections, lệch tổng số lượng `+1,79%`.
- MAE số lượng `1,615` đối tượng/ảnh; RMSE `2,055`.
- Chỉ 35/200 ảnh có số lượng dự đoán bằng đúng Ground Truth.
- Precision/Recall/F1 cũ (`0,975/0,993/0,984`) chỉ là **count-agreement estimate** vì dùng `TP = min(detected, GT)`. Đây không phải TP/FP/FN thật theo vị trí.
- Ground Truth cũ không có bounding box chuẩn nên không thể tính IoU hoặc mAP đáng tin cậy.
- Biểu đồ ML cũ dùng nhãn hình thái hậu xử lý thay cho raw YOLO class, nên phân bố `Fragment=6151` không mô tả đúng đầu ra class của model ba lớp.

Giữ báo cáo này làm **Level A / before baseline** để chứng minh ảnh hưởng của lỗi benchmark; không dùng nó làm kết quả cuối cùng về chất lượng detector.

## 3. Những gì đã được sửa

- Generator lưu `Bounding Box: (x, y, width, height)` lấy trực tiếp từ mask đối tượng gốc.
- Parser đọc bbox vào Ground Truth khi load lại dataset.
- Raw YOLO detection được giữ trước ROI và hậu xử lý.
- Evaluator ghép cặp một-một theo IoU, không cho một prediction khớp nhiều Ground Truth.
- Báo cáo mới có TP, FP, FN theo không gian; Precision, Recall, F1 theo class; confusion matrix; AP@0.50 và mAP@0.50:0.95.
- Ontology có đúng ba class: `Microbead/Pellet`, `Fiber/Filament`, `Irregular`.
- `Fragment` trong dữ liệu sinh được ánh xạ sang `Irregular`; raw prediction tên `Fragment` bị từ chối để tránh âm thầm đánh giá model bốn lớp.
- Biểu đồ ML dùng raw `ml_class`; Quick/Deep vẫn dùng nhãn hình thái heuristic và được ghi chú rõ.
- Nếu GT thiếu bbox, evaluator trả `available=false`; không suy đoán bbox từ Position, Size hoặc Area.
- ML batch tạo một `run_id`, lưu PNG và Ground Truth, reload và verify hash trước khi
  analyzer đầu tiên chạy.
- Sau inference, raw prediction, full-image overlay, contact sheet, model provenance và
  final artifact inventory được seal trong cùng evidence package.
- Snapshot có evidence dùng schema 2 và tham chiếu input/evidence manifest bằng SHA-256;
  snapshot cũ không provenance vẫn giữ schema 1.

## 4. Chuẩn bị môi trường

Tại repo fork:

```powershell
cd D:\ICISE\Fluorescence-based-Microplastic-analyzer
.\venv\Scripts\Activate.ps1
python main.py --system-info
```

Trạng thái kiểm tra ngày 2026-08-24:

- PyTorch `2.5.1+cu121`;
- CUDA Available `True`;
- Ultralytics YOLO `8.4.126`.

Không đổi môi trường, model, confidence threshold hoặc tham số phân tích giữa hai lần chạy cần so sánh.

## 5. Tạo bộ dữ liệu spatial mới

Bộ `batch_20260823_165503` chỉ phù hợp làm baseline cũ vì thiếu bbox. Phải tạo dataset mới bằng code đã sửa:

1. Chạy `python main.py` và load đúng model.
2. Chọn **ML Benchmark Batch** → **Generate Synthetic Images**.
3. Chọn đúng số ảnh cần đánh giá; chạy 10 ảnh trước rồi mới tạo holdout lớn hơn.
4. ML batch tự tạo thư mục `benchmark_results/evidence/<run_id>`.
5. Hệ thống phải báo input đã persist và verify trước khi Quick, Deep hoặc ML chạy.
6. Sau khi hoàn thành, kiểm tra `input_manifest.json`, `verification.json` và
   `package_state.json`.

Đối với **Load Image Folder**, hệ thống copy ảnh vào package theo thứ tự xác định, giữ
source path làm provenance và không thay đổi file nguồn.

Nếu bất kỳ particle nào thiếu bbox hoặc bbox có chiều rộng/chiều cao bằng 0, package vẫn
có thể lưu input nhưng `spatial_visual_evidence_status` phải là `unavailable`; không dùng
dataset đó để công bố spatial metrics.

## 6. Chạy benchmark spatial

1. Load đúng `src/ml/Yolo26m/best.pt` trên UI.
2. Chọn **ML Benchmark Batch** và nguồn ảnh ở Bước 5.
3. Xác nhận input package được verify trước analyzer đầu tiên.
4. Giữ confidence threshold `0.25` và các tham số khác cố định.
5. Chạy thử 10 ảnh. Chỉ tiếp tục 200 ảnh nếu báo cáo có mục **Spatial YOLO Evaluation (Authoritative GT BBox)**.
6. Chạy toàn bộ 200 ảnh.
7. Giữ nguyên report, snapshot và evidence package có cùng `run_id`:

```text
<run_id>.html
<run_id>.benchmark.json
benchmark_results/evidence/<run_id>/
```

Snapshot hợp lệ phải có:

- `status = "spatial-ready"`;
- `spatial_metrics_ready = true`;
- `model.sha256` không rỗng và đúng hash đã khóa;
- đúng 200 phần tử trong `images`;
- mỗi Ground Truth particle có `bounding_box`;
- `report_payload.spatial_evaluation.available = true`.
- `snapshot_schema_version = 2`;
- `evidence_package.verified = true`;
- `evidence_package.status = "complete"`;
- manifest SHA-256 và per-image pixel SHA-256 trùng với file trên disk.

## 7. Pilot source-pixel đã xác minh bằng máy

Run tham chiếu hiện tại:
`ml_benchmark_10images_20260824_205909_c594614e`.

* 10 ảnh, 500 Ground Truth, 500/500 bbox hợp lệ
* Ba class: 170 Microbead/Pellet, 184 Fiber/Filament, 146 Irregular
* Model SHA-256:
  `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c`
* Spatial TP/FP/FN: 286/212/214
* Precision/Recall/F1: 0,574/0,572/0,573
* mAP@0.50: 0,558; mAP@0.50:0.95 nội bộ: 0,199
* Fiber F1: 0,103; Fiber AP@0.50: 0,021
* GT Fiber: 90 ngang, 84 dọc, 10 gần vuông
* Prediction Fiber: 0 ngang, 177 dọc, 9 gần vuông
* Prediction Fiber dọc: 95,2%
* Machine verification: passed, 47 artifacts

![Crop trên source pixels cho thấy GT Fiber ngang nhưng prediction thường dựng dọc](../benchmark_results/diagnostics/ml_benchmark_10images_20260824_205909_c594614e_fiber_actual_pixel_crops/fiber_20_actual_pixel_crops.png)

Figure chọn cố định 10 GT ngang và 10 GT dọc theo manifest, không chọn thủ công. Sidecar
JSON lưu image ID, source path, pixel/file hash, Ground Truth index và crop coordinates.

> [!IMPORTANT]
> Machine integrity và visual inspection bằng AI không thay thế human review. Trước khi
> trình bày chính thức, người trình bày phải cập nhật
> `human_visual_review.json` từ `incomplete` thành kết quả review thực tế cho đủ 10 ảnh.

## 8. Cách đọc kết quả

Ưu tiên metric mới trong mục Spatial YOLO Evaluation:

- **TP/FP/FN**: prediction có khớp đúng một đối tượng thật theo vị trí hay không.
- **Precision**: tỷ lệ prediction có đối tượng thật tương ứng.
- **Recall**: tỷ lệ đối tượng thật được tìm thấy.
- **F1**: cân bằng Precision và Recall.
- **Confusion matrix**: phát hiện đúng vị trí nhưng nhầm class nào.
- **AP@0.50**: chất lượng theo từng class tại IoU 0,50.
- **mAP@0.50:0.95**: tiêu chí chặt hơn, đánh giá cả độ chính xác của bbox.

Precision/Recall/F1 ở summary card vẫn được giữ để đối chiếu lịch sử, nhưng phải ghi là **legacy count-agreement**, không dùng làm kết luận chính.

## 9. Thiết kế so sánh trước/sau

| Yếu tố | Before | After | Cách kiểm soát |
|---|---|---|---|
| Model và SHA-256 | YOLO26m hiện tại | Cùng model | Phải giống nhau |
| Dataset cũ thiếu bbox | Có | Không dùng cho spatial | Chỉ minh họa lỗi cũ |
| Dataset spatial mới | Không có | Có bbox chuẩn | Khóa cho các lần chạy sau |
| Legacy count metrics | Có | Vẫn hiển thị | Chỉ tham khảo |
| One-to-one IoU | Không | Có | Kết quả chính |
| Confusion matrix, AP/mAP | Không | Có | Kết quả chính |

Để đo riêng ảnh hưởng của evaluator, dùng raw predictions trong snapshot mới và tính cả công thức cũ lẫn công thức spatial trên đúng cùng lần inference. Khi đó chênh lệch xuất phát từ cách đánh giá, không phải do model chạy lại khác đi.

## 10. Checklist trình bày

- [ ] Báo cáo before cũ được giữ nguyên.
- [ ] Dataset spatial mới có bbox chuẩn cho mọi đối tượng.
- [ ] Model path, SHA-256, threshold, số ảnh và môi trường được ghi lại.
- [ ] Snapshot sau sửa có trạng thái `spatial-ready`.
- [ ] Legacy count metrics được giải thích là metric có thể làm kết quả đẹp giả tạo.
- [ ] Có TP/FP/FN, per-class Precision/Recall/F1, confusion matrix và mAP mới.
- [ ] Phân biệt rõ lỗi localization với lỗi classification.
- [ ] Không kết luận model cải thiện khi chỉ evaluator được sửa.
- [ ] Evidence package có `verified=true`, `status=complete` và snapshot schema 2.
- [ ] Figure hiển thị object thật và có sidecar truy về image ID cùng hash.
- [ ] Human reviewer đã xác nhận đủ 10/10 ảnh hoặc báo rõ trạng thái chưa hoàn thành.

## 11. Tiêu chí dừng

Không công bố kết quả spatial nếu:

- `spatial_evaluation.available = false`;
- thiếu bbox GT;
- prediction có class ngoài ontology ba lớp;
- model hash hoặc dataset khác giữa các lần so sánh;
- report chỉ có legacy Precision/Recall/F1 mà không có IoU/mAP.
- evidence package thiếu manifest, hash mismatch hoặc `package_state` không phải `complete`;
- tài liệu gọi evidence là human-verified khi `human_visual_review.json` chưa pass.
