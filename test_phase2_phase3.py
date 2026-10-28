"""
test_phase2_phase3.py
---------------------
Automated test suite verifying Phase 2 & Phase 3 POC endpoints:
  1. /health
  2. /ask (RAG)
  3. /content/boards
  4. /content/guide/tn_10_eng_ch1
  5. /practice/generate
  6. /exam/start -> /exam/{id}/violation -> /exam/{id}/submit
  7. /grade/written (AI Evaluator)
  8. /leaderboard/TN_STATE/tn_class_10
  9. /parent/students/stu_101/progress
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all_phase2_3_features():
    print("Testing GET /health ...")
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("  [OK] Health:", r.json())

    print("\nTesting POST /ask (RAG Engine) ...")
    r = client.post("/ask", json={"question": "Why was the young seagull afraid to fly?"})
    assert r.status_code == 200, f"RAG failed: {r.text}"
    res = r.json()
    print("  [OK] RAG Answer:", res["answer"][:100], "...")
    print("  [OK] Sources:", len(res["sources"]), "retrieved from pgvector")

    print("\nTesting GET /content/boards ...")
    r = client.get("/content/boards")
    assert r.status_code == 200
    print("  [OK] Boards:", r.json())

    print("\nTesting GET /content/guide/tn_10_eng_ch1 ...")
    r = client.get("/content/guide/tn_10_eng_ch1")
    assert r.status_code == 200
    print("  [OK] Guide Title & Takeaways:", r.json()["key_points"])

    print("\nTesting POST /practice/generate ...")
    r = client.post("/practice/generate", json={"subject_id": "tn_10_english"})
    assert r.status_code == 200
    p = r.json()
    print("  [OK] Generated Practice Paper Total Marks:", p["total_marks"])

    print("\nTesting Exam & Anti-Cheat Proctoring Flow ...")
    r = client.post("/exam/start", json={"subject_id": "tn_10_english"})
    assert r.status_code == 200
    exam_data = r.json()
    exam_id = exam_data["exam_id"]
    print(f"  [OK] Started Mock Exam ID: {exam_id}")

    # Log tab switch violation
    r = client.post(f"/exam/{exam_id}/violation", json={"event_type": "tab_switch", "timestamp_ms": 1700000000})
    assert r.status_code == 200
    print("  [OK] Anti-cheat logged tab-switch violation")

    # Submit exam
    mcq_q_id = exam_data["mcqs"][0]["id"]
    written_q_id = exam_data["written_questions"][0]["id"]
    submit_req = {
        "mcq_answers": {mcq_q_id: 1},
        "written_answers": {written_q_id: "The mother seagull flew near the ledge with fish to make the hungry seagull dive and spread his wings."}
    }
    r = client.post(f"/exam/{exam_id}/submit", json=submit_req)
    assert r.status_code == 200
    submit_res = r.json()
    print("  [OK] Exam Submitted! Score:", submit_res["score"], "/", submit_res["max_score"])
    print("  [OK] AI Written Evaluation Feedback:", submit_res["written_evaluations"][0]["feedback"])

    print("\nTesting Standalone /grade/written ...")
    r = client.post("/grade/written", json={
        "question_text": "Role of mother seagull",
        "model_answer": "Model answer",
        "student_answer": "Mother held fish out of reach, forcing seagull to fly.",
        "rubric_points": [{"point_id": "r1", "description": "Mentions fish lure", "marks": 2.0}],
        "max_marks": 5.0
    })
    assert r.status_code == 200
    print("  [OK] Direct Grade Result:", r.json()["awarded_marks"], "/", r.json()["max_marks"])

    print("\nTesting GET /leaderboard/TN_STATE/tn_class_10 ...")
    r = client.get("/leaderboard/TN_STATE/tn_class_10")
    assert r.status_code == 200
    print("  [OK] Leaderboard Top Entries:", len(r.json()))

    print("\nTesting GET /parent/students/stu_101/progress ...")
    r = client.get("/parent/students/stu_101/progress")
    assert r.status_code == 200
    print("  [OK] Parent Progress Report:", r.json()["avg_score"])

    print("\n============================================================")
    print("ALL PHASE 2 & 3 POC VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("============================================================")

if __name__ == "__main__":
    test_all_phase2_3_features()
