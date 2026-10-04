# MySQL 8.4 Windows — 설치·복원 Runbook (Percenty)

**대상 PC:** 삼성 노트북 `192.168.0.94`  
**datadir:** `C:\MySQL\Data`  
**덤프 위치:** `D:\percenty_backups\mysql\daily\`  

---

## Phase 0 — 다운로드 대기 중에도 할 일 (사전 준비)

풀 덤프(60GB+) 내려받는 동안 **아래만** 진행하면 됩니다. **복원(Phase 3)은 파일 완료 후.**

### 0.1 용량 확인

PowerShell (관리자):

```powershell
Get-PSDrive C,D | Select Name, @{N='FreeGB';E={[math]::Round($_.Free/1GB,1)}}
```

- **C:** datadir + InnoDB 로그·임시 공간 → 덤프 크기의 **1.3~1.8배** 여유 권장 (63GB 덤프면 C: **100GB+ 여유** 이상이 안전)
- **D:** 덤프 파일 보관 (이미 사용 중이면 완료 후 크기 확인)

### 0.2 폴더 생성

```powershell
New-Item -ItemType Directory -Force -Path C:\MySQL\Data, C:\MySQL\Logs, C:\MySQL\Tmp
```

### 0.3 MySQL 8.4 설치 파일 미리 받기

- [MySQL Community Downloads](https://dev.mysql.com/downloads/mysql/) → **Windows (x86, 64-bit), MSI Installer**, **8.4.x LTS**
- 또는 `mysql-installer-community-8.4.x.msi` (MySQL Installer)

설치 유형: **Server only** 또는 Custom에서 **MySQL Server 8.4** 만 선택.

### 0.4 (선택) Visual C++ 재배포

MySQL / 클라이언트 도구 오류 시: Microsoft VC++ 2015–2022 x64 설치.

---

## Phase 1 — MySQL 8.4 설치 + datadir

### 1.1 설치

1. MSI 실행 → **Developer Default**가 아니라 **Server only** 권장 (불필요 구성요소 최소화).
2. **Config Type:** Development Computer 또는 Dedicated (RAM에 맞게).
3. **Authentication:** 기존 레노보와 동일 정책 유지  
   - 레거시 앱이 `mysql_native_password` 를 쓰면 설치/설정에서 **Use Legacy Authentication** 또는 이후 사용자 ALTER 필요 — 레노보 `my.ini` / 사용자 플러그인 확인 후 맞출 것.
4. Windows **Service** 이름 예: `MySQL84`, **Start at Startup**.

**중요:** 설치 마법사에서 Data Directory를 `C:\MySQL\Data` 로 지정할 수 있으면 **그때 지정**.  
이미 기본(`ProgramData\...`)으로 깔린 경우:

1. 서비스 중지: `Stop-Service MySQL84` (이름은 실제 서비스명)
2. `my.ini` 에 `datadir=C:/MySQL/Data` 설정 (아래 1.2)
3. 빈 datadir이면 **한 번만** initialize (데이터 없을 때만):

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" `
  --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.4\my.ini" `
  --initialize-insecure
```

(운영 root 비밀번호는 initialize 직후 `mysql_secure_installation` 또는 SQL로 설정.)

### 1.2 `my.ini` (복원 전·중 tuned)

파일 위치 (일반적): `C:\ProgramData\MySQL\MySQL Server 8.4\my.ini`

```ini
[mysqld]
basedir="C:/Program Files/MySQL/MySQL Server 8.4"
datadir=C:/MySQL/Data
log-error=C:/MySQL/Logs/error.log
tmpdir=C:/MySQL/Tmp

port=3306
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 대용량 풀 덤프 복원용 (복원 후 일부는 운영값으로 되돌릴 것)
max_allowed_packet=1G
net_read_timeout=3600
net_write_timeout=3600
wait_timeout=28800
interactive_timeout=28800

# RAM의 50~70% 정도까지 (예: 32GB RAM → 16G~24G)
innodb_buffer_pool_size=16G
innodb_log_file_size=2G
innodb_flush_log_at_trx_commit=2
innodb_flush_method=normal

# 복원 중만 유리; 완료 후 1 또는 운영 정책으로 변경
# sync_binlog=0

[mysql]
max_allowed_packet=1G

[client]
port=3306
default-character-set=utf8mb4
```

`innodb_buffer_pool_size` 는 **실제 RAM**에 맞게 줄이거나 키우기.

서비스 재시작:

```powershell
Restart-Service MySQL84
```

### 1.3 로컬 기동 확인 (빈 인스턴스)

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p -e "SELECT VERSION(); SHOW VARIABLES LIKE 'datadir';"
```

3306 리슨:

```powershell
Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue
```

---

## Phase 2 — 방화벽·원격 접속 (복원 전에 규칙만 만들어 두기 가능)

### 2.1 Windows 방화벽

```powershell
New-NetFirewallRule -DisplayName "MySQL 3306 (Percenty)" `
  -Direction Inbound -Protocol TCP -LocalPort 3306 `
  -RemoteAddress 192.168.0.121 -Action Allow -Profile Private
```

배치 PC IP가 따로 있으면 `-RemoteAddress` 에 추가하거나 서브넷 `192.168.0.0/24` (보안상 필요한 IP만 권장).

### 2.2 MySQL 사용자·원격 (레노보와 동일 계정명/DB명 맞추기)

레노보에서 확인한 뒤 동일하게 생성 (예시 — **실제 DB명·계정·호스트는 레노보 기준으로 교체**):

```sql
CREATE DATABASE IF NOT EXISTS percenty_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'percenty_user'@'192.168.0.%' IDENTIFIED BY '***';
GRANT ALL PRIVILEGES ON percenty_db.* TO 'percenty_user'@'192.168.0.%';
FLUSH PRIVILEGES;
```

풀 덤프에 `CREATE USER` / `GRANT` 가 포함되면 **Phase 3 후** 중복 오류 여부만 확인.

---

## Phase 3 — 풀 덤프 복원 (다운로드 완료 후)

### 3.1 덤프 무결성 간단 확인

```powershell
Get-Item "D:\percenty_backups\mysql\daily\percenty_db_full_*.sql" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1 FullName, Length, LastWriteTime
```

크기가 예상(~63GB)과 비슷하고, 전송 중이 아닐 것 (복사 도구가 “완료” 상태).

### 3.2 복원 실행 (cmd/PowerShell, **mysql 클라이언트**)

PowerShell에서 리다이렉션은 느리거나 인코딩 이슈가 있을 수 있어 **cmd** 권장:

```cmd
cd /d "C:\Program Files\MySQL\MySQL Server 8.4\bin"
mysql.exe -u root -p --default-character-set=utf8mb4 < "D:\percenty_backups\mysql\daily\percenty_db_full_YYYYMMDD_HHMMSS.sql"
```

- **수 시간** 걸릴 수 있음. 같은 세션에서 PC 절전 해제.
- 오류 시 `C:\MySQL\Logs\error.log` 와 콘솔 마지막 메시지 저장.

### 3.3 복원 후 검증

```sql
SHOW DATABASES;
USE percenty_db;
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'percenty_db';
-- 핵심 테이블 row count 1~2개 spot check
```

운영 튜닝 되돌리기 (예):

```ini
innodb_flush_log_at_trx_commit=1
```

→ `Restart-Service MySQL84`

---

## Phase 4 — 배치 PC 1대 연결 테스트

1. 배치 PC의 DB 설정(호스트 `192.168.0.94`, 포트 `3306`, DB/用户)을 **노트북 IP**로 변경 (레노보와 동일 키 이름).
2. **한 대만** 기동 → 로그인/단순 step 또는 health check.
3. 성공 후 나머지 PC 일괄 전환·레노보 MySQL 서비스 중지는 **별도 컷오버 창**에서.

원격에서 노트북 MySQL 테스트 (레노보):

```cmd
mysql -h 192.168.0.94 -P 3306 -u percenty_user -p -e "SELECT 1;"
```

---

## Phase 5 — 백업 서버 정책 (참고)

- `Percenty_MySQL_Full_Backup` / `_User` 태스크 **Disabled** 상태 유지 여부는 컷오버 후 재설정.
- 신규 서버 기준 **덤프 경로·계정** runbook / 작업 스케줄러 문서화.

---

## 문제 해결 빠른 참조

| 증상 | 확인 |
|------|------|
| 3306 연결 거부 | 서비스 실행, `bind-address` (0.0.0.0 또는 필요 IP), 방화벽 |
| Access denied | user@host, 비밀번호, 덤프 내 DEFINER/GRANT |
| Packet too large | client/server `max_allowed_packet` |
| Disk full | C: datadir 여유, temp on `C:\MySQL\Tmp` |
| 매우 느린 import | buffer pool, flush_log_at_trx_commit=2 (임시), 디스크 SSD |

---

## Cursor Agent에게 시킬 때

```
다운로드는 진행 중. Phase 0~2 먼저 실행하고, 덤프 경로 확인되면 Phase 3.
@docs/context-summary.md @docs/runbooks/mysql_backup_restore_runbook.md
```
