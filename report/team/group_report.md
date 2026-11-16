# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Bùi Mạnh Linh
- Thành viên: Bùi Mạnh Linh 
- Commit chốt: 034c6c4
 

## 2. Mục tiêu và cách tiếp cận

Mục tiêu là xử lý claim hoàn phí theo bốn kiến trúc cùng contract `run_claim`, trong khi code giữ quyền quyết định tiền, approval, trần theo đơn và idempotency. Ba shape workflow, single và orchestrator được triển khai; swarm dùng làm baseline tham chiếu. Mọi phép so sánh dùng cùng 14 claim public, năm seed (11, 22, 33, 44, 55), giá mô phỏng và evaluator.

## 3. Giải pháp

- **Workflow:** đọc claim bằng tool allowlist, xác minh order theo principal, gọi quote tất định từ order/policy và chuyển quote đầy đủ cho `issue_refund`. Không dùng model để quyết định tiền.
- **Single:** dùng vòng `run_react` giới hạn 8 bước và chỉ gọi tool đọc (`get_claim_view`, `lookup_order`, `compute_compensation`). Shape mới gọi host để ghi refund sau khi nhận quote; không trao quyền ghi cho model.
- **Orchestrator:** tạo handoff bằng `make_handoff` theo `handoff.v1`, investigator chỉ nhận tool đọc và trả order/policy/quote đã giới hạn field. Orchestrator mới gọi `issue_refund`.
- **Bảo mật và durability:** trace không ghi ticket thô, principal, secret/header hay trường PII nhạy cảm; crash được chuyển tiếp để kiểm thử rồi host xử lý retry/idempotency. Mọi quote dương đều đi qua host để approval và cap theo đơn.

## 4. Kết quả

Nguồn số liệu: `src/reports/benchmark.json`; public có 14 claim × 5 seed = 70 trial/shape.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
|---|---:|---:|---:|---:|---:|---:|
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 2.86 / 3 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 29.98 | 3.14 / 4 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.30 | 3.79 / 4 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Crash suite đạt `20/20` (`src/reports/crash.json`). Cổng host: 57 passed; ma trận student: 248 passed. Test mới `src/tests/test_student_shapes_trace.py` kiểm tra trace của ba shape không ghi ticket thô hoặc secret. Chọn workflow vì đạt cùng độ chính xác public với single/orchestrator nhưng có cost mô phỏng thấp nhất; đây chưa phải kết quả hidden. Chi tiết kiến trúc và ablation nằm trong `decision_adr.md` và `research_card.md`.

## 5. Khó khăn và cách xử lý

Máy ban đầu chưa cài pytest/PyYAML nên test không khởi động được. Cài các dependency đã khai báo bằng `python -m pip install -r requirements.txt`, sau đó chạy smoke, pytest, crash suite và benchmark thành công. Không có lỗi kỹ thuật còn tồn tại trong lượt kiểm chứng này.

## 6. Tổng hợp đóng góp

Bùi Mạnh Linh là thành viên duy nhất, phụ trách triển khai ba shape, test trace, benchmark và báo cáo. Bảng đóng góp nằm trong `TEAM.md`, báo cáo cá nhân tại `report/team/2A202603539_BuiManhLinh.md`. Hash commit chốt cần cập nhật sau khi commit các thay đổi cuối.

## 7. Hạn chế và hướng cải thiện

Benchmark chỉ gồm 14 claim public; không có nhãn/pack hidden trong repo. MockLLM không đại diện model sản xuất, chi phí token là mô phỏng và latency là `unavailable`. Cần chạy lại hidden grader của giảng viên, xác nhận approval bypass/secret leak bằng số liệu hidden và cập nhật ADR nếu kết quả thay đổi.

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- `src/reports/benchmark.json` và `src/reports/crash.json` (được tạo bởi công cụ của lab).
