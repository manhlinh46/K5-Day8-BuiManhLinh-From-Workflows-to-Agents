# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: Chưa commit; điền hash sau commit chốt
- Run id dẫn chứng: R-workflow-C-001-s11 (reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (14 claim × 5 seed, public)
- Cost per success (mô phỏng, VND): 27.86 (public benchmark; không phải giá API)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trong kiểm thử public; chưa có hidden_grade.json chính thức

## Vì sao shape này

Chọn workflow vì trên cùng 14 claim, 5 seed, MockLLM, tool và evaluator, workflow đạt pass rate 1.000, pass^5 1.000, seed variance 0 và cost/success mô phỏng 27.86 VND. Kết quả pass bằng single và orchestrator nhưng rẻ hơn lần lượt khoảng 7% và 51%; so với swarm, workflow vừa không có trial sai do seed vừa có cost/success thấp hơn. Vì bài toán có luật tiền và nguồn dữ liệu cấu trúc rõ ràng, các bước cố định là đủ và là mức tự chủ thấp nhất.

## Có đáng đổi lấy multi-agent không

Trong public benchmark không có lợi ích về pass rate để bù cho chi phí cao hơn: orchestrator đạt cùng pass nhưng cost/success cao hơn, còn swarm có một lỗi ở seed 55. Kết luận chỉ áp dụng cho bộ public nhỏ và MockLLM. Có thể xem xét multi-agent lại nếu trên cùng hidden corpus, cùng tool và seed, nó cải thiện pass rate hoặc độ bền đáng kể mà không làm tăng rủi ro policy/secret; cần benchmark lặp lại trước khi đổi.

## Trace và bằng chứng

Trace ghi run id, tên bước, trạng thái order lookup, quote đã tính từ order/policy và quyết định; handoff của orchestrator chỉ dùng hợp đồng `handoff.v1` với tool đọc. Trace cố ý không ghi ticket thô, principal, secret, header, số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng. `trial_pass` kiểm tra trace và artifact theo contract; ma trận public đạt toàn bộ. Không có hidden grader trong repo này nên không tuyên bố đã qua hidden.

## Giới hạn

Benchmark chỉ có 14 claim public × 5 seed; không thay thế hidden 40 × 5. MockLLM không phải model sản xuất, chi phí là mô phỏng và latency là `unavailable`. Cần điền commit hash thật sau khi commit chốt và xác nhận lại số liệu trên grader hidden.
