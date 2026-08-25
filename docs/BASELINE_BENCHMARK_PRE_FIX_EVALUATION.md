# Đánh giá benchmark trước khi chỉnh sửa

## 1. Kết luận trình bày ngắn

Baseline cũ **không đủ điều kiện để kết luận model YOLO26m có F1 = 0,984**. Con số này chỉ đo mức độ gần nhau giữa **tổng số prediction** và **tổng số Ground Truth (GT)** trên từng ảnh; nó không kiểm tra prediction có đúng object, đúng vị trí bbox hay đúng class hay không.

Trên cùng một snapshot gồm 10.157 prediction đã được pipeline ML cũ chấp nhận:

| Cách đánh giá | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Benchmark cũ: chỉ so số lượng | 9.914 | 243 | 86 | 0,9761 | 0,9914 | **0,9837** |
| Matching đúng class + IoU ≥ 0,50 | 5.298 | 4.859 | 4.702 | 0,5216 | 0,5298 | **0,5257** |
| Chênh lệch do evaluator | −4.616 TP | +4.616 FP | +4.616 FN | −0,4545 | −0,4616 | **−0,4580** |

Như vậy F1 cũ bị phóng đại **45,80 điểm phần trăm**. Có 4.616 prediction được công thức đếm gán là TP dù không ghép được với GT cùng class tại IoU 0,50.

![So sánh metric cũ và metric bbox](../benchmark_results/evidence/pre_fix_baseline_20260825_001406/legacy_vs_spatial_metrics.png)

## 2. Phạm vi và provenance

### Baseline do người dùng chạy

| Thuộc tính | Giá trị |
|---|---|
| Report | `benchmark_results/ml_benchmark_200images_20260825_001406.html` |
| SHA-256 report | `bccf6444759e4199221c264f418ddc134f00c4976109c0aec165ef651ec49d02` |
| Thời điểm trong report | 2026-08-25 00:14:08 |
| Kết quả ML hiển thị | Precision 0,976; Recall 0,991; F1 0,984 |
| Hạn chế | HTML không lưu raw prediction, thứ tự input hoặc sidecar provenance |

### Audit độc lập để kiểm tra evaluator

| Thuộc tính | Giá trị |
|---|---|
| Dataset | `benchmark_results/dataset/20260824` |
| Dataset manifest SHA-256 | `d5d55d44aa9a8cff6f39a292a7f99e186887a15b8c0c5ac300399b8e5f4d5a23` |
| Model | `src/ml/Yolo26m/best.pt` |
| Model SHA-256 | `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c` |
| Confidence | 0,25 |
| Spatial rule | one-to-one, đúng class, IoU ≥ 0,50 |
| Prediction sau pipeline cũ | 10.157 |
| GT | 10.000 |
| Audit JSON SHA-256 | `f90af3621a0e6aa5fab79d8511329a8092f9b2e6058e426a1a584b6701abb2d8` |

Audit chạy lại inference vì HTML baseline không chứa bbox prediction. Đây không được mô tả là bbox của chính lượt inference `001406`. Tuy nhiên, audit dùng đúng dataset, model, confidence và đường xử lý ML cũ; đặc biệt công thức cũ trên snapshot audit tái tạo chính xác số chưa làm tròn **P = 0,9760756; R = 0,9914; F1 = 0,9836781**, khớp với `0,976 / 0,991 / 0,984` trong HTML.

## 3. Dataset đã dùng

Dataset đạt điều kiện để đánh giá benchmark cũ về mặt inventory:

| Nội dung | Số lượng |
|---|---:|
| Ảnh PNG | 200 |
| File GT | 200 |
| Tổng object GT | 10.000 |
| Bbox dương và nằm trong ảnh | 10.000 |
| Object mỗi ảnh | 50 |
| Microbead/Pellet | 3.302 |
| Fiber/Filament | 3.364 |
| Irregular, gồm Fragment + Irregular | 3.334 |

Có ba GT Fiber có bbox 1×1 sau erosion: `synthetic_069 #1`, `synthetic_147 #4`, `synthetic_199 #3`. Khi loại ba GT này, spatial F1 thay đổi từ `0,525673` thành `0,525752`, tức chỉ `+0,000079`. Ba bbox này **không giải thích được** chênh lệch 45,80 điểm phần trăm.

## 4. Evidence hình ảnh trực tiếp

Hình dưới chọn bốn ảnh có đúng 50 prediction và 50 GT. Công thức cũ cho cả bốn ảnh **F1 = 1,000** chỉ vì hai số lượng bằng nhau. Matching bbox cho F1 chỉ từ **0,360 đến 0,400**.

Quy ước màu:

- Xanh lá: GT đã match.
- Vàng: GT bị bỏ sót.
- Xanh cyan: prediction đã match đúng class và IoU.
- Đỏ: prediction không match, là false positive.

![Bốn trường hợp count F1 bằng 1 nhưng spatial F1 thấp](../benchmark_results/evidence/pre_fix_baseline_20260825_001406/spatial_failure_contact_sheet.png)

| Ảnh | Prediction | GT | F1 theo số lượng | TP/FP/FN theo bbox | F1 theo bbox |
|---|---:|---:|---:|---:|---:|
| `synthetic_076` | 50 | 50 | **1,000** | 18 / 32 / 32 | **0,360** |
| `synthetic_002` | 50 | 50 | **1,000** | 20 / 30 / 30 | **0,400** |
| `synthetic_006` | 50 | 50 | **1,000** | 20 / 30 / 30 | **0,400** |
| `synthetic_138` | 50 | 50 | **1,000** | 20 / 30 / 30 | **0,400** |

Ảnh full-resolution nằm trong thư mục evidence với tên `overlay_synthetic_*.png` để phóng to khi trình bày.

## 5. Các điểm sai hoặc gây hiểu nhầm

### Vấn đề 1 — Precision, Recall và F1 không phải detection metrics

**Tình trạng hiện tại**

Source cũ tính cho từng ảnh:

```python
tp = min(detected, gt)
fp = max(0, detected - gt)
fn = max(0, gt - detected)
```

Đoạn này nằm tại `src/gui/main_window.py:5222-5224`.

**Evidence**

GT có dòng `Bounding Box`, nhưng parser cũ chỉ xử lý `Position`, `Area`, `Size` tại `src/gui/main_window.py:5052-5059`; không có nhánh đọc `Bounding Box`. Vì vậy evaluator không có dữ liệu để xác định prediction nào khớp GT nào.

Ví dụ `synthetic_076`: 50 prediction và 50 GT làm công thức cũ tạo TP=50, FP=0, FN=0. Matching thật chỉ tìm được 18 TP; còn lại là 32 FP và 32 FN.

**Ảnh hưởng**

- Không đo khả năng phát hiện object.
- Prediction sai vị trí, bbox sai kích thước hoặc prediction của object khác vẫn có thể được tính TP.
- Không phát hiện duplicate prediction nếu tổng đếm tình cờ gần GT.
- F1 0,984 gây kết luận model gần hoàn hảo trong khi spatial F1 chỉ 0,526.

**Cách sửa cụ thể**

1. Parse và lưu GT bbox theo `xywh` pixel, đổi có kiểm soát sang `xyxy` khi matching.
2. Chuẩn hóa đúng ba class: `Microbead/Pellet`, `Fiber/Filament`, `Irregular`; map `Fragment → Irregular`.
3. Với mỗi ảnh và class, sort prediction theo confidence; mỗi prediction chỉ được ghép tối đa một GT, và mỗi GT chỉ được ghép một prediction.
4. TP khi đúng class và IoU ≥ ngưỡng; prediction không ghép là FP; GT không ghép là FN.
5. Aggregate TP/FP/FN toàn dataset rồi mới tính micro Precision/Recall/F1; đồng thời báo cáo riêng từng class.
6. Thêm test: perfect match, sai vị trí, sai class, duplicate prediction, ảnh không có prediction và ảnh không có GT.

### Vấn đề 2 — Biểu đồ Shape của “ML Benchmark” không dùng class YOLO

**Tình trạng hiện tại**

Model YOLO có đúng ba class, nhưng biểu đồ baseline hiển thị bốn nhóm: `Fiber/Filament`, `Fragment`, `Irregular`, `Microbead/Pellet`.

![Biểu đồ shape gốc trong baseline](../benchmark_results/evidence/pre_fix_baseline_20260825_001406/baseline_report_chart_02.png)

YOLO class được lưu ở `feature['ml_class']` (`src/analysis/ml_benchmark_analyzer.py:133`). Tuy nhiên report lại cộng `feature['shape']` tại `src/gui/main_window.py:5280`; trường này là kết quả heuristic `ShapeAnalyzer` chạy trên ROI (`src/analysis/ml_benchmark_analyzer.py:119`), không phải class model.

`SHAPE_GROUP_MAPPING` còn giữ `Fragment` và `Irregular` tách riêng tại `config/constants.py:92-93`, trái với ontology ba class của model.

**Evidence số liệu**

| Nguồn | Fiber/Filament | Irregular | Microbead/Pellet | Ghi chú |
|---|---:|---:|---:|---|
| GT canonical | 3.364 | 3.334 | 3.302 | Ba class đúng |
| Raw YOLO class trong audit | 3.465 | 3.279 | 3.413 | Ba class đúng |
| Cột tím report | 812 | 6.167 + 3.164 | 14 | Heuristic bốn nhóm, không phải YOLO class |

Tổng phân phối raw YOLO nhìn khá gần GT, nhưng điều đó vẫn không chứng minh đúng object. Fiber/Filament có 3.465 prediction so với 3.364 GT, trong khi matching bbox chỉ có 160 TP.

**Ảnh hưởng**

- Người đọc tưởng đang xem hiệu năng phân loại của YOLO nhưng thực tế đang xem một classifier hình học hậu xử lý.
- Ontology bốn nhóm làm phép so sánh với model ba class không cùng định nghĩa.
- Phân phối tổng có thể gần GT dù precision/recall theo object rất thấp.

**Cách sửa cụ thể**

- Biểu đồ “YOLO class distribution” phải dùng `ml_class` và đúng ba class canonical.
- Nếu vẫn cần heuristic shape, tách thành biểu đồ “Post-processing morphology classification”, không gọi là output class của model.
- Không dùng distribution count thay cho confusion matrix/per-class detection metrics.

### Vấn đề 3 — Color chart không phải khả năng dự đoán màu của model

**Tình trạng hiện tại**

YOLO26m không có class màu. Màu được suy ra bằng `ColorAnalyzer.extract_color_from_region()` trong bbox tại `src/analysis/ml_benchmark_analyzer.py:124`, sau đó report chỉ giữ Red/Green/Blue/Yellow tại `src/gui/main_window.py:5282`.

![Biểu đồ color gốc trong baseline](../benchmark_results/evidence/pre_fix_baseline_20260825_001406/baseline_report_chart_03.png)

**Evidence số liệu**

Cột ML trong chart chỉ có Blue 142 + Green 420 + Red 218 + Yellow 650 = **1.430** object, bằng **14,08%** của 10.157 prediction. 8.727 kết quả còn lại không xuất hiện trên chart vì màu ngoài whitelist/Unknown bị loại.

**Ảnh hưởng**

- Chart dễ bị diễn giải nhầm là model dự đoán màu kém.
- Tổng cột ML không bằng tổng prediction nhưng report không hiển thị tỷ lệ bị loại.
- Không có matching theo object nên không thể tính color accuracy từ các cột tổng.

**Cách sửa cụ thể**

- Đổi nhãn thành “ROI color post-processing distribution”.
- Luôn hiển thị `Unknown/Other` và coverage: số object có màu hợp lệ / tổng prediction.
- Muốn đánh giá màu, trước hết match prediction với GT theo bbox; chỉ sau đó lập confusion matrix màu trên các cặp đã match.

### Vấn đề 4 — Số trung bình bị cắt xuống số nguyên

**Tình trạng hiện tại**

Report dùng `int(np.mean(ml_detections))` tại `src/gui/main_window.py:5332`.

**Evidence**

Audit có 10.157 prediction / 200 ảnh = **50,785 prediction/ảnh**, nhưng report hiển thị **50**. Ground Truth cũng là 50 nên biểu đồ “Detection Count Comparison” tạo cảm giác ML bằng chính xác GT.

![Biểu đồ metric và average count gốc](../benchmark_results/evidence/pre_fix_baseline_20260825_001406/baseline_report_chart_01.png)

**Ảnh hưởng**

Sai số trung bình `−0,785 object/ảnh`; tổng over-detection 157 object bị che khuất trên summary.

**Cách sửa cụ thể**

Hiển thị ít nhất một hoặc hai chữ số thập phân, kèm tổng detection, median, độ lệch chuẩn và khoảng min–max. Average count vẫn chỉ là thống kê mô tả, không thay thế detection metric.

### Vấn đề 5 — Area distribution đang so các tập object không được matching

**Tình trạng hiện tại**

Biểu đồ đặt phân phối area của toàn bộ GT cạnh area của toàn bộ prediction. Area ML được lấy từ mask segment lại bên trong ROI, hoặc fallback sang area bbox; nó không nhất quán với GT area và không ghép từng prediction với GT tương ứng.

![Biểu đồ area gốc trong baseline](../benchmark_results/evidence/pre_fix_baseline_20260825_001406/baseline_report_chart_04.png)

**Evidence**

Report cho GT mean `421,7 px²` và ML mean `651,8 px²`, nhưng không cho biết chênh lệch trên cùng object, số pair hợp lệ hoặc sai số tuyệt đối/tương đối. Vì 4.859 prediction không match và 4.702 GT bị bỏ sót trong spatial audit, hai histogram đang so hai population khác nhau.

**Ảnh hưởng và cách sửa**

Không được diễn giải chênh lệch mean là model ước lượng area sai bao nhiêu. Chỉ tính MAE, median absolute error, bias và Bland–Altman/relative error trên các cặp bbox đã match; ghi rõ area lấy từ bbox, mask hay segmentation hậu xử lý và giữ cùng định nghĩa với GT.

### Vấn đề 6 — Thiếu provenance và snapshot để kiểm toán

**Tình trạng hiện tại**

HTML không lưu dataset path/hash, danh sách ảnh có thứ tự, model hash, confidence, raw boxes hoặc sidecar JSON. Folder input được gom bằng `Path(folder).glob(ext)` tại `src/gui/main_window.py:4971` mà không sort.

**Ảnh hưởng**

- Không thể dựng lại bbox của chính lượt `001406` từ report.
- Khó chứng minh hai lượt before/after dùng đúng cùng input, model và cấu hình.
- Timing và thứ tự xử lý có thể thay đổi giữa các lượt.

**Cách sửa cụ thể**

Mỗi run cần lưu một snapshot JSON gồm: run ID, commit/source hash, dataset manifest/hash, ordered image IDs, image/GT hashes, model path/hash, class names, confidence/IoU/imgsz/device, raw prediction bbox/class/confidence, per-image metrics và report hash. Sort input theo đường dẫn chuẩn trước khi chạy.

## 6. Spatial result theo từng class

| Class | GT | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fiber/Filament | 3.364 | 160 | 3.305 | 3.204 | 0,0462 | 0,0476 | **0,0469** |
| Irregular | 3.334 | 2.981 | 298 | 353 | 0,9091 | 0,8941 | **0,9016** |
| Microbead/Pellet | 3.302 | 2.157 | 1.256 | 1.145 | 0,6320 | 0,6532 | **0,6424** |

Localization-only tìm được 5.325 cặp, còn class-aware tìm được 5.298 cặp. Chỉ chênh 27 cặp; do đó vấn đề lớn nhất trong snapshot này là **localization/bbox**, đặc biệt Fiber/Filament, không phải nhầm class giữa các object đã định vị đúng.

## 7. Những số nào có thể và không thể dùng

| Thành phần trong baseline | Đánh giá | Có thể dùng như thế nào |
|---|---|---|
| Số ảnh = 200, GT = 10.000 | Hợp lệ | Mô tả dataset |
| Tổng/average detection | Mô tả, nhưng average bị truncate | Chỉ dùng sau khi sửa hiển thị; không gọi là accuracy |
| Precision/Recall/F1 của Quick, Deep, ML | **Không hợp lệ như detection metrics** | Phải tính lại bằng object matching |
| Shape distribution ML | **Sai nguồn để đánh giá class YOLO** | Dùng `ml_class`; heuristic phải tách riêng |
| Color distribution ML | Dễ gây hiểu nhầm, coverage rất thấp | Chỉ là hậu xử lý ROI; cần Unknown/coverage và object matching |
| Area distribution | Hai population chưa matching, định nghĩa area khác nhau | Chỉ đánh giá area trên các cặp object đã match và cùng định nghĩa |
| Processing time | Chưa đủ kiểm soát | Không dùng để kết luận before/after trong báo cáo này |

## 8. Thứ tự sửa benchmark và tiêu chí chạy lại

1. Bổ sung parser GT bbox và canonical ontology ba class.
2. Lưu raw prediction + provenance sidecar trước mọi hậu xử lý.
3. Thay count agreement bằng one-to-one class-aware IoU matching; báo cáo micro và per-class metrics.
4. Sửa shape chart dùng `ml_class`; tách heuristic shape.
5. Sửa color chart thành auxiliary post-processing metric, có coverage/Unknown và matching theo object.
6. Không truncate average; sort input; lưu config/hash/version.
7. Thêm unit test metric và test lifecycle evidence.
8. Chạy after-fix trên đúng manifest/hash/model/confidence và thứ tự 200 ảnh này.
9. So sánh **cùng snapshot prediction** giữa công thức cũ và mới để chứng minh tác động evaluator; không dùng thay đổi metric để tuyên bố model được cải thiện.

## 9. Giới hạn của kết luận

- Báo cáo này đánh giá lỗi evaluator của nhánh ML; chưa tạo spatial audit cho Quick/Deep vì baseline HTML không lưu bbox output của hai nhánh đó.
- IoU@0,50 là một operating point, chưa phải mAP50 hoặc mAP50–95.
- Audit dùng greedy matching theo confidence, là quy tắc detection evaluation thông dụng. Independent maximum-cardinality matching cho 5.299 TP thay vì 5.298 và F1 `0,525773` thay vì `0,525673`; khác biệt một object không làm thay đổi kết luận.
- Snapshot audit là lượt inference độc lập với HTML `001406`, dù aggregate legacy metrics khớp chính xác đến các chữ số report hiển thị.
- Cảnh báo `Mean of empty slice` xuất hiện một lần trong post-processing ROI; cần harden riêng, nhưng nó không được dùng để giải thích chênh lệch metric.
- Đây là đánh giá **trước sửa**. Chưa có source benchmark nào được sửa trong bước này.

## 10. Danh mục evidence

| Evidence | Mục đích |
|---|---|
| `benchmark_results/evidence/pre_fix_baseline_20260825_001406/audit_summary.json` | Tóm tắt số liệu nhỏ gọn để dùng khi trình bày |
| `benchmark_results/evidence/pre_fix_baseline_20260825_001406/pre_fix_evaluator_audit.json` | Prediction, GT, pair matching, metric và provenance đầy đủ |
| `legacy_vs_spatial_metrics.png` | So sánh trực tiếp metric cũ/mới trên cùng snapshot |
| `spatial_failure_contact_sheet.png` | Bốn phản ví dụ trực quan với count F1 = 1 |
| `overlay_synthetic_002.png`, `006`, `076`, `138` | Ảnh full-resolution để kiểm tra bbox |
| `baseline_report_chart_01.png` đến `04.png` | Chart nguyên bản trích từ baseline HTML |
| `.copilot-tracking/details/2026-08-25/audit_pre_fix_baseline_001406.py` | Script tái tạo audit |
