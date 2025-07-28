# Goal

gitoy add 삭제 파일에 대한 처리

# Description

- 지금까지 신규 추가 파일 및 수정만 처리
- 삭제 파일에 대한 처리 필요
- 삭제 파일 식별 방법?
    - worktree 에서는 파일이 존재하지 않지만 index 에는 존재하는 상태
    - add 에 전달한 경로에 index_entry 와 worktree 를 모두 조회하기
    - 이후 둘을 비교하여 생성, 수정, 삭제할 파일 탐색 가능
- 생성, 수정, 삭제할 파일을 탐색했다면 생성, 수정은 기존 로직을 활용. 
- 삭제의 경우 index 에서 기존 entry 삭제
- blob 은 다른 ref 에서 참조하고 있을수도 있으므로 삭제하지 않음
- 같은 파일을 이름이나 경로만 변경한 경우 삭제 후 생성으로 간주함. 이 역시도 위 과정을 통해 처리 가능

# Todo

- database 에서 add 로 전달한 경로와 매칭되는 entry 조회하기 -> ing
- 조회한 entry 를 file 로 변환하기
- worktree 의 file 과 index 의 file을 비교하기
- 비교 로직을 처리하는 역할을 담당할 IndexDiff 객체 구현하기
    - IndexDiff 는 add pathspec 을 받아서 index_entry, worktree file 을 조회하고 비교하는 기능 수행
- repository.add_index 에 diff 로직 반영하기
- 생성, 수정, 삭제, 경로 변경 케이스에 대해서 테스트하기 

# Test it

- add path 기반으로 매칭되는 index_entry 조회
- index_entry 를 File class 로 변환하기
- IndexDiff class 의 worktree 의 file 과 index 의 file 객체 비교 기능
- 기존 repository.add_index 테스트 케이스 통과 확인
- file 삭제, 경로 변경 케이스 테스트

# AI's Review

## Technical Feedback from Senior Developer

### 🎯 **Scope Assessment**
The scope is well-defined and appropriately sized for a single commit. Handling file deletions is a natural extension of the existing `add` functionality.

### 🏗️ **Code Design**
**Strengths:**
- Good separation of concerns with `IndexDiff` class
- Follows existing repository pattern
- Maintains consistency with current architecture

**Suggestions:**
- Consider using enum/constants for file states (CREATED, MODIFIED, DELETED)
- `IndexDiff` should implement a clear interface/protocol
- Consider factory pattern for creating File objects from IndexEntry

### 🔒 **Security**
- Path traversal validation needed when processing pathspecs
- Ensure proper file path normalization
- Validate that deleted files don't expose sensitive information in error messages

### ⚡ **Performance**
**Potential Issues:**
- Comparing every index entry against worktree could be expensive
- Multiple file system calls for large repositories

**Optimizations:**
- Batch file system operations
- Consider caching worktree file states
- Use generators for large file collections
- Early exit when possible in comparison logic

### 🎨 **Design Patterns**
**Current Approach:** Good use of Repository pattern
**Recommendations:**
- Strategy pattern for different file state handlers
- Observer pattern if you need to notify about deletions
- Command pattern could encapsulate the diff operation

### 🧪 **Test Strategy**
**Missing Test Cases:**
- Edge case: symbolic links
- Permission denied scenarios
- Concurrent file modifications
- Large file handling
- Unicode/special characters in filenames
- Nested directory deletions

**Test Structure:**
```python
class TestIndexDiff:
    def test_identifies_deleted_files(self):
    def test_identifies_modified_files(self):
    def test_identifies_new_files(self):
    def test_handles_moved_files(self):
    def test_handles_permission_errors(self):
    def test_performance_with_large_repo(self):
```

### 🔧 **Implementation Recommendations**

1. **Error Handling**: Wrap file operations in try-catch blocks
2. **Logging**: Add debug logging for diff operations
3. **Type Safety**: Use proper type hints for File state enums
4. **Documentation**: Add docstrings explaining the comparison logic

### 🚨 **Potential Risks**
- Race conditions if files change during diff operation
- Memory usage with large repositories
- Incorrect file state detection leading to data loss

### ✅ **Approval with Conditions**
This is a solid scope for implementation. Please address the security and performance considerations before implementation.
