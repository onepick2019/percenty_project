# MySQL 백업·복원 Runbook (Windows — Percenty 이전)

**대상:** Samsung 노트북 DB 서버 `192.168.0.94`  
**MySQL:** 8.4 (Windows Custom)  
**datadir:** `C:\MySQL\Data`  
**백업:** `D:\percenty_backups\mysql\daily\percenty_db_full_20261004_003004.sql` (~63GB)

비 DBA도 따라 할 수 있도록 **Phase A → B → C** 순서로 진행합니다.  
**Phase A는 백업 다운로드와 동시에 진행해도 됩니다.** Phase B는 **SQL 파일 다운로드·크기 확인 후** 시작하세요.

---

## 사전 체크

- [ ] Windows 관리자 계정으로 로그인 가능
- [ ] `C:` 드라이브 여유 공간 **복원본(63GB) + 데이터 파일(여유 80GB 이상 권장)**
- [ ] `D:` 에 백업 SQL 저장 경로 존재 (`D:\percenty_backups\mysql\daily\`)
- [ ] 레노보 `192.168.0.121` 쪽 MySQL/Percenty 배치는 **이미 중지**된 상태

---

## Phase A: Pre-restore prep (복원 **전** 준비)

### A-1. 폴더 생성

PowerShell **관리자**에서:

```powershell
New-Item -ItemType Directory -Force -Path 'C:\MySQL\Data','C:\MySQL\Logs','C:\MySQL\Tmp','C:\MySQL\Backup'
New-Item -ItemType Directory -Force -Path 'D:\percenty_backups\mysql\daily'
```

또는 저장소 스크립트:

```powershell
cd C:\path\to\percenty_project
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\windows\mysql_prep.ps1 -Phase PrepOnly
```

### A-2. MySQL 8.4 Windows 설치 (Custom)

1. [MySQL Community Downloads](https://dev.mysql.com/downloads/mysql/) → **Windows (x86, 64-bit), MSI Installer** → **8.4.x**.
2. 설치 유형: **Custom**.
3. **Server only** (또는 Server + Client) 선택.
4. **Advanced Options** (또는 Configuration 단계):
   - **Config Type:** Server Computer (또는 Dedicated — RAM 많으면 Dedicated)
   - **datadir:** `C:\MySQL\Data`
   - **Port:** `3306`
   - **Windows Service:** `MySQL84` (또는 기본 이름) — **Start at System Startup**
   - **Authentication:** **Use Strong Password Encryption** (MySQL 8 기본)
5. **root 비밀번호** 설정 — 안전한 곳에 기록 (복원·운영에 필요).
6. 설치 완료 후 **MySQL Server 실행** 확인.

> **참고:** 이미 다른 MySQL이 3306을 쓰면 포트 충돌합니다. `services.msc`에서 기존 MySQL 서비스 중지/제거 후 진행.

### A-3. `my.ini` — 63GB SQL import 튜닝

설치 후 `my.ini` 위치 (일반적):

- `C:\ProgramData\MySQL\MySQL Server 8.4\my.ini`

**서비스 중지** → `my.ini` 편집 → **저장** → 서비스 시작.

아래는 **16GB RAM 노트북 기준 예시**입니다. RAM이 더 크면 `innodb_buffer_pool_size`를 RAM의 **50~70%** 까지 올릴 수 있습니다 (OS·다른 앱 여유 확보).

```ini
[mysqld]
# Paths (설치 시 datadir과 일치하는지 확인)
datadir=C:/MySQL/Data
tmpdir=C:/MySQL/Tmp

# Network
port=3306
bind-address=0.0.0.0

# Large import / InnoDB
max_allowed_packet=1G
innodb_buffer_pool_size=8G
innodb_log_file_size=2G
innodb_log_buffer_size=256M
innodb_flush_log_at_trx_commit=2
innodb_doublewrite=1

# Import session often benefits from disabling FK checks in client;
# server-side keep defaults unless you know you need otherwise.

# Timeouts (long-running import)
net_read_timeout=3600
net_write_timeout=3600
wait_timeout=28800
interactive_timeout=28800

# Logging (문제 추적)
log_error=C:/MySQL/Logs/error.log
slow_query_log=1
slow_query_log_file=C:/MySQL/Logs/slow.log
long_query_time=5

# Character set (한글 — 백업과 동일 charset 확인 권장)
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[client]
default-character-set=utf8mb4
```

**서비스 재시작:**

```powershell
Restart-Service MySQL84
# 서비스 이름이 다르면: Get-Service *mysql*
```

> **주의:** `innodb_buffer_pool_size`를 물리 RAM보다 크게 잡지 마세요. import 끝난 뒤 운영 값으로 다시 조정할 수 있습니다.

### A-4. Windows Firewall — TCP 3306

**로컬 LAN(192.168.0.x) 배치/앱 서버만** 허용하는 것을 권장합니다.

PowerShell **관리자**:

```powershell
New-NetFirewallRule -DisplayName 'MySQL 3306 LAN' -Direction Inbound -Protocol TCP -LocalPort 3306 `
  -RemoteAddress 192.168.0.0/24 -Action Allow -Profile Private
```

또는 `mysql_prep.ps1 -Phase Firewall` (동일 규칙).

### A-5. root 인증 및 빈 인스턴스 확인

MySQL **Command Line Client** 또는 `bin\mysql.exe`:

```powershell
cd "C:\Program Files\MySQL\MySQL Server 8.4\bin"
.\mysql.exe -u root -p
```

SQL:

```sql
SELECT VERSION();
SHOW VARIABLES LIKE 'datadir';
SHOW VARIABLES LIKE 'max_allowed_packet';
SHOW DATABASES;
```

**기대 결과:**

- `VERSION()` → 8.4.x
- `datadir` → `C:\MySQL\Data\`
- `percenty` / 운영 DB 이름은 **아직 없거나 비어 있음** (복원 전)
- `information_schema`, `mysql`, `performance_schema`, `sys` 만 있어도 정상

**원격 접속 테스트 (같은 PC 또는 다른 LAN PC):**

```powershell
.\mysql.exe -h 192.168.0.94 -P 3306 -u root -p -e "SELECT 1;"
```

---

## Phase B: Restore from `.sql` (다운로드 **완료 후**)

### B-0. 백업 파일 무결성 (간단)

```powershell
Get-Item 'D:\percenty_backups\mysql\daily\percenty_db_full_20261004_003004.sql' |
  Select-Object FullName, Length, LastWriteTime
```

- 크기가 **약 63GB** 근처인지, 다운로드 중이면 **Length가 계속 변하는지** 확인 — **고정된 후** 복원 시작.

### B-1. 복원 전 서비스·디스크

- [ ] Phase A 완료, MySQL 서비스 **Running**
- [ ] `C:` 여유 공간 충분
- [ ] 복원은 **수 시간** 걸릴 수 있음 — 노트북 **절전 비활성**, **유선 LAN** 권장

### B-2. `mysql` 클라이언트로 import

**CMD/PowerShell** (경로는 설치 버전에 맞게):

```powershell
cd "C:\Program Files\MySQL\MySQL Server 8.4\bin"

$env:MYSQL_PWD = 'YOUR_ROOT_PASSWORD'   # 또는 -p 로 대화형 입력 (히스토리 주의)

.\mysql.exe -h 127.0.0.1 -P 3306 -u root `
  --default-character-set=utf8mb4 `
  --max_allowed_packet=1G `
  --connect-timeout=600 `
  --init-command="SET SESSION foreign_key_checks=0; SET SESSION unique_checks=0; SET autocommit=0;" `
  < "D:\percenty_backups\mysql\daily\percenty_db_full_20261004_003004.sql"
```

PowerShell에서 `<` 리다이렉션이 안 되면 **cmd.exe** 사용:

```cmd
cd /d "C:\Program Files\MySQL\MySQL Server 8.4\bin"
mysql -h 127.0.0.1 -P 3306 -u root -p --default-character-set=utf8mb4 --max_allowed_packet=1G < D:\percenty_backups\mysql\daily\percenty_db_full_20261004_003004.sql
```

**대안 (로그 남기기):**

```cmd
mysql ... 2> D:\percenty_backups\mysql\restore_errors.log
```

### B-3. 복원 후 검증 쿼리

```sql
SHOW DATABASES;

-- 백업에 포함된 DB 이름으로 변경 (예: percenty, percenty_db 등)
USE percenty_db;

SELECT COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema = DATABASE();

-- 대표 테이블 1~2개 (실제 테이블명은 SHOW TABLES 로 확인)
-- SHOW TABLES LIMIT 20;
-- SELECT COUNT(*) FROM some_core_table;

SHOW TABLE STATUS FROM percenty_db LIMIT 5;
```

**체크:**

- [ ] 예상 DB가 `SHOW DATABASES`에 보임
- [ ] 테이블 수·row count가 **0이 아님** (핵심 테이블)
- [ ] `SHOW ENGINE INNODB STATUS\G` 에 fatal error 없음

### B-4. import 후 `my.ini` 운영값 (선택)

대용량 import용으로 `innodb_flush_log_at_trx_commit=2` 를 썼다면, 안정성 우선으로 **1** 로 되돌리고 재시작 검토.

---

## Phase C: Batch PC 연결 테스트

### C-1. 네트워크

배치 PC(또는 Percenty 앱 서버)에서:

```powershell
Test-NetConnection 192.168.0.94 -Port 3306
```

MySQL 클라이언트가 있는 PC:

```powershell
mysql -h 192.168.0.94 -P 3306 -u percenty_app_user -p -e "SELECT 1;"
```

> 앱 전용 계정이 없으면 root로 테스트 후, **운영용 계정 생성·root 원격 제한** 권장.

### C-2. Percenty / 배치 자동화 (이 repo)

- `percenty_project` 배치는 **웹 브라우저(Selenium)** 로 퍼센티에 접속합니다 — **DB IP는 이 레포 설정 파일에 없습니다.**
- DB 이전 후 확인할 것:
  1. **Percenty 백엔드/웹앱** DB host가 `192.168.0.121` → **`192.168.0.94`** 로 변경되었는지 (별도 서버 설정).
  2. 배치 PC에서 **퍼센티 웹 로그인·상품 목록** 정상.
  3. **배치 1대만** 소량 작업 실행 (`docs/my_quick_guide.md` 참고 — `python percenty_gui_advanced.py` 또는 `cli/batch_cli.py` 등).

### C-3. 배치 재개

- [ ] Phase B 검증 완료
- [ ] Phase C 1대 테스트 성공
- [ ] 레노보 `192.168.0.121` MySQL **중복 기동하지 않음** (split-brain 방지)
- [ ] 전체 배치 PC 순차 재개

---

## 부록: `mysql_prep.ps1` 사용법

```powershell
# 관리자 PowerShell
Set-ExecutionPolicy -Scope Process Bypass -Force
cd C:\path\to\percenty_project\scripts\windows

.\mysql_prep.ps1                    # 폴더 + 방화벽 + 점검
.\mysql_prep.ps1 -Phase PrepOnly    # 폴더만
.\mysql_prep.ps1 -Phase Firewall    # 방화벽만
.\mysql_prep.ps1 -Phase Verify      # 서비스/포트/경로 점검 (MySQL 설치 후)
```

---

## 문제 해결 (짧게)

| 증상 | 조치 |
|------|------|
| `Can't connect` / 방화벽 | Phase A-4, `Test-NetConnection`, 서비스 Running |
| `Packet too large` | `max_allowed_packet=1G` (my.ini + 클라이언트 옵션) |
| 디스크 full | `C:\MySQL\Data` 확장 또는 불필요 파일 정리 |
| Import 매우 느림 | RAM 여유, `innodb_buffer_pool_size`, SSD, 절전 끄기 |
| charset 깨짐 | `--default-character-set=utf8mb4`, DB collation 확인 |

---

**관련:** [context-summary.md](../context-summary.md)
