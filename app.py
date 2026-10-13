"""
SentinelDesk App Security Demo — Milestone 6

A deliberately minimal, deliberately vulnerable Flask app. Its only purpose
is to give CodeQL (SAST) and Dependabot (SCA) something real to catch in a
pull request, and later, to give an OWASP ZAP baseline scan (DAST) a running
target to test from the outside.

DO NOT deploy this publicly or reuse this code pattern anywhere real.
"""

import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "sentineldesk_demo.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, tenant_id TEXT, title TEXT)"
    )
    conn.execute("DELETE FROM documents")
    conn.executemany(
        "INSERT INTO documents (tenant_id, title) VALUES (?, ?)",
        [("tenant-a", "Tenant A onboarding notes"), ("tenant-b", "Tenant B billing summary")],
    )
    conn.commit()
    conn.close()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/documents")
def list_documents_vulnerable():
    """
    INTENTIONALLY VULNERABLE — CWE-89 / OWASP A03:2021 (Injection).

    tenant_id comes straight from the query string and is spliced directly
    into the SQL statement via an f-string, rather than passed as a bound
    parameter. This is the exact pattern CodeQL's py/sql-injection query is
    designed to catch, and it's the same class of bug the row-level-security
    work in Milestone 5 defends against at the database layer — this
    exercise is about catching it earlier, in the code itself, before it
    ever reaches a database that may or may not have RLS correctly enforced.
    """
    tenant_id = request.args.get("tenant_id", "")
    conn = get_db()
    query = f"SELECT id, tenant_id, title FROM documents WHERE tenant_id = '{tenant_id}'"
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/documents-safe")
def list_documents_safe():
    """The corrected version, included for contrast: a parameterized query,
    where the driver — not string formatting — is responsible for safely
    escaping the value. This endpoint should NOT trigger a SAST finding."""
    tenant_id = request.args.get("tenant_id", "")
    conn = get_db()
    rows = conn.execute(
        "SELECT id, tenant_id, title FROM documents WHERE tenant_id = ?", (tenant_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
