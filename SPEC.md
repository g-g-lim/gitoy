# 목표

git checkout 설계 및 구현

git checkout 이 먼저 구현되어서 다른 브랜치에서 작업이 가능해야 함. 그래야 서로 다른 작업 변경들을 merge 하는 로직을 구현하고 테스트할 수 있음

# git checkout 이란?

- 브랜치를 이동하거나, 특정 커밋/파일로 작업 디렉토리를 전환하는 명령어

# git checkout 과정

1. HEAD가 새로운 브랜치를 가리키도록 변경됨
    - 커밋 해시로 체크하면 브랜치가 아닌 커밋 자체를 직접 가리킴
2. Index 업데이트
    - 스냅샷 그대로 index를 재구성함
    - 이전 브랜치에서 작업중인 변경사항들(staging, unstaing)은 모두 그대로 이동 
    - 단, 아직 커밋하지 않고 수정중인 파일이 checkout 하려는 브랜치의 파일 내용과 충돌하면 중단
3.  Working Directory를 Index 내용으로 덮어씀
    - 없는 파일 추가
	- 수정된 파일은 해당 커밋 기준으로 덮어씀
	- 필요 없는 파일은 삭제

# git checkout 중단

- 위 과정대로 checkout은 파일을 바꾸는 동작이기 때문에, 현재 작업 중인 파일 변경 내용이 사라질 위험이 있다면 Git은 checkout을 막아버림
- 현재 Working Directory에 수정한 파일이 있는데, checkout 하려는 브랜치에서 같은 파일의 내용이 다를 때 중단이 발생
- 변경했지만, 타겟 브랜치에 해당 파일이 없는 경우는 무시. 변경했지만, 타겟 브랜치에 같은 파일이 있는데 내용이 다른 경우만 발생

| 상황 | Working Directory 변경 | 타겟 브랜치 상태 | 결과 |
|---|---|---|---|
| 파일 수정 O | 타겟 브랜치에 해당 파일 없음 | ✅ checkout 가능 | (내 변경은 그대로 유지됨) |
| 파일 수정 O | 타겟 브랜치에도 같은 파일 존재 + 내용 다름 | ❌ **checkout 불가 (충돌)** | 변경 손실 위험 → Git이 막음 |
| 파일 수정 없음 | 상관없음 | ✅ checkout 가능 | 안전하게 브랜치 이동 가능 |
| 변경했지만 이미 commit됨 | Index / Working Directory 깨끗함 | ✅ checkout 가능 | 커밋 때문에 작업 내용이 보존됨 |

# Index update 

- index 는 스냅샷과 워킹트리의 중간 단계 
- 스냅샷은 커밋과 트리, 블롭 파일로 구성됨
- 브랜치가 가르키고 있는 커밋을 조회하고 커밋이 참조하고 있는 루트 트리를 조회하면 조회된 트리를 기반으로 디렉토리 구조와 파일을 구성할 수 있음
- 디렉토리 구조와 구성된 파일은 index entry 형태로 변환이 가능함
- 기존에 저장된 entry 들을 모두 제거하고 새로 구성하는 방식이 있고, 변경점이 있는 entry 만
업데이트 하거나 제거하거나 추가하는 방식이 있을 듯
- 구현 비용만 놓고보면 기존 index 는 모두 삭제하고 새로 구성하는 것이 빠를 것
- 하지만 고려해야 하는 것이 파일 충돌 케이스. 만일 인덱스를 완전히 재구성한 뒤 파일 충돌을 발견하면 chekcout을 중단하고 이전 브랜치의 인덱스로 복원해야 함. 가능은 하지만 비효율적. 이부분은 충동 로직과도 연관됨
- index entry 만으로는 변경사항이 있다는 것만 알 수 있을 뿐, 어떤 지점이 수정되었는지, 충돌이 발생했는지 알 수 없음
- 이를 알기 위해서는 blob 파일을 복원해서 실제 파일 내용을 비교할 필요가 있음 (정말?)
- 수정하는 파일이 너무 많지 않으면 비교하는 비용은 그리 크지 않긴 함. 충돌이 중단되는 케이스는 아직 커밋되지 않은
수정중인 파일이 충돌했을 때만
- 그러면 먼저 수정중인 파일들, 즉 unstaged 상태 파일들을 먼저 조회해서 파일로 복원한 뒤 파일 비교 알고리즘을 사용해서 충돌이 발생했는지 확인하면 되지 않을까?
    - ㄴㄴ. object_id 만 비교
- git 은 checkout 시 충돌은 파일 내용을 비교하지 않고 변경되었는지만 확인

```
AI 에게 물어보니 fail-fast 전략으로 더 효율적이라는데는 동의. 하지만 변경 중인 파일에 대해서 blob 파일을 복원해서 충돌을 확인할 필요는 없다고 함. 하지만 이는 내 생각과 다름. object_id 가 다르면 다른 파일임은 
맞지만 실제로 같은 라인의 코드가 서로 달라야 충돌이 아닐까? 예를 들어 1000라인 코드 파일이 있는데 
그 파일의 변경사항이 모든 라인은 동일하고 맨 밑에 몇줄 추가된 거라면? 이것도 충돌로 봐야할까? git 은 그렇게 보고 있을까? 근데 나라면 그냥 충돌로 볼 것 같다. 구현 비용이 커서.

AI 에게 다시 물어보니 git 에서는 다음과 같이 처리하고 있다. 

- Git은 3-way 비교를 하지 않음
- Git은 "working directory 내용이 타겟과 같은지" 확인하지 않음
- 단순히: "현재 브랜치 커밋과 다르면 변경사항" → "타겟 브랜치에 같은 파일 있으면 충돌"
```

- 충돌이 발생하면 그 즉시 중단하면 되고 발생하지 않았다면 이어서 나머지 스냅샷 데이터들을 모두 index entry 로 만들면 됨
- 그리고 놓친게 있는데 이전 브랜치에서 작업중인 변경사항들(staging, unstaing)은 그대로 가져오기 위해서는 변경사항을 백업하고 index entry 구성이 끝나면 복원해야 함.
- 전체적인 과정은 다음과 같음

1. Staged, Unstaged, Untracked 파일 충돌 체크 (fail-fast)
2. Staged, Unstaged, Untracked 변경사항 백업
3. Index 전체 재구성 (target 브랜치 커밋 기준)
4. Working Directory 업데이트
5. 변경사항 복원

## 파일 충돌 케이스

### 1. 추가 (신규 파일)

| 현재 브랜치 상태 | Checkout 브랜치 상태 | 결과 |
|----------------|-------------------|------|
| 신규 생성 (untracked) | 같은 파일 존재 (내용 무관) | ❌ **충돌** |
| 신규 생성 + add (staged) | 같은 파일 존재 + 내용 같음 | ⚠️ checkout 성공하지만 **변경사항 날아감** |
| 신규 생성 + add (staged) | 같은 파일 존재 + 내용 다름 | ❌ **충돌** |
| 신규 생성 + add (staged) | 파일 없음 | ✅ **그대로 추가됨** |
| 신규 생성 (untracked) | 파일 없음 | ✅ **그대로 추가됨** |

### 2. 삭제

| 현재 브랜치 상태 | Checkout 브랜치 상태 | 결과 |
|----------------|-------------------|------|
| 삭제 + add (staged) | 같은 파일 존재 + 내용 같음 | ✅ **삭제 그대로 반영** |
| 삭제 (unstaged) | 같은 파일 존재 + 내용 같음 | ✅ **삭제 그대로 반영** |
| 삭제 + add (staged) | 같은 파일 존재 + 내용 다름 | ❌ **충돌** |
| 삭제 (unstaged) | 같은 파일 존재 + 내용 다름 | ⚠️ checkout 성공하지만 **삭제 변경내용 날아감** |

### 3. 수정

| 현재 브랜치 상태 | Checkout 브랜치 상태 | 결과 |
|----------------|-------------------|------|
| 수정 (staged) | 같은 파일 존재 + 내용 다름 | ❌ **충돌** |
| 수정 (unstaged) | 같은 파일 존재 + 내용 다름 | ❌ **충돌** |
| 수정 (staged) | 같은 파일 존재 + 내용 같음 | ✅ 안전하게 checkout |
| 수정 (unstaged) | 같은 파일 존재 + 내용 같음 | ✅ 안전하게 checkout |

### 핵심 패턴

- **Staged (add 한 경우)**: Checkout 브랜치에 같은 파일이 있고 내용이 다를 때 충돌
- **Unstaged 수정**: 수정한 파일이 checkout 브랜치에 있고 내용이 다를 때 충돌
- **Unstaged 삭제**: 보호 안 됨! 내용 다르면 변경사항 날아감
- **Untracked (신규 파일)**: Checkout 브랜치에 같은 파일명이 존재하면 무조건 충돌 (내용 무관)

### 단순화된 충돌 로직

| 변경 타입 | Checkout 브랜치 파일 상태 | 결과 |
|----------|------------------------|------|
| **추가** | 파일 없음 | ✅ 그대로 가져오기 |
| **추가** | 파일 있음 + 내용 같음 | ⚠️ 변경사항 버리기 |
| **추가** | 파일 있음 + 내용 다름 | ❌ **충돌** |
| **삭제** | 파일 없음 | ⚠️ 변경사항 버리기 |
| **삭제** | 파일 있음 + 내용 같음 | ✅ 삭제 반영 |
| **삭제** | 파일 있음 + 내용 다름 | ❌ **충돌** |
| **수정** | 파일 없음 | ❌ **충돌** |
| **수정** | 파일 있음 + 내용 같음 | ⚠️ 변경사항 버리기 |
| **수정** | 파일 있음 + 내용 다름 | ❌ **충돌** |

### 핵심 규칙

1. **Checkout 브랜치 기준**: 모든 판단은 checkout 할 브랜치의 파일 상태 기준
2. **충돌 조건 (단순화)**:
   - 추가: Checkout 브랜치에 같은 파일이 있고 내용 다름
   - 삭제: Checkout 브랜치에 같은 파일이 있고 내용 다름
   - 수정: Checkout 브랜치에 파일 없음 OR 파일 있고 내용 다름
3. **Staged/Unstaged 구분 불필요**: 위 규칙은 staged, unstaged 모두 동일하게 적용

## Staged, Unstaged, Untracked 파일 충돌 체크

- 현재 브랜치의 staged, unstaged, untracked 파일의 index entry 조회
- checkout 하려는 브랜치의 커밋, 트리, 블롭 객체 탐색
    - 현재는 스냅샷 트리를 조회하는 메서드만 존재
    - staged, unstaged entry 데이터만 조회하기 위해서는 index entry path 로 tree 조회하는 메서드 필요
    - 하지만, 기존에 있는 전체 트리 조회해서 일부 트리만 비교하게 되면 구현은 빨라짐. 일부 최적화는 어려움
    - 일단 트리 전체 조회해서 처리하고 추후 고도화
- checkout 브랜치 블롭 객체와 현재 브랜치의 staged, unstaged 블롭 객체의 경로 및 object_id 비교
    - 이 diff의 목적은? object_id 가 다른 entry가 하나라도 있을 경우 checkout 을 중단하기 위함
    - tree_diff 클래스는 현재 브랜치의 tree 와 index 를 비교하는 책임을 보유
    - tree 와 index 를 비교하는 이유는 새로운 커밋에 반영할 entry 를 식별하기 위함
    - index_diff 클래스는 현재 브랜치의 index 와 worktree 를 비교하는 책임을 보유
    - checkout diff 는 checkout 할 브랜치의 커밋 tree 와 현재 브랜치의 index 를 비교하는 것
    - checkout_diff 와 tree_diff 의 차이는 특정 index 만 비교한다는 것과 비교 후 처리가 다름
    - git 역시 이를 추상화한 diff_options struct 를 활용함
        ```
        struct diff_options {
            // 설정과 상태를 캡슐화
            // 비교 대상 (tree vs tree, tree vs index 등)
            // 출력 포맷 (patch, stat, name-only 등)
        }
        ```
    - 접근 1. checkout_conflict_checker 클래스 만들기. checkout 전 충돌에 문제가 없는지 확인하는 책임 보유. 
        - tree_diff 의 로직을 재사용할 수는 없음. tree builder 만을 활용해서 트리를 만들고 staged, unstaged entry 만 선별해서 비교하기
        - checkout_conflict_checker 로직
            - constructor 에 tree_store, index_store 의존성 주입
            - 다른 브랜치의 커밋과 비교할 staged, unstaged entry 경로를 인자로 전달받아 충돌 확인하는 함수
    - 접근 2. tree_diff 기존 로직 활용하기
        - 비교 결과를 크게 세가지로 나눌 수 있음
        - 파일 없음, 파일 있지만 내용이 같음. 있지만 내용이 다른 세가지
        - tree_diff 로직을 활용하면 파일 없음은 added 로 파일 있지만 내용 같으면 안나오고, 있지만 내용이 다른 경우는 modified 로 나올 것
        - 이 결괏값과 staged, unstaged 의 추가, 수정, 삭제 상태를 활용하여 로직 처리
- 경로가 같고 object_id 가 다르면 충돌로 간주하여 checkout 을 중단하고 오류 메시지 출력. 충돌난 파일명 출력
    - 추가, 삭제, 변경된 파일별로 다르게 처리해야 하므로 추후 케이스를 고려해야 함
    - 케이스는 위에 단순화된 충돌 규칙의 표를 따를 것
- 충돌이 없는 경우 checkout 할 브랜치의 index 와 working tree 에 반영하기 위해 보류

## Staiging 백업, 복원

- 백업, 복원이란 checkout 하려는 브랜치에 이전 작업 내용을 그대로 가져오는 것. 
- 이는 이전 브랜치에서 작업한 내용을 다른 브랜치로 그대로 이전시키기
- 그럼 git은 왜 이렇게 할까?
    - 변경중인건 테스트일수 있고 기존 코드에 영향을 주는 것이 아닐 수 있음
    - 무조건 변경사항을 버리면 안됨. 실수로 checkout 하는 경우도 존재
    - 충돌시에만 중단하는 것이 합리적. 데이터 손실은 방지하되, 방해하지 않기
- staged 는 이전 커밋에서 변경된 파일이 index 에 저장된 상태
- unstaged 는 변경은 됐지만 index 에 아직 저장되지 않은 상태
- untracked 는 unstaged 와 동일하나 신규로 추가된 파일을 가르킴
- staged 는 index 에서 조회가능. unstaged, untracked 모두 work tree 에서 index 생성 가능
- index 전체 재구성 전에 staged, unstaged, untracked entry 를 복원용으로 따로 보관.
- index 구성이 완료되면 staged 는 index 에 반영하고 unstaged, untracked entry 는 working tree 에 반영한다. index 에 반영하는 것과 working tree 에 반영하는 시점은 다름
- 생각해보니 unstaged 영역의 파일은 working tree 에 반영하는 프로세스가 필요하지 않아보임. 이유는 이전 브랜치에 이미 파일 변경사항이 working tree 에 반영되어있기 때문. checkout 하는 과정에서 working tree 는 그대로 활용됨
- staged 같은 경우 index 에 반영해야 함. checkout 하는 브랜치의 스냅샷에는 존재하지 않고 스냅샷을 기반으로 index 를 업데이트하는 과정에서 index 를 아예 초기화 시킬 예정. index 를 재구성하고 나면 staged 영역의 index entry 는 추가 반영이 필요함
- untracked 의 경우 checkout 한 브랜치에서 동일한 이름에 동일한 내용을 가진 파일이 존재할 수 있음. 이 경우 untracked 에서 unstaged 로 변경되어야 함. 사실 이는 상태로 관리하는 것은 아니니 gitoy status 출력 시 unstaged 로 출력되는지 확인할 필요가 있음.
다만 같은 파일명인데 다른 내용인 경우는 충돌이므로 checkout 중지 필요

## Index 재구성

- 충돌 확인 후 index 데이터 삭제
- checkout branch 의 commit 과 tree, blob 를 참조하여 index entry 형태로 변환
- 변환한 index entry 를 db index 테이블에 저장
- 이전 브랜치에서 이관할 변경사항(staged)이 있다면 index 에 반영

# working directory 반영

- index update 까지 완료했다면 working directory 를 변경할 차례
- index 만 업데이트 했으므로 working directory는 아직 이전 브랜치의 스냅샷인 상태
- 업데이트한 index 를 기준으로 추가, 변경, 삭제할 파일 식별하기 
- 식별 후 추가할 파일은 신규 생성, 변경할 파일은 기존 파일 덮어씌우기, 삭제할 파일은 파일 삭제 
- Working Directory 업데이트 시 unstaged 파일은 건드리지 않아야 함
    - 문제 시나리오:
    - 현재 브랜치: file.txt = "A" (unstaged 변경 = "B")
    - 타겟 브랜치: file.txt = "C"
    - Working Directory 업데이트 시:
    - Index 기준으로 file.txt를 "C"로 덮어쓰면
    - Unstaged 변경 "B"가 사라짐!
- unstaged 파일 처리 케이스
    - 추가: 새 파일 생성
    - 변경: Unstaged/Untracked 제외하고 덮어쓰기
    - 삭제: Unstaged/Untracked 제외하고 삭제

# HEAD 업데이트

- working directory 업데이트를 끝으로 head 를 checkout 한 브랜치로 변경

# checkout 구현 범위

- detached HEAD 또는 commit hash 기반 checkout 기능은 구현하지 않음
- 브랜치 전환만 이번 스코프에서 구현