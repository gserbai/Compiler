## The Compilation Pipeline

### 1. Lexical Analysis (The Scanner - `scanner.l`)
This phase acts as the foundational text-processing step. The compiler processes the source code and categorizes sequences of characters into recognized linguistic units.
* **Function:** Groups characters into **Tokens**.
* **Example:** Transforms a statement like `x = 10;` into `ID(x)`, `ASSIGN_OP`, `CONST(10)`, `SEMICOLON`.
* **Tool:** **Flex**.

### 2. Syntax Analysis (The Parser - `parser.y`)
This is the structural validation phase. It verifies whether the sequence of tokens adheres to the formal grammar rules of the programming language.
* **Function:** Organizes tokens into a hierarchical structure known as the **Abstract Syntax Tree (AST)**.
* **Example:** Ensures that syntactically invalid statements, such as `= x 10;`, are rejected.
* **Tool:** **Bison**.

### 3. Semantic Analysis (Logic Validation)
This phase ensures that the syntactically correct code carries valid meaning and logical consistency.
* **Function:** Performs type checking (e.g., preventing the addition of an `int` to a `string`), verifies variable declarations, and maintains the **Symbol Table**.
* **Example:** Given the expression `x = y + 1`, it verifies that `y` has been previously defined and holds a valid numeric type.

### 4. Intermediate Representation Generation (`codegen.cpp`)
This is a critical phase where the **LLVM** framework is leveraged. Rather than translating directly to the target hardware architecture, the AST is converted into an intermediate format.
* **Function:** Translates the AST into **LLVM IR** (a platform-independent, assembly-like language).
* **Advantage:** LLVM IR is highly optimizable and architecture-agnostic, allowing the frontend to be decoupled from the hardware backend.

### 5. Optimization
The LLVM toolchain analyzes the Intermediate Representation to enhance performance and execution efficiency.
* **Function:** Eliminates dead code, simplifies mathematical operations, and optimizes loop execution.
* **Research Application:** This phase provides the ideal entry point to inject **Approximate Computing** techniques directly into the IR to reduce power consumption and optimize execution time.

### 6. Machine Code Generation (Backend)
The final phase, where the compiler targets the specific underlying hardware architecture.
* **Function:** Translates the optimized LLVM IR into architecture-specific **Assembly code** (e.g., **RISC-V**).
* **Result:** Produces an `.s` file or an executable binary intended for the target simulator or physical board.

---

### Pipeline Summary
1. **Lexical Analysis:** Token identification.
2. **Syntax Analysis:** Structural organization (AST construction).
3. **Semantic Analysis:** Logical validation.
4. **IR Generation (LLVM):** Translation to a universal intermediate language.
5. **Backend:** Generation of target-specific Assembly (e.g., **RISC-V**).

---

## Build Instructions


## Usage Example

