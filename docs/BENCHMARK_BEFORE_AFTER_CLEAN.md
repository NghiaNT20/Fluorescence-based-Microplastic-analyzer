# So sánh benchmark trước và sau khi sửa

> [!IMPORTANT]
> Thí nghiệm 200 ảnh có kiểm soát đã hoàn tất. Kết quả chính thức nằm tại
> [BENCHMARK_CONTROLLED_200_RESULT.md](BENCHMARK_CONTROLLED_200_RESULT.md).
> Các số liệu run 10 ảnh trong tài liệu này chỉ là evidence thăm dò trước đó và không còn là kết luận chính.

> Đây là tài liệu chính cho mục tiêu hiện tại. Mục tiêu là đo ảnh hưởng của việc sửa **cách đánh giá benchmark**, không phải chứng minh model đã được cải thiện và chưa phải bước fine-tuning.

## 1. Câu hỏi cần trả lời

Benchmark cũ có làm kết quả của YOLO26m đẹp hơn thực tế hay không, và kết quả thay đổi bao nhiêu khi dùng cách đánh giá object detection đúng?

Để so sánh chính thức trước và sau khi sửa code, phải giữ nguyên model, confidence threshold và **chính dataset baseline**:

```text
benchmark_results/images/batch_20260823_165503
```

Run 10 ảnh `004112` chỉ là phép kiểm tra bổ sung giúp chứng minh hai công thức cho kết quả khác nhau trên cùng prediction. Nó không thay thế phép so sánh lịch sử trên 200 ảnh.

## 2. Evidence baseline chính thức

Baseline trước khi sửa:

```text
benchmark_results/ml_benchmark_200images_20260823_232221.html
benchmark_results/ml_benchmark_200images_20260823_232221.benchmark.json
benchmark_results/images/batch_20260823_165503/
```

Kiểm tra trực tiếp cho thấy:

| Thành phần baseline | Giá trị |
|---|---:|
| Ảnh PNG | 200 |
| File Ground Truth TXT | 200 |
| Tổng Ground Truth | 10.000 object |
| Raw YOLO detections đã lưu trong snapshot | 10.179 |
| Ảnh có raw detections | 200/200 |
| Model SHA-256 | `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c` |
| Confidence threshold | 0.25 |

Đây là dataset bắt buộc phải dùng lại cho phép so sánh end-to-end sau khi sửa.

### Blocker hiện tại

Toàn bộ 10.000 Ground Truth cũ có `Shape`, `Position`, `Area` và `Size`, nhưng có **0 trường Bounding Box**. Snapshot baseline xác nhận:

```text
status = legacy-captured
spatial_metrics_ready = false
reason = ground truth has no authoritative bounding boxes
```

Vì vậy có thể chạy lại pipeline mới trên cùng 200 ảnh, nhưng evaluator spatial sẽ không có Ground Truth bbox để tính IoU, TP/FP/FN và mAP hợp lệ. Không được tự suy bbox từ `Position`, `Area` hoặc `Size`, đặc biệt vì các trường này không chứa hướng và hình dạng đầy đủ của Fiber.

## 3. Evidence kiểm tra công thức trên run 10 ảnh

Run bổ sung:

```text
benchmark_results/ml_benchmark_10images_20260824_004112.html
benchmark_results/ml_benchmark_10images_20260824_004112.benchmark.json
```

| Thành phần | Giá trị |
|---|---:|
| Model | `src/ml/Yolo26m/best.pt` |
| SHA-256 | `c308593934437df75a9ea34ef0a6cca11337fcbe66159b2293d295be9807da5c` |
| Class | Microbead/Pellet, Fiber/Filament, Irregular |
| Số ảnh | 10 |
| Ground Truth | 500 object |
| Prediction | 500 object |
| Confidence threshold | 0.25 |
| IoU threshold của evaluator mới | 0.50 |

Snapshot có `status = spatial-ready` và `spatial_evaluation.available = true`, nên Ground Truth của run này có bounding box và có thể đánh giá theo vị trí. Các số liệu của run này chỉ trả lời câu hỏi “metric cũ sai lệch bao nhiêu trên một dữ liệu spatial-ready”, không phải “bản benchmark lịch sử 200 ảnh thay đổi bao nhiêu sau khi sửa code”.

## 4. Benchmark trước khi sửa sai ở đâu?

Metric cũ chủ yếu so sánh **số lượng** prediction và Ground Truth thay vì kiểm tra từng prediction có nằm đúng vị trí của một Ground Truth hay không. Ảnh có 50 Ground Truth và 50 prediction có thể nhận điểm gần hoàn hảo dù nhiều bounding box nằm sai vị trí.

Các sai lệch chính:

- không kiểm tra IoU giữa prediction và Ground Truth;
- không bắt buộc ghép cặp một-một;
- prediction sai vị trí không được phản ánh đúng thành FP và FN;
- Precision, Recall và F1 cũ không phải metric object detection theo không gian;
- phân bố class từng bị trộn với nhãn hình thái hậu xử lý thay vì raw class của YOLO.

Vì vậy F1 cũ chỉ được gọi là **legacy count-agreement F1**.

## 5. Benchmark sau khi sửa

Evaluator mới dùng raw YOLO detections, ontology đúng ba class và ghép prediction với Ground Truth một-một theo class và IoU. Tại IoU `0.50`, prediction ghép đúng là TP, prediction không ghép được là FP và Ground Truth không được ghép là FN. Báo cáo mới có thêm per-class Precision/Recall/F1, confusion matrix, AP@0.50 và mAP@0.50:0.95.

## 6. Kết quả audit hai công thức trên run 10 ảnh

| Metric | Trước: count agreement | Sau: spatial IoU | Chênh lệch |
|---|---:|---:|---:|
| Precision | 0.988 | 0.634 | -0.354 |
| Recall | 0.988 | 0.634 | -0.354 |
| F1 | 0.988 | 0.634 | -0.354 |
| TP/FP/FN theo vị trí | Không có | 317 / 183 / 183 | Có thể kiểm chứng |
| mAP@0.50 | Không có | 0.575 | Có thể kiểm chứng |
| mAP@0.50:0.95 | Không có | 0.202 | Có thể kiểm chứng |

F1 giảm từ `0.988` xuống `0.634`: giảm **0.354**, tương đương **35.4 điểm phần trăm**. F1 cũ cao hơn F1 spatial khoảng **55.8%**.

Trong riêng run `004112`, model và prediction không thay đổi; chỉ có công thức đánh giá thay đổi. Bảng này là evidence mạnh về lỗi metric, nhưng chưa phải kết quả rerun chính thức của baseline 200 ảnh.

## 7. Điều evaluator mới làm lộ ra

| Class | Precision | Recall | F1 | AP@0.50 |
|---|---:|---:|---:|---:|
| Microbead/Pellet | 0.775 | 0.798 | 0.786 | 0.786 |
| Fiber/Filament | 0.122 | 0.119 | 0.120 | 0.018 |
| Irregular | 0.953 | 0.934 | 0.943 | 0.920 |

Model phân loại đúng gần như toàn bộ các cặp đã khớp vị trí (`class accuracy = 99.69%`), nhưng chỉ có 318/500 cặp khớp được theo vị trí và 317 cặp đúng cả vị trí lẫn class. Vấn đề nổi bật là localization của Fiber/Filament.

Đây là lý do để điều tra model hoặc dữ liệu Fiber ở bước sau, không phải lý do để thay đổi evaluator cho đến khi điểm đẹp hơn.

## 8. Cách tạo phép so sánh 200 ảnh hợp lệ

```text
benchmark_results/ml_benchmark_200images_20260823_232221.html
benchmark_results/ml_benchmark_200images_20260823_232221.benchmark.json
```

Không tạo dataset ngẫu nhiên mới. Thực hiện theo thứ tự:

1. Giữ nguyên thư mục `batch_20260823_165503` làm dữ liệu chỉ đọc và lập SHA-256 manifest.
2. Tạo bộ annotation bbox song song cho đúng 200 ảnh; không sửa đè Ground Truth gốc.
3. Bbox phải được lấy từ annotation/mask có thẩm quyền hoặc được con người gán và review. Không suy bbox giả từ tâm và kích thước.
4. Dùng 10.179 raw detections đã lưu trong snapshot baseline cùng bbox mới để tính spatial metrics. Đây là phép so sánh **chỉ thay evaluator**, không chịu ảnh hưởng của inference chạy lại.
5. Sau đó mới chạy code benchmark hiện tại trên đúng `batch_20260823_165503`, cùng model hash và threshold `0.25`, để kiểm tra end-to-end.
6. Báo cáo riêng hai kết quả: “re-evaluation của prediction cũ” và “rerun pipeline mới”.

Nếu không bổ sung được bbox đáng tin cậy, ta vẫn có thể so sánh khả năng chạy, thời gian và count metrics trên cùng dataset, nhưng **không thể công bố spatial F1 hoặc mAP sau sửa cho baseline này**.

## 9. Phần tạm dừng để tránh lệch mục tiêu

Các nội dung sau được giữ làm tham khảo nhưng **không thuộc phép so sánh evaluator trước/sau**:

- run source-pixel `ml_benchmark_10images_20260824_205909_c594614e`;
- crop và audit hướng bounding box Fiber;
- evidence package, manifest và human visual review;
- kế hoạch fine-tuning YOLO26m.

Không chạy thêm dataset ngẫu nhiên, không fine-tune và không so hai lần inference khác nhau trước khi báo cáo evaluator được chốt.

## 10. Kết luận hiện có thể dùng khi trình bày

> Baseline lịch sử được chạy trên 200 ảnh của `batch_20260823_165503`, vì vậy phép so sánh sau sửa cũng phải dùng đúng dataset này. Snapshot baseline đã lưu 10.179 raw detections, nhưng 10.000 Ground Truth cũ không có bounding box nên hiện chưa thể tính spatial F1/mAP hợp lệ. Run 10 ảnh `004112` cho thấy trên cùng prediction, F1 count-agreement là 0.988 trong khi F1 spatial chỉ là 0.634; đây là evidence về sai lệch của công thức cũ, chưa phải kết quả sau sửa chính thức của baseline 200 ảnh.

## 11. Trạng thái và bước tiếp theo

- [x] Xác định lỗi metric cũ.
- [x] Xác định đúng dataset baseline 200 ảnh và lưu được raw prediction cũ.
- [x] Có run 10 ảnh đủ bbox để audit hai công thức.
- [x] Khóa model hash, class và confidence threshold.
- [ ] Bổ sung bbox Ground Truth đáng tin cậy cho đúng 200 ảnh baseline, trong bộ annotation song song.
- [ ] Re-evaluate 10.179 prediction cũ bằng evaluator mới.
- [ ] Rerun benchmark mới trên đúng `batch_20260823_165503`.
- [ ] Chốt báo cáo trước/sau; sau đó mới quyết định fine-tuning.

**Điểm dừng hiện tại: chưa chạy benchmark lại ngay. Bước kế tiếp là giải quyết Ground Truth bbox của chính dataset baseline; fine-tuning vẫn tạm dừng.**
