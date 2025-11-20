# Code Cohesion Analyzer

Analyze the cohesion level of code modules/classes/functions based on the 7 types of cohesion.

## Instructions for Claude

When this command is invoked, analyze the code file(s) or module(s) specified by the user and:

1. **Identify each logical unit** (module, class, or function) in the code
2. **Classify the cohesion type** for each unit according to these 7 levels (from best to worst):
   - **Functional Cohesion (Level 7)** [IDEAL] - All elements work toward a single, well-defined purpose
   - **Sequential Cohesion (Level 6)** [GOOD] - Output of one element is input to the next, like a pipeline
   - **Communicational Cohesion (Level 5)** [ACCEPTABLE] - Elements operate on the same data structure
   - **Procedural Cohesion (Level 4)** [ACCEPTABLE] - Elements follow a specific execution order
   - **Temporal Cohesion (Level 3)** [NEEDS IMPROVEMENT] - Elements executed together at specific time (e.g., initialization)
   - **Logical Cohesion (Level 2)** [POOR] - Similar operations grouped but only one selected via switch/flag
   - **Coincidental Cohesion (Level 1)** [UNACCEPTABLE] - No meaningful relationship, just grouped randomly

3. **Provide assessment** for each unit:
   - Cohesion type and level (1-7)
   - Clear reasoning for the classification
   - Specific code evidence supporting your analysis
   - Impact on maintainability and reusability

4. **Give recommendations**:
   - For units with cohesion level <= 3, suggest concrete refactoring strategies
   - Prioritize improvements (worst cohesion first)
   - Show example refactoring if helpful

## Analysis Criteria

### Functional Cohesion (Level 7) - Target
- Single, well-defined responsibility
- All code serves one purpose
- Cannot be split without losing meaning
- Example: `calculateRectangleArea(width, height)` - everything focused on calculating area

### Sequential Cohesion (Level 6)
- Data flows through stages: A -> B -> C
- Output of one step is input to next
- Example: `readData() -> parseData() -> saveData()`

### Communicational Cohesion (Level 5)
- Multiple operations on same data structure
- Share input/output data
- Example: `updateBookDetails(book)` updating title, author, price of same Book object

### Procedural Cohesion (Level 4)
- Steps must execute in specific order
- Control flow focused, not data flow
- Example: `checkPermissions() -> openConnection() -> logAccess()`

### Temporal Cohesion (Level 3) - Warning Zone
- Unrelated operations executed at same time
- Time-based grouping (initialization, cleanup)
- Example: `initializeApp()` containing config load, DB connection, cache clear

### Logical Cohesion (Level 2) - Poor
- Similar operations grouped with switch/flag selection
- Only one operation executes per call
- Example: `printError(errorCode)` handling file, network, DB errors via switch
- Utility classes like `StringUtils` often fall here

### Coincidental Cohesion (Level 1) - Worst
- No meaningful relationship
- Random grouping in same file
- Example: `Utils.java` with `calculateFactorial()`, `sendEmail()`, `formatCurrency()`

## Output Format

Provide a structured report:

```
# Cohesion Analysis Report

## Summary
- Total units analyzed: X
- High cohesion (6-7): Y units
- Medium cohesion (4-5): Y units
- Low cohesion (1-3): Y units
- Overall health: [EXCELLENT/GOOD/NEEDS IMPROVEMENT/POOR]

## Detailed Analysis

### [Module/Class/Function Name]
**Cohesion Level**: X/7 - [Type Name] [IDEAL/GOOD/ACCEPTABLE/POOR/UNACCEPTABLE]
**Assessment**: [Explanation]
**Evidence**:
- [Specific code characteristics]
**Impact**: [Maintainability/reusability implications]
**Recommendation**: [If level <= 3, specific refactoring suggestions]

[Repeat for each unit]

## Priority Refactoring List
1. [Highest priority - lowest cohesion units]
2. [Next priority]
...

## Refactoring Examples
[Show concrete before/after examples for worst cases]
```

## Usage Examples

User might invoke this as:
- `/check_cohesion` (analyze current file)
- `/check_cohesion src/utils.py` (analyze specific file)
- `/check_cohesion src/repository/` (analyze all files in directory)

Be thorough but concise. Focus on actionable insights.
