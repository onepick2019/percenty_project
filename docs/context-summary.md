# DB 이전 컨텍스트 요약 (Percenty)

> 레노보(설계·백업 정리) ↔ 삼성 노트북(실제 MySQL 설치·복원) 핸드오프용.  
> Cursor 채팅은 PC/워크스pace마다 새로 시작하는 경우가 많으므로, 이 파일 + runbook을 `@`로 붙여 사용.

## 환경

| 구분 | IP | 역할 | 비고 |
|------|-----|------|------|
| 레노보 | 192.168.0.121 | 기존 DB·배치 | C: 256GB 풀, 백업 정리·용량 논의는 여기 채팅에 기록 |
| 삼성 노트북 | 192.168.0.94 | 신규 DB 서버 | 유선 1G, **datadir → C:**, **백업 파일 → D:** |
| 백업 서버 | (내부) | 풀 덤프 생성 | `Percenty_MySQL_Full_Backup(_User)` **Disabled**, mysqldump 없음 |

## 목표

1. **MySQL 8.4** Windows 설치  
2. **datadir** `C:\MySQL\Data`  
3. 최신 풀 SQL 복원  
4. 방화벽 **3306** (필요 시 레노보/배치 PC만 허용)  
5. 배치 PC **1대** DB 연결 테스트  

## 복원 파일 (예시 — 다운로드 완료 후 실제 파일명 확인)

- 경로: `D:\percenty_backups\mysql\daily\`
- 파일: `percenty_db_full_20261004_003004.sql` (약 **63GB** full dump)
- 더 새 덤프가 내려받기 중이면 **완료된 파일** 기준으로 runbook Phase 3 진행

## 현재 상태 체크리스트

- [ ] 노트북: MySQL **미설치** → Phase 1 runbook 진행  
- [ ] 3306 **닫힘** → 설치·서비스 기동 후 방화벽 규칙  
- [ ] 배치 PC **전부 중지** (복원·컷오버 전)  
- [ ] 풀 덤프 **다운로드 중** → 완료 전까지 **Phase 1~2** (설치·설정·빈 DB 검증)만  

## Cursor에서 새 채팅 시작 시 붙여넣기 (한 블록)

```
MySQL DB를 레노보(192.168.0.121) → 삼성 노트북(192.168.0.94)로 이전 중.
복원용: D:\percenty_backups\mysql\daily\ (최신 percenty_db_full_*.sql, ~63GB).
노트북: datadir C:\MySQL\Data, MySQL 8.4 Windows, 3306, 배치 1대 연결 테스트까지.
@docs/context-summary.md @docs/runbooks/mysql_backup_restore_runbook.md 따라 Phase부터 진행.
레노보 Cursor 채팅에서 용량·백업 정책 논의함.
```

## 관련 문서

- [MySQL 백업·복원 runbook](./runbooks/mysql_backup_restore_runbook.md)
