# Goal

- gitoy merge develop command 구현하기 

# TODO

[x] commit entity 에 generation number attr 추가 
[] generation number 일괄 계산 코드 추가, 테스트 (top-down)
    - 현재는 필요없어 보이므로 보류. merge commit 생성 시 여러개의 부모커밋을 가진 커밋 생성 시 사용
[x] commit 시 generation number 코드 설정 로직 추가, 테스트 (bottom-up)
[] merge_base 함수 구현 및 테스트 
[] is_ancester 함수 수현 및 테스트
[] merge 함수 일부 구현 및 테스트
[] merge 가능 확인 및 ff merge 확인
[] ff merge 구현