# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | Zhang et al., EMNLP 2026, *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 — evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang et al. (2026), [ACL Anthology](https://aclanthology.org/2026.emnlp-main.798/), EMNLP 2026, nghiên cứu benchmark chẩn đoán có kiểm soát. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Bài báo cho rằng đánh giá hiệu quả MAS có thể phóng đại lợi ích do prompt/topology khởi đầu khác nhau; kết quả có thể phụ thuộc setup, suy sụp cấu trúc, đường đi tool bị tắt hoặc random pruning đã đủ giữ độ chính xác. Nghiên cứu đề xuất dùng backbone, agent registry và runtime chung để kiểm soát. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Claim này thuộc benchmark chẩn đoán và các phương pháp hiệu quả MAS mà bài báo đánh giá; không chứng minh mọi hệ thống multi-agent đều kém hiệu quả. Ablation của nhóm chỉ chạy 14 claim public với MockLLM, không tái lập benchmark của paper. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Workflow và orchestrator sẽ có pass rate tương đương trên public; orchestrator có cost/success cao hơn ít nhất 1.5× vì thêm planner và investigator. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định MockLLM, tool/host, corpus 14 claim, seeds 11/22/33/44/55, giá, SQLite mới mỗi trial và evaluator. Thay đổi duy nhất là shape workflow/single/orchestrator/swarm. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: chi phí tăng mà pass rate không tăng; đo pass rate, pass^5, variance theo seed và simulated cost/success. Kiểm safety riêng bằng crash suite và test trace/approval. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11`; `reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng trên bộ public. Workflow/orchestrator đều pass rate 1.000 và pass^5 1.000; cost/success lần lượt 27.86 và 57.30 VND mô phỏng (orchestrator ≈2.06× workflow). Single cũng đạt 1.000/1.000 với cost 29.98. Swarm đạt pass rate 0.986, pass^5 0.929, variance 0.000816 và cost 49.57. Kết quả chỉ có 70 trial/shape, không chứng minh kết luận cho hidden hay model thật.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
