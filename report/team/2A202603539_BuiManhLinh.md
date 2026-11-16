# Báo cáo cá nhân — Bùi Mạnh Linh

## 1. Thông tin thành viên

- Họ tên: Bùi Mạnh Linh
- MSSV: 2A202603539
- Email: 26ai.linhbm@vinuni.edu.vn
- GitHub: [manhlinh46](https://github.com/manhlinh46)

## 2. Phần việc phụ trách

Thành viên duy nhất của nhóm; phụ trách triển khai ba shape workflow, single và orchestrator, kiểm thử, benchmark và hoàn thiện báo cáo nộp bài.

## 3. Đóng góp cụ thể

- Triển khai `run_claim` cho workflow với quote tất định từ order/policy và ghi refund qua host.
- Triển khai single-agent ReAct có giới hạn bước, chỉ dùng tool đọc trước khi host quyết định ghi refund.
- Triển khai orchestrator với handoff allowlist `handoff.v1` và investigator chỉ có quyền đọc.
- Chuyển tiếp điểm crash vào `issue_refund`, không bắt `InjectedCrash`; giữ nguyên quote đầy đủ để host xử lý approval và cap theo đơn.
- Thêm test trace cho ba shape để xác nhận trace không chứa ticket thô hoặc `parent_secret`.
- Tạo `src/reports/benchmark.json` và `src/reports/crash.json` bằng lệnh lab.
- Commit chính: chưa commit các thay đổi hiện tại; cập nhật hash sau khi commit.

## 4. Bằng chứng

- `python -m pytest -q`: 57 passed.
- `python -m pytest -q -m student -o addopts=`: 248 passed.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: crash safety 20/20.
- `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`: workflow đạt pass rate 1.000, pass^5 1.000, cost/success mô phỏng 27.86 VND.
- Run id dẫn chứng trong benchmark: `R-workflow-C-001-s11`.
- `python -m lab8.check_submission`: 0 FAIL; còn cảnh báo vì thay đổi chưa commit.

## 5. Công cụ AI đã dùng

Đã dùng Copilot để hỗ trợ đọc yêu cầu, triển khai và rà soát mã, cũng như soạn báo cáo. Kết quả được tự kiểm bằng test host, ma trận student, smoke, crash suite, benchmark và submission checker; không tự tạo số liệu benchmark. Các chỉ số trong báo cáo lấy từ file do công cụ benchmark/crash của lab sinh ra.

## 6. Tự đánh giá

Ba shape đáp ứng contract công khai và các kiểm tra về policy, trace, idempotency và crash. Workflow được chọn theo benchmark public vì đạt pass rate ngang single/orchestrator nhưng có cost mô phỏng thấp hơn trong lần đo này. Kết quả hiện tại chưa bao gồm hidden grader; benchmark chỉ có 14 claim public nên không khẳng định hiệu năng tổng quát. Cần điền email, commit hash sau khi commit và cập nhật kết luận nếu hidden grader cho kết quả khác.
