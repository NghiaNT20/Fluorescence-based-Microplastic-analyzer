---
title: YOLO26m Benchmark Correction and Fine-Tuning Evidence
description: Evidence, root-cause analysis, benchmark corrections, and the controlled execution log required before fine-tuning YOLO26m
author: Microplastic Analyzer Team
ms.date: 2026-08-24
ms.topic: reference
keywords:
  - YOLO26m
  - benchmark
  - fine-tuning
  - object detection
  - microplastic
estimated_reading_time: 18
---

> [!IMPORTANT]
> **TẠM DỪNG:** tài liệu này thuộc giai đoạn điều tra/fine-tuning sau khi báo cáo
> benchmark trước/sau đã được chốt. Với mục tiêu hiện tại, chỉ sử dụng
> [BENCHMARK_BEFORE_AFTER_CLEAN.md](BENCHMARK_BEFORE_AFTER_CLEAN.md).

## Tóm tắt quyết định

Trạng thái hiện tại: **chưa bắt đầu fine-tuning**.

Benchmark cũ làm kết quả của model cao giả tạo vì TP, FP và FN được suy ra từ số
lượng đối tượng, không ghép prediction với Ground Truth theo vị trí. Benchmark mới
đã bổ sung bbox Ground Truth chuẩn và matching theo class cộng IoU. Pilot 10 ảnh cho
thấy F1 giảm từ `0,988` theo công thức cũ xuống `0,634` theo spatial evaluation.

Lỗi lớn nhất nằm ở `Fiber/Filament`. Pilot geometry cũ ghi nhận 96,6% bbox prediction
có hướng dọc nhưng không lưu source pixels. Pilot truy xuất mới lưu đủ ảnh và manifest
ghi nhận 95,2% prediction Fiber dọc, không có prediction ngang, trong khi Ground Truth
có 90 bbox ngang và 84 bbox dọc. Ảnh crop trên object thật xác nhận trực quan cùng một
pattern. Đây là evidence đủ mạnh để yêu cầu kiểm tra annotation training trước
fine-tuning, nhưng chưa chứng minh nguyên nhân nằm trong training dataset cũ.

> [!CAUTION]
> Không fine-tune trên dataset chưa được kiểm kê và chưa xác nhận đúng ba class.
> Exporter training hiện vẫn còn cấu hình lịch sử bốn class và nhánh bbox legacy.

## Mục đích và phạm vi

Tài liệu này là nguồn theo dõi duy nhất cho các công việc sau:

* Lưu evidence trước khi thay đổi model
* Mô tả benchmark cũ bị sai ở đâu và ảnh hưởng thế nào
* Ghi lại từng thay đổi benchmark và lý do thay đổi
* Lưu kết quả pilot sau sửa
* Giải thích tại sao có thể cần fine-tuning
* Ghi lại từng bước chuẩn bị, fine-tuning và đánh giá model mới

Tất cả số liệu phải truy ngược được về snapshot, report, model hash hoặc artifact
trong workspace. Giả thuyết phải được ghi là suy luận, không trình bày như fact.

## Nguồn evidence được khóa

| Artifact | Vai trò |
|----------|---------|
| `benchmark_results/ml_benchmark_200images_20260823_232221.html` | Báo cáo benchmark trước sửa |
| `benchmark_results/ml_benchmark_200images_20260823_232221.benchmark.json` | Snapshot 200 ảnh, raw prediction và Ground Truth |
| `benchmark_results/ml_benchmark_10images_20260824_004112.html` | Báo cáo pilot sau sửa |
| `benchmark_results/ml_benchmark_10images_20260824_004112.benchmark.json` | Snapshot spatial-ready của pilot |
| `benchmark_results/diagnostics/ml_benchmark_10images_20260824_004112_fiber_bbox_audit/` | Audit hình học Fiber |
| `benchmark_results/ml_benchmark_10images_20260824_205909_c594614e.html` | Báo cáo pilot có source-pixel evidence |
| `benchmark_results/ml_benchmark_10images_20260824_205909_c594614e.benchmark.json` | Snapshot schema 2 gắn manifest, model hash và từng ảnh |
| `benchmark_results/evidence/ml_benchmark_10images_20260824_205909_c594614e/` | Ảnh, annotation, prediction, overlay và manifest đã verify |
| `benchmark_results/diagnostics/ml_benchmark_10images_20260824_205909_c594614e_fiber_actual_pixel_crops/` | Figure zoom dẫn xuất có sidecar nguồn/hash |
| `yolo26m/args.yaml` | Cấu hình lần train model hiện tại |
| `yolo26m/results.csv` | Metrics theo 200 epoch của lần train hiện tại |
| `yolo26m/labels.jpg` | Phân bố instance và bbox của training labels |
| `yolo26m/train_batch0.jpg` | Mosaic annotation training |
| `src/ml/Yolo26m/best.pt` | Model đang được đánh giá |

Không chỉnh sửa các artifact này. Model mới và dataset mới phải dùng tên, thư mục và
hash riêng.

## Định danh model trước fine-tuning

| Thuộc tính | Giá trị |
|------------|---------|
| Model path | `src/ml/Yolo26m/best.pt` |
| SHA-256 | `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c` |
| Model khởi đầu lịch sử | `yolov8m.pt` |
| Task | Object detection |
| Image size khi train | 640 |
| Epoch đã chạy | 200 |
| Seed | 0 |
| Class | `Microbead/Pellet`, `Fiber/Filament`, `Irregular` |
| Confidence benchmark | 0,25 |

`yolo26m/results.csv` ghi nhận kết quả cao nhất theo mAP@0.50:0.95 tại epoch 198:

| Precision | Recall | mAP@0.50 | mAP@0.50:0.95 |
|-----------|--------|----------|---------------|
| 0,996 | 0,972 | 0,980 | 0,820 |

Các số liệu training này dùng validation labels theo chính sách annotation cũ. Không
so sánh trực tiếp chúng với spatial benchmark mới vì evaluator và bbox policy khác nhau.

## Kiểm kê dataset

### Dataset training của model hiện tại

`yolo26m/args.yaml` trỏ tới đường dẫn ngoài workspace:

```text
/Users/nghiant51/learnAI/Fluorescence-based-Microplastic-analyzer/data/yolo_microplastic_dataset_balanced/microplastic_balanced.yaml
```

Dataset gốc không có trong repo hiện tại. Vì vậy chưa xác nhận được số ảnh train,
validation, test hoặc raw label của từng ảnh.

Artifact `yolo26m/labels.jpg` ghi nhận số instance training:

| Class | Số instance |
|-------|------------:|
| Microbead/Pellet | 1.000 |
| Fiber/Filament | 1.000 |
| Irregular | 1.000 |
| Tổng | 3.000 |

![Phân bố 3.000 training instances và hình học label](../yolo26m/labels.jpg)

> [!WARNING]
> Số ảnh training chính xác hiện là `Unknown`. Không suy ra số ảnh từ tên file trong
> mosaic. Đây là blocker phải giải quyết trước fine-tuning.

### Dataset benchmark trước sửa

| Thuộc tính | Giá trị |
|------------|--------:|
| Số ảnh | 200 |
| Ground Truth mỗi ảnh | 50 |
| Tổng Ground Truth | 10.000 |
| Raw YOLO predictions | 10.179 |
| Ảnh có count chính xác | 35/200 |
| Count MAE | 1,615 |
| Count RMSE | 2,055 |

Ground Truth theo sáu shape nguồn:

| Shape nguồn | Số đối tượng |
|-------------|-------------:|
| Microbead | 1.626 |
| Pellet | 1.667 |
| Fiber | 1.672 |
| Filament | 1.683 |
| Fragment | 1.659 |
| Irregular | 1.693 |
| Tổng | 10.000 |

Sau khi ánh xạ đúng ontology ba class:

| Class đánh giá | Ground Truth | Raw prediction | Sai lệch count |
|----------------|-------------:|---------------:|---------------:|
| Microbead/Pellet | 3.293 | 3.413 | +120 |
| Fiber/Filament | 3.355 | 3.461 | +106 |
| Irregular | 3.352 | 3.305 | -47 |

### Dataset pilot sau sửa

| Thuộc tính | Giá trị |
|------------|--------:|
| Số ảnh | 10 |
| Ground Truth mỗi ảnh | 50 |
| Tổng Ground Truth | 500 |
| GT có bbox hợp lệ | 500/500 |
| Raw YOLO predictions | 500 |
| Ảnh có count chính xác | 3/10 |
| Count MAE | 1,200 |
| Count RMSE | 1,549 |

Ground Truth theo sáu shape nguồn:

| Shape nguồn | Số đối tượng |
|-------------|-------------:|
| Microbead | 115 |
| Pellet | 83 |
| Fiber | 75 |
| Filament | 76 |
| Fragment | 77 |
| Irregular | 74 |
| Tổng | 500 |

Sau khi ánh xạ đúng ontology ba class:

| Class đánh giá | Ground Truth | Raw prediction | Sai lệch count |
|----------------|-------------:|---------------:|---------------:|
| Microbead/Pellet | 198 | 204 | +6 |
| Fiber/Filament | 151 | 148 | -3 |
| Irregular | 151 | 148 | -3 |

![Phân bố Ground Truth ba class của baseline và pilot](../benchmark_results/evidence/yolo26m_finetuning_20260824/dataset_3class_distribution.png)

## Benchmark trước sửa bị gì

### B-01 TP, FP và FN được suy ra từ số lượng

Code legacy tính từng ảnh như sau:

```python
tp = min(detected, gt)
fp = max(0, detected - gt)
fn = max(0, gt - detected)
```

Công thức không kiểm tra prediction và Ground Truth có cùng vị trí, cùng bbox hoặc cùng
class hay không. Nếu một ảnh có 50 Ground Truth và model dự đoán 50 bbox sai hoàn toàn,
công thức vẫn cho `TP=50`, `FP=0`, `FN=0`.

Evidence trên pilot dùng cùng một tập prediction:

| Evaluator | TP | FP | FN | Precision | Recall | F1 |
|-----------|---:|---:|---:|----------:|-------:|---:|
| Legacy count agreement | 494 | 6 | 6 | 0,988 | 0,988 | 0,988 |
| Class-aware IoU ≥ 0,50 | 317 | 183 | 183 | 0,634 | 0,634 | 0,634 |

![Cùng prediction nhưng metric thay đổi theo evaluator](../benchmark_results/evidence/yolo26m_finetuning_20260824/pilot_legacy_vs_spatial_metrics.png)

Ảnh hưởng: F1 legacy cao hơn spatial F1 `0,354` điểm. Kết luận “model đạt gần
99%” không được hỗ trợ bởi localization evidence.

### B-02 Ground Truth cũ không có bbox chuẩn

Dataset 200 ảnh cũ chỉ lưu Position, Size và Area. Snapshot có trạng thái:

```text
status = legacy-captured
spatial_metrics_ready = false
```

Không thể tính IoU hoặc AP đáng tin cậy. Suy đoán bbox từ Area hoặc Size sẽ tạo thêm
một chính sách annotation không có nguồn rõ ràng.

### B-03 Biểu đồ ML dùng morphology sau hậu xử lý

Báo cáo cũ hiển thị phân bố ML:

| Nhãn trên biểu đồ cũ | Count |
|----------------------|------:|
| Fragment | 6.151 |
| Irregular | 3.299 |
| Fiber/Filament | 716 |
| Microbead/Pellet | 13 |

Raw YOLO thực tế lại là:

| Raw YOLO class | Count |
|----------------|------:|
| Microbead/Pellet | 3.413 |
| Fiber/Filament | 3.461 |
| Irregular | 3.305 |

Nguyên nhân: biểu đồ lấy trường `shape` do heuristic morphology sinh ra thay vì
`ml_class` từ YOLO. Vì vậy cột màu tím không thể dùng để đánh giá classification của
model ba class.

![Biểu đồ cũ trộn raw class với morphology heuristic](../benchmark_results/evidence/yolo26m_finetuning_20260824/before_misleading_shape_distribution.png)

### B-04 Ontology không nhất quán

Model có ba class, nhưng code lịch sử còn bốn category:

```text
Microbead/Pellet
Fiber/Filament
Fragment
Irregular
```

Trong benchmark ba class, `Fragment` phải ánh xạ thành `Irregular`. Nếu exporter
training vẫn tạo ID riêng cho Fragment, model và dataset YAML sẽ không cùng ontology.

### B-05 Không có replay evidence đầy đủ

HTML cũ chỉ trình bày số tổng hợp. Trước instrumentation, không có model hash, image
hash, raw YOLO bbox, confidence và Ground Truth theo từng ảnh trong một artifact có
thể replay.

Ảnh hưởng: không phân biệt được kết quả thay đổi do model, dataset, hậu xử lý hay
evaluator.

## Các điểm đã chỉnh sửa trong benchmark

| ID | File | Thay đổi | Lý do |
|----|------|----------|-------|
| C-01 | `src/analysis/ml_benchmark_analyzer.py` | Lưu raw class, confidence và `bbox_xyxy` trước ROI | Tách output model khỏi hậu xử lý |
| C-02 | `src/analysis/benchmark_snapshot.py` | Lưu model hash, image hash, GT, raw prediction và timing | Tạo baseline có thể kiểm tra lại |
| C-03 | `src/data_generation/synthetic_generator.py` | Tạo bbox pixel `xywh` từ binary object mask | Có Ground Truth geometry có nguồn rõ ràng |
| C-04 | `src/data_generation/yolo_exporter.py` | Ưu tiên authoritative bbox khi export | Không ước lượng bbox khi đã có bbox thật |
| C-05 | `src/gui/main_window.py` | Ghi và đọc dòng `Bounding Box` | Bảo toàn bbox khi lưu và load dataset |
| C-06 | `src/analysis/detection_metrics.py` | Matching một-một theo class và IoU | Tính TP, FP, FN spatial thật |
| C-07 | `src/analysis/detection_metrics.py` | Thêm per-class metrics, confusion matrix, AP và mAP | Phân biệt localization và classification |
| C-08 | `src/analysis/report_generator.py` | Gắn nhãn legacy metric và thêm spatial section | Tránh trình bày count metric như detection metric |
| C-09 | `src/gui/main_window.py` | Dùng raw `ml_class` cho biểu đồ ML | Biểu đồ phản ánh output model thật |
| C-10 | `tests/unit/` | Thêm test IoU, ontology, missing bbox, AP và raw capture | Ngăn regression của evaluator |

Legacy Precision, Recall và F1 chưa bị xóa. Chúng được giữ để so sánh lịch sử nhưng
phải được gọi là `legacy count agreement`.

## Validation cho benchmark đã sửa

| Kiểm tra | Kết quả |
|----------|---------|
| Python `compileall` | Passed |
| Unit test | 9/9 passed |
| System info | PyTorch và Ultralytics available, CUDA available |
| Report spatial rendering smoke | Passed |
| Real-model spatial smoke | Passed |
| Pilot snapshot | `spatial-ready` |
| Pilot GT bbox | 500/500 hợp lệ |
| Prediction class ngoài ontology | Không có |

Metric AP hiện dùng tích phân precision-recall nội bộ. Có thể dùng nhất quán cho
before/after trong dự án, nhưng chưa được gọi là COCO mAP chính thức nếu chưa đối chiếu
với evaluator Ultralytics hoặc COCO.

## Kết quả pilot sau sửa

### Kết quả toàn dataset

| TP | FP | FN | Precision | Recall | F1 | mAP@0.50 | mAP@0.50:0.95 |
|---:|---:|---:|----------:|-------:|---:|---------:|--------------:|
| 317 | 183 | 183 | 0,634 | 0,634 | 0,634 | 0,575 | 0,202 |

### Kết quả theo class

| Class | TP | FP | FN | Precision | Recall | F1 | AP@0.50 |
|-------|---:|---:|---:|----------:|-------:|---:|--------:|
| Microbead/Pellet | 158 | 46 | 40 | 0,775 | 0,798 | 0,786 | 0,786 |
| Fiber/Filament | 18 | 130 | 133 | 0,122 | 0,119 | 0,120 | 0,018 |
| Irregular | 141 | 7 | 10 | 0,953 | 0,934 | 0,943 | 0,920 |

Trong 318 cặp khớp theo vị trí, 317 cặp đúng class. Lỗi chính là geometry/localization,
không phải classification ở các đối tượng đã định vị đúng.

## Pilot truy xuất được trên ảnh thật

Run ID: `ml_benchmark_10images_20260824_205909_c594614e`.

### Dataset và tính toàn vẹn

| Thuộc tính | Giá trị |
|------------|--------:|
| Số ảnh | 10 |
| Object mỗi ảnh | 50 |
| Tổng Ground Truth | 500 |
| Microbead/Pellet | 170 |
| Fiber/Filament | 184 |
| Irregular | 146 |
| Class không hợp lệ | 0 |
| Bbox hợp lệ | 500/500 |
| Machine package verification | Passed, 47 artifacts |
| Snapshot schema | 2 |

* Input manifest SHA-256:
  `262d1f08cd82bcdaa1f9b5e17ba84a04b0620fa2f8267d6caeacba6aa8f27a1b`
* Evidence manifest SHA-256:
  `0112181986bf9dd5efcce1bf99cbe18751525c744ac8217779b3b0fa717b2bde`
* Model SHA-256:
  `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c`
* Master seed: `20260824`
* Synthetic parameters chính: 10 ảnh, 50 object/ảnh, `1280 × 1280`, Mixed,
  Fluorescent, blur kernel 15, confidence 0,25

Mỗi ảnh có `image_id`, đường dẫn PNG, annotation path, pixel hash, encoded-file hash,
annotation hash và per-image seed. Snapshot kiểm tra pixel hash của ảnh reload trùng
manifest trước khi được ghi.

### Spatial metrics của pilot truy xuất

| TP | FP | FN | Precision | Recall | F1 | mAP@0.50 | mAP@0.50:0.95 |
|---:|---:|---:|----------:|-------:|---:|---------:|--------------:|
| 286 | 212 | 214 | 0,574 | 0,572 | 0,573 | 0,558 | 0,199 |

Riêng `Fiber/Filament`: TP `19`, FP `167`, FN `165`, Precision `0,102`, Recall
`0,103`, F1 `0,103` và AP@0.50 `0,021`.

Hai pilot dùng sample synthetic khác nhau nên không so sánh trực tiếp từng bbox. Kết
quả mới có giá trị bổ sung: nó tái hiện cùng orientation bias trên một dataset có ảnh
nguồn, manifest và hash đầy đủ.

### Evidence hình ảnh trên object thật

| Hướng | Ground Truth | YOLO prediction |
|-------|-------------:|----------------:|
| Ngang | 90 | 0 |
| Dọc | 84 | 177 |
| Gần vuông | 10 | 9 |

Prediction dọc chiếm `177/186 = 95,2%`. Figure dưới đây chọn cố định 10 GT Fiber ngang
rồi 10 GT Fiber dọc theo manifest ordinal và annotation order. Đây không phải sample
chọn thủ công. Màu xanh là Ground Truth; màu hồng là YOLO prediction.

![Hai mươi crop Fiber trên source pixels cho thấy prediction thường dựng dọc, kể cả khi Ground Truth nằm ngang](../benchmark_results/diagnostics/ml_benchmark_10images_20260824_205909_c594614e_fiber_actual_pixel_crops/fiber_20_actual_pixel_crops.png)

Sidecar truy xuất nguồn:
`benchmark_results/diagnostics/ml_benchmark_10images_20260824_205909_c594614e_fiber_actual_pixel_crops/fiber_20_actual_pixel_crops.json`.

Full-image contact sheet của cả 10 ảnh:

![Mười ảnh pilot thật với GT Fiber màu xanh và YOLO Fiber màu hồng](../benchmark_results/evidence/ml_benchmark_10images_20260824_205909_c594614e/fiber_contact_sheet.png)

> [!IMPORTANT]
> Machine integrity đã pass. `human_visual_review.json` vẫn có trạng thái
> `incomplete`. Hình đã được AI hỗ trợ kiểm tra để phát hiện lỗi hiển thị, nhưng người
> trình bày phải xác nhận 10/10 ảnh trước khi ghi “human-verified” trong báo cáo chính thức.

## Evidence riêng cho Fiber/Filament

### Kết quả hình học

| Chỉ số | Giá trị |
|--------|--------:|
| GT Fiber | 151 |
| Prediction Fiber | 148 |
| One-to-one pairs có giao nhau | 142 |
| GT không có prediction giao nhau | 9 |
| Prediction không ghép được | 6 |
| Khoảng cách tâm trung vị | 0,73 px |
| IoU trung vị | 0,332 |
| Cặp đạt IoU ≥ 0,50 | 18/142 |
| Diện tích prediction/GT trung vị | 0,394 |
| Chiều rộng prediction/GT trung vị | 0,436 |
| Chiều cao prediction/GT trung vị | 0,792 |

Tâm prediction gần như đúng nhưng bbox thường nhỏ hơn GT.

### Evidence hướng bbox

| Hướng | Ground Truth | YOLO prediction |
|-------|-------------:|----------------:|
| Ngang | 74 | 0 |
| Dọc | 66 | 143 |
| Gần vuông | 11 | 5 |

YOLO tạo bbox dọc cho 96,6% Fiber. Trong 142 cặp, 68 cặp có dạng `GT ngang →
prediction dọc`.

![Sơ đồ hai mươi cặp Fiber trên nền trống, chỉ dùng để kiểm tra geometry](../benchmark_results/diagnostics/ml_benchmark_10images_20260824_004112_fiber_bbox_audit/fiber_20_pair_crops.png)

> [!WARNING]
> Figure trên là sơ đồ bbox geometry của pilot cũ, không phải ảnh object và không chứng
> minh image membership. Dùng figure crop source-pixel của pilot truy xuất ở phần trên
> khi trình bày bằng chứng hình ảnh.

### Evidence từ training mosaic

Class 1 trong training mosaic chủ yếu có bbox cao và hẹp theo chiều dọc.

![Training mosaic của model hiện tại](../yolo26m/train_batch0.jpg)

Legacy fallback trong `src/data_generation/yolo_exporter.py` tạo Fiber như sau:

```python
bbox_width = max(size_hint * 0.3, 8)
bbox_height = size_hint * 1.2
```

Công thức không dùng góc quay, nên luôn tạo bbox cao và hẹp.

## Phân loại mức độ chắc chắn của nguyên nhân

### Evidence trực tiếp

* GT Fiber có cả bbox ngang và dọc
* 96,6% prediction Fiber là bbox dọc
* Tâm prediction sai lệch trung vị chỉ 0,73 px
* Training mosaic hiển thị class 1 chủ yếu là bbox dọc
* Source legacy exporter có công thức Fiber luôn dọc
* Training validation cũ báo metric rất cao trên annotation policy cũ

### Suy luận có độ tin cậy cao

Model có khả năng đã học geometry sai hoặc không đầy đủ từ training labels cũ. Điều
này giải thích vì sao model tìm đúng tâm nhưng bbox của Fiber nằm ngang vẫn dựng đứng.

### Chưa được chứng minh

Raw training dataset và label files không có trong workspace. Chưa thể chứng minh model
hiện tại chắc chắn được train trực tiếp bằng đúng nhánh exporter legacy đang thấy trong
source.

Không được thay cụm từ “có khả năng” bằng khẳng định tuyệt đối cho đến khi raw labels
được audit.

## Tại sao có thể cần fine-tuning

Sửa evaluator không thay đổi prediction của model. Nếu bbox chính xác là yêu cầu sản
phẩm, model phải học lại từ annotation đúng để:

* Bao phủ toàn bộ Fiber theo hướng thật
* Cải thiện IoU và AP của Fiber
* Cho phép đo kích thước và diện tích từ bbox
* Không phụ thuộc post-processing phóng to bbox để làm metric đẹp hơn

Không cần fine-tuning nếu mục tiêu duy nhất là đếm hoặc xác định tâm. Khi đó model hiện
tại vẫn có giá trị, nhưng không được dùng bbox để báo cáo kích thước hoặc COCO-style
detection quality.

## Fine-tuning readiness gate

### Evidence đã hoàn thành

* [x] Khóa model path và SHA-256 trước thay đổi
* [x] Lưu baseline 200 ảnh trước sửa
* [x] Lưu raw prediction và snapshot replay evidence
* [x] Sửa benchmark spatial và ghi rõ legacy metric
* [x] Chạy pilot 10 ảnh spatial-ready
* [x] Audit lỗi bbox Fiber bằng số liệu và hình ảnh
* [x] Lưu training args, results, labels plot và mosaic hiện có
* [x] Lưu pilot mới với 10 PNG, 10 annotation, 10 prediction và 10 full overlays
* [x] Khóa input/evidence manifest, image hashes, model hash và snapshot schema 2
* [x] Tạo figure crop source-pixel có selection sidecar, không cherry-pick
* [ ] Người trình bày xác nhận `human_visual_review.json` cho đủ 10/10 ảnh

### Điều kiện chưa hoàn thành

* [ ] Khôi phục hoặc tạo dataset fine-tuning có ảnh lưu trên disk
* [ ] Ghi chính xác số ảnh train, validation và test
* [ ] Ghi chính xác số instance theo mỗi split và mỗi class
* [ ] Khóa ontology exporter đúng ba class
* [ ] Loại bỏ việc dùng bbox legacy cho dataset mới
* [ ] Visual audit ít nhất 50 ảnh annotation trước train
* [ ] Khóa split bằng manifest và hash
* [ ] Lưu dataset YAML và toàn bộ hyperparameter
* [ ] Phê duyệt experiment A từ `best.pt`
* [ ] Chạy fine-tuning
* [ ] Chạy lại pilot và benchmark holdout

Trạng thái gate: **BLOCKED BEFORE TRAINING**.

## Rủi ro còn lại trước fine-tuning

### Exporter vẫn có ontology lịch sử bốn class

`config/constants.py` vẫn chứa cả `Fragment` và `Irregular`. Hàm
`YOLODatasetExporter.get_class_id()` hiện lấy ID theo danh sách này. Dataset dùng để
fine-tuning model ba class có nguy cơ sinh class ID thứ tư hoặc ánh xạ không trùng model.

### Exporter vẫn giữ bbox fallback

Nhánh authoritative bbox đã được thêm, nhưng fallback cũ vẫn tồn tại để tương thích
dataset cũ. Pipeline tạo dataset fine-tuning phải fail nếu thiếu authoritative bbox,
không được tự động rơi về fallback.

### Pilot geometry cũ không lưu source pixels

Snapshot có image hash nhưng không chứa pixel và ảnh PNG không được lưu. Overlay Fiber
hiện tại chỉ chứng minh geometry trên nền trống. Hạn chế này đã được khắc phục cho run
`ml_benchmark_10images_20260824_205909_c594614e`; artifact cũ vẫn giữ nguyên và không
được đổi tên thành image evidence.

### Dataset pilot không phải holdout để ra quyết định cuối

Pilot chỉ có 10 ảnh và 500 objects. Không dùng pilot này để chọn model cuối cùng. Cần
validation/test split độc lập và benchmark holdout đã khóa.

## Nhật ký thực hiện

| Step | Ngày | Trạng thái | Công việc | Kết quả và evidence |
|-----:|------|------------|-----------|---------------------|
| 01 | 2026-08-23 | Completed | Chạy baseline 200 ảnh | Legacy F1 0,984; 10.000 GT; snapshot `legacy-captured` |
| 02 | 2026-08-23 | Completed | Capture raw YOLO và snapshot | Model/image hash, raw bbox, confidence và per-image outputs được lưu |
| 03 | 2026-08-24 | Completed | Thêm authoritative GT bbox | Bbox lấy từ binary object mask và được serialize |
| 04 | 2026-08-24 | Completed | Thêm spatial evaluator | Class-aware one-to-one IoU, confusion matrix, AP và mAP |
| 05 | 2026-08-24 | Completed | Chạy pilot 10 ảnh | Spatial F1 0,634; mAP@0.50 0,575; snapshot `spatial-ready` |
| 06 | 2026-08-24 | Completed | Audit Fiber geometry | 96,6% prediction dọc; center error median 0,73 px |
| 07 | 2026-08-24 | Completed | Tổng hợp evidence trước fine-tuning | Tài liệu và ảnh evidence này được tạo |
| 07A | 2026-08-24 | Completed | Persist/verify evidence trước inference | 10 PNG, 10 annotation, manifest và hashes được khóa trước analyzer |
| 07B | 2026-08-24 | Completed | Chạy pilot source-pixel | F1 0,573; Fiber F1 0,103; 95,2% prediction Fiber dọc; package 47 artifacts verified |
| 07C | 2026-08-24 | Awaiting human review | Visual confirmation | Figure crop và sidecar hoàn thành; `human_visual_review.json` chưa được người trình bày xác nhận |
| 08 | Pending | Blocked | Kiểm kê dataset fine-tuning | Chưa có dataset và split manifest hợp lệ |
| 09 | Pending | Blocked | Sửa pipeline export training ba class | Chờ Step 08 xác định nguồn dataset |
| 10 | Pending | Blocked | Visual audit annotation | Chờ dataset export mới |
| 11 | Pending | Blocked | Fine-tune experiment A từ `best.pt` | Chỉ chạy sau khi readiness gate đạt |
| 12 | Pending | Blocked | So sánh với experiment B từ pretrained base | Chỉ chạy nếu A còn orientation bias |
| 13 | Pending | Blocked | Benchmark holdout và quyết định model | Chờ model candidate và holdout dataset |

## Quy tắc cập nhật cho các bước tiếp theo

Mỗi step phải cập nhật trực tiếp tài liệu này trước khi chuyển sang step kế tiếp. Mỗi
bản ghi phải có:

1. Ngày giờ và trạng thái `Pending`, `In progress`, `Completed` hoặc `Blocked`.
2. Mục tiêu và điều kiện đầu vào.
3. Command hoặc UI action đã thực hiện.
4. Dataset path, số ảnh, số instance/class và split.
5. Model path, parent model hash và output model hash.
6. Hyperparameter hoặc config đã dùng.
7. Output artifact và log path.
8. Validation result, metric và hình ảnh evidence.
9. Quyết định tiếp tục, rollback hoặc dừng.
10. Người review nếu kết quả được dùng để trình bày hoặc công bố.

Mẫu bản ghi:

```markdown
### Step NN: Tên bước

* Date/time:
* Status:
* Objective:
* Input dataset and hash:
* Input model and SHA-256:
* Command/config:
* Output artifacts:
* Validation:
* Metrics:
* Visual evidence:
* Decision:
* Human reviewer:
```

## Bước được phép thực hiện tiếp theo

Step 08 là bước duy nhất được phép bắt đầu: tạo hoặc khôi phục dataset fine-tuning,
kiểm kê số ảnh và số instance theo split/class, sau đó lưu manifest và hash.

Không chạy `model.train()` trước khi Step 08, Step 09 và Step 10 hoàn thành.

## Disclosure và human review

Tài liệu được tổng hợp với hỗ trợ của AI từ source code và artifact trong workspace.
Các kết luận ảnh hưởng đến quyết định fine-tuning, chất lượng model hoặc công bố metric
cần được người phụ trách dự án kiểm tra và phê duyệt.
