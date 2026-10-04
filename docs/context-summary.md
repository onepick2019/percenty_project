# Percenty MySQL 이전 — 컨텍스트 요약 (Handoff)

**작성 목적:** 레노보 DB 서버에서 삼성 노트북으로 MySQL을 옮기는 작업의 현재 상태와 다음 단계를 한 페이지에 정리합니다.

## 환경

| 항목 | 이전 (소스) | 신규 (타겟) |
|------|-------------|-------------|
| 장비 | Lenovo PC | Samsung 노트북 (Windows DB 서버) |
| IP | 192.168.0.121 | **192.168.0.94** |
| MySQL | (기존 운영) | **MySQL 8.4** (Windows Custom 설치) |
| datadir | — | `C:\MySQL\Data` |
| 백업 보관 | — | `D:\percenty_backups\mysql\daily\` |

## 백업 파일 (복원 대상)

- **파일명:** `percenty_db_full_20261004_003004.sql`
- **크기:** 약 **63GB** (다운로드 완료 후 복원)
- **위치(권장):** `D:\percenty_backups\mysql\daily\percenty_db_full_20261004_003004.sql`

## 현재 상태 (2026-10-04)

1. **Percenty 배치 PC:** MySQL 이전을 위해 **일시 중지**됨 (DB 의존 작업 중단).
2. **백업 SQL:** 네트워크/디스크로 **다운로드 진행 중** — 완료 전까지 **Phase B(복원)는 하지 않음**.
3. **타겟 서버:** Samsung `192.168.0.94` — **Phase A(사전 준비)** 는 다운로드와 **병행 가능**.

## 권장 작업 순서

1. **지금 (다운로드 중):** [mysql_backup_restore_runbook.md](./runbooks/mysql_backup_restore_runbook.md) **Phase A** — 폴더, MySQL 8.4 설치, `my.ini` 대용량 import 튜닝, 방화벽 3306, 빈 인스턴스 확인.
2. **다운로드 완료 후:** 동일 runbook **Phase B** — `mysql` 클라이언트로 `.sql` 복원 및 검증 쿼리.
3. **복원 검증 후:** **Phase C** — 배치 PC 1대로 연결/앱 동작 테스트, 이후 배치 재개.

## 저장소 문서·스크립트

| 경로 | 설명 |
|------|------|
| `docs/runbooks/mysql_backup_restore_runbook.md` | 단계별 runbook (A/B/C) |
| `scripts/windows/mysql_prep.ps1` | (선택) 관리자 PowerShell — 폴더·방화벽·설치 후 점검 |

## 이 레포와 DB 연결

`percenty_project`는 **Selenium 기반 퍼센티 웹 UI 자동화** 중심이며, **MySQL 접속 문자열은 이 저장소에 없습니다.** 배치 PC는 브라우저로 퍼센티 서비스에 접속합니다. DB 호스트를 `192.168.0.121` → `192.168.0.94`로 바꿔야 하는 설정은 **Percenty 애플리케이션/백엔드 서버 쪽** (별도 배포)에서 확인하세요. Phase C runbook에 점검 힌트를 적어 두었습니다.

## 연락·에스컬레이션

- 복원 중 디스크 부족, `my.ini` 오류, 방화벽 차단 → Phase A 재확인.
- 복원 SQL 오류 → 소스 백업 무결성·MySQL 8.4 호환성 확인.
- 배치만 실패·웹은 정상 → Phase C 및 Percenty 백엔드 DB 설정 확인.
