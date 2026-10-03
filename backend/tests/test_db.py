from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import sqlite3

import pytest

from backend.db import claim_next_job, create_job, get_job, init_db, requeue_stale_claims, update_status


def new_job(db, n="doc.pdf"):
    return create_job(db, original_name=n, original_path="data/original.pdf", print_path="data/print.pdf")


def test_schema_create_and_create_get(tmp_path):
    db = tmp_path / "jobs.sqlite"
    init_db(db)
    job_id = new_job(db)
    job = get_job(db, job_id)
    assert job and job.status == "queued" and job.original_name == "doc.pdf"
    assert get_job(db, "missing") is None


def test_claim_is_oldest_and_atomic(tmp_path):
    db = tmp_path / "jobs.sqlite"
    ids = [new_job(db, str(i)) for i in range(4)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        claimed = list(pool.map(lambda _: claim_next_job(db), range(8)))
    claimed_ids = [job.id for job in claimed if job]
    assert len(claimed_ids) == 4
    assert len(set(claimed_ids)) == 4
    assert claimed_ids[0] == ids[0]
    assert all(get_job(db, job_id).status == "claimed" for job_id in claimed_ids)


def test_state_machine_and_clear_invalid_transition(tmp_path):
    db = tmp_path / "jobs.sqlite"
    job_id = new_job(db)
    with pytest.raises(ValueError, match="Invalid job transition"):
        update_status(db, job_id, "printed")
    assert update_status(db, job_id, "claimed").status == "claimed"
    assert update_status(db, job_id, "printing").status == "printing"
    assert update_status(db, job_id, "printed").status == "printed"
    with pytest.raises(ValueError, match="Invalid job transition"):
        update_status(db, job_id, "queued")
    with pytest.raises(ValueError, match="Unknown job status"):
        update_status(db, job_id, "bogus")
    with pytest.raises(KeyError):
        update_status(db, "missing", "claimed")


def test_failed_transition_and_error(tmp_path):
    db = tmp_path / "jobs.sqlite"
    job_id = new_job(db)
    job = update_status(db, job_id, "failed", "broken")
    assert job.status == "failed" and job.error == "broken"


def test_requeue_stale_claims(tmp_path):
    db = tmp_path / "jobs.sqlite"
    job_id = new_job(db)
    assert claim_next_job(db).id == job_id
    with sqlite3.connect(db) as connection:
        old = "2000-01-01T00:00:00+00:00"
        connection.execute("UPDATE jobs SET claimed_at=? WHERE id=?", (old, job_id))
    assert requeue_stale_claims(db, 600) == 1
    assert get_job(db, job_id).status == "queued"
    assert requeue_stale_claims(db, 600) == 0
