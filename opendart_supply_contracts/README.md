# OpenDART 공급계약 누적 관리

`stocks.json`에 등록된 기업을 대상으로 OpenDART의 `단일판매ㆍ공급계약체결` 공시를 수집해 기업별 엑셀 파일과 마스터 파일에 누적 관리하는 기능입니다.

이 폴더는 `Consensus_tracking` 레포 안에 포함되어 있지만, 컨센서스 추적 기능과 섞이지 않도록 독립 모듈처럼 관리합니다.

## 하는 일

- 기업별 공급계약 공시를 엑셀 파일 하나에 계속 누적합니다.
- 신규 공시는 `신규 공시` 시트에 저장합니다.
- 정정 공시는 `정정 공시` 시트에 저장합니다.
- `공급계약_마스터.xlsx`에는 날짜별로 어떤 기업에 공급계약 공시가 있었는지만 요약합니다.
- 매일 평일 16시에 자동 실행되도록 Windows 작업 스케줄러와 연결할 수 있습니다.
- 실행일 기준 전 영업일~당일을 다시 조회하고, 접수번호 기준으로 중복 반영을 막습니다.

## 폴더 구성

```text
opendart_supply_contracts/
  build_bhi_disclosures.py
  build_contracts_for_stocks.py
  daily_update_supply_contracts.py
  rebuild_supply_contract_master.py
  run_daily_supply_update.ps1
  requirements.txt
  README.md
```

파일 역할:

- `build_contracts_for_stocks.py`: 전체 기간 데이터를 처음 구축할 때 사용합니다.
- `daily_update_supply_contracts.py`: 매일 자동 업데이트에 사용합니다.
- `rebuild_supply_contract_master.py`: 기업별 파일을 기준으로 마스터 파일을 다시 만들 때 사용합니다.
- `run_daily_supply_update.ps1`: Windows 작업 스케줄러에서 호출하는 PowerShell 래퍼입니다.
- `build_bhi_disclosures.py`: DART 원문 HTML 표를 파싱하는 공통 로직입니다.
- `requirements.txt`: 필요한 Python 패키지 목록입니다.

## GitHub에 올라가는 것과 안 올라가는 것

GitHub에 올리는 것:

- Python 코드
- PowerShell 실행 래퍼
- README 문서
- requirements.txt

GitHub에 올리지 않는 것:

- 기업별 엑셀 파일
- `공급계약_마스터.xlsx`
- 실행 로그
- OpenDART 원문 ZIP/XML
- OpenDART API 키

이런 산출물은 `.gitignore`로 제외합니다. API 키도 코드에 직접 적지 않고 환경변수로 관리합니다.

## 준비 사항

### 1. Python 패키지 설치

레포 루트에서 실행합니다.

```powershell
pip install -r .\opendart_supply_contracts\requirements.txt
```

현재 필요한 패키지는 `openpyxl`입니다.

### 2. OpenDART API 키 설정

PowerShell에서 아래처럼 설정합니다.

```powershell
$env:OPENDART_API_KEY = "YOUR_OPEN_DART_API_KEY"
```

이 설정은 현재 PowerShell 창에서만 유지됩니다. Windows 작업 스케줄러에서도 안정적으로 쓰려면 사용자 환경변수로 등록하는 것이 좋습니다.

사용자 환경변수로 등록:

```powershell
[Environment]::SetEnvironmentVariable("OPENDART_API_KEY", "YOUR_OPEN_DART_API_KEY", "User")
```

등록 후에는 새 PowerShell 창을 열어야 반영됩니다.

### 3. 기업 목록 파일

기본값은 레포 루트의 `stocks.json`입니다.

```text
C:\Investment\컨센서스 tracking\stocks.json
```

다른 파일을 쓰고 싶으면 환경변수로 지정합니다.

```powershell
$env:SUPPLY_CONTRACT_STOCKS_JSON = "C:\투자\stocks.json"
```

### 4. 엑셀 저장 위치

기본 저장 위치:

```text
G:\내 드라이브\3. Stocks\Open Dart\공급계약
```

다른 위치를 쓰고 싶으면 환경변수로 지정합니다.

```powershell
$env:SUPPLY_CONTRACT_OUTPUT_DIR = "G:\내 드라이브\3. Stocks\Open Dart\공급계약"
```

## 처음 전체 구축

처음 한 번 전체 데이터를 만들 때 실행합니다.

```powershell
python .\opendart_supply_contracts\build_contracts_for_stocks.py
python .\opendart_supply_contracts\rebuild_supply_contract_master.py
```

결과:

- `{기업명}.xlsx`
- `공급계약_마스터.xlsx`

## 매일 업데이트

일별 업데이트를 직접 실행하려면:

```powershell
python .\opendart_supply_contracts\daily_update_supply_contracts.py
```

특정 날짜를 다시 확인하려면:

```powershell
python .\opendart_supply_contracts\daily_update_supply_contracts.py --date 2026-07-07
```

실행 방식:

- 실행일이 화~금이면 전일~당일을 조회합니다.
- 실행일이 월요일이면 금요일~월요일을 조회합니다.
- 이미 반영된 접수번호는 다시 추가하지 않습니다.

예를 들어 7월 2일 17시에 공시가 올라왔고 7월 2일 16시 자동 실행에서는 못 잡았더라도, 7월 3일 16시 실행 때 7월 2일~7월 3일을 다시 조회하므로 누락을 보완할 수 있습니다.

## 브리핑 로그

매일 실행 후 `logs/` 폴더에 브리핑 파일이 생성됩니다.

```text
logs\daily_update_YYYYMMDD_briefing.txt
```

예시:

```text
2026-07-07 공급계약 공시 확인 결과:
- 2026-07-07 대우건설: 정정 공시 2행
```

신규 공시가 있으면 계약상대방과 계약금액도 표시합니다.

```text
2026-07-02 공급계약 공시 확인 결과:
- 2026-07-02 삼성중공업: 신규 계약 공시 1건, 계약상대방 오세아니아 지역 선주, 계약금액 273,400,000,000원
```

## Windows 작업 스케줄러

현재 운영 방식은 평일 16시에 `run_daily_supply_update.ps1`을 실행하는 구조입니다.

작업 스케줄러 명:

```text
OpenDART Supply Contract Daily Update
```

실행 대상:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Investment\컨센서스 tracking\opendart_supply_contracts\run_daily_supply_update.ps1"
```

권장 실행 주기:

```text
월, 화, 수, 목, 금 / 16:00
```

작업 스케줄러 등록 예시:

```powershell
$taskName = "OpenDART Supply Contract Daily Update"
$script = "C:\Investment\컨센서스 tracking\opendart_supply_contracts\run_daily_supply_update.ps1"
$workdir = "C:\Investment\컨센서스 tracking\opendart_supply_contracts"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $script + '"') -WorkingDirectory $workdir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 16:00
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force
```

## 자주 하는 확인

스케줄러 마지막 실행 확인:

```powershell
Get-ScheduledTaskInfo -TaskName "OpenDART Supply Contract Daily Update"
```

오늘 브리핑 확인:

```powershell
Get-Content .\opendart_supply_contracts\logs\daily_update_YYYYMMDD_briefing.txt
```

마스터 파일 위치:

```text
G:\내 드라이브\3. Stocks\Open Dart\공급계약\공급계약_마스터.xlsx
```

## 운영 시 주의사항

- 엑셀 파일이 열려 있으면 저장에 실패할 수 있습니다.
- 저장 실패 시 해당 파일을 닫고 같은 날짜로 다시 실행하면 됩니다.
- OpenDART API 키는 GitHub에 올리지 않습니다.
- `stocks.json`에 기업을 추가하면 다음 실행부터 대상 기업에 포함됩니다.
- 기존 공시는 접수번호 기준으로 중복 추가되지 않습니다.

## 문제 해결

### 오늘 공시가 있는데 반영되지 않은 경우

1. 해당 날짜로 다시 실행합니다.

```powershell
python .\opendart_supply_contracts\daily_update_supply_contracts.py --date 2026-07-07
```

2. 엑셀 파일이 열려 있으면 닫고 다시 실행합니다.

3. 로그를 확인합니다.

```text
opendart_supply_contracts\logs\
```

### API 키 오류가 나는 경우

환경변수가 설정되어 있는지 확인합니다.

```powershell
echo $env:OPENDART_API_KEY
```

비어 있으면 다시 설정합니다.

```powershell
$env:OPENDART_API_KEY = "YOUR_OPEN_DART_API_KEY"
```

