# Seed Concept Graph

This is a first-pass concept graph for the linear algebra adaptive review
system. It is intentionally written as a human-readable seed before being
converted into JSON or another machine-readable format.

## Design Principles

- Use `slides_md` as the authority for course structure.
- Use `flipped_md` to validate that concepts appear in exercises.
- Use `mit_linear_algebra_md` to validate exam relevance and difficulty range.
- Keep nodes at teachable concept granularity, not at theorem-fragment level.
- Prefer prerequisite edges that are pedagogically meaningful for remediation.

## Top-Level Units

### U1. Linear Systems and Gaussian Elimination

Core nodes:

- linear combination
- linear equation
- system of linear equations
- solution set
- row operation
- echelon form
- reduced echelon form
- pivot / leading variable
- free variable
- Gaussian elimination
- back substitution
- consistency and inconsistency
- homogeneous system
- matrix representation of a system

Likely prerequisite edges:

- linear combination -> linear equation
- linear equation -> system of linear equations
- row operation -> Gaussian elimination
- echelon form -> pivot / leading variable
- pivot / leading variable -> free variable
- Gaussian elimination -> solution set
- homogeneous system -> nullspace

Paper relevance:

This unit is the natural entry point for cold-start diagnostic questions. It
also gives clear procedural steps for rubric-based grading.

### U2. Vector Spaces and Subspaces

Core nodes:

- vector space
- subspace
- span
- linear independence
- basis
- dimension
- coordinate vector
- row space
- column space
- nullspace
- rank
- rank-nullity relation
- direct sum / decomposition

Likely prerequisite edges:

- linear combination -> span
- span -> subspace
- linear independence -> basis
- basis -> dimension
- system solution set -> nullspace
- row reduction -> rank
- rank -> rank-nullity relation
- column space + nullspace -> fundamental subspace reasoning

Paper relevance:

This unit supports concept-level diagnosis. Many exam questions mix basis,
dimension, rank, and nullspace, making it useful for multi-label knowledge
point tagging.

### U3. Linear Maps and Matrix Representations

Core nodes:

- function / map
- linear map
- kernel
- range / image
- matrix of a linear map
- change of basis
- representation relative to bases
- composition of linear maps
- isomorphism
- inverse map

Likely prerequisite edges:

- vector space -> linear map
- linear map -> kernel
- linear map -> range / image
- basis -> matrix of a linear map
- coordinate vector -> representation relative to bases
- kernel -> nullspace
- range / image -> column space

Paper relevance:

This unit helps bridge abstract concepts and computational matrix tasks. It is
also useful for explaining why the same problem can be represented in different
bases.

### U4. Determinants

Core nodes:

- determinant definition
- determinant by row reduction
- determinant properties
- row swap / scaling effects
- cofactor expansion
- invertibility criterion
- Cramer's rule
- volume / orientation interpretation
- characteristic polynomial connection

Likely prerequisite edges:

- square matrix -> determinant
- row operation -> determinant by row reduction
- determinant properties -> invertibility criterion
- determinant -> Cramer's rule
- determinant -> characteristic polynomial

Paper relevance:

Determinants are frequent in exam-style questions and connect procedural
calculation with conceptual tests of invertibility.

### U5. Eigenvalues, Eigenvectors, and Complex Vector Spaces

Core nodes:

- complex numbers as scalars
- polynomial roots
- characteristic polynomial
- eigenvalue
- eigenvector
- eigenspace
- algebraic multiplicity
- geometric multiplicity
- diagonalization
- similar matrices
- matrix powers
- linear recurrences / dynamical systems
- Jordan form or canonical form

Likely prerequisite edges:

- determinant -> characteristic polynomial
- polynomial roots -> eigenvalue
- eigenvalue -> eigenvector
- eigenvector -> eigenspace
- basis -> diagonalization
- diagonalization -> matrix powers
- complex scalars -> complete eigenvalue factorization
- geometric multiplicity -> diagonalizability

Paper relevance:

This is a high-value topic cluster for adaptive review because errors often
come from prerequisite gaps: determinant calculation, polynomial roots, basis,
and nullspace.

### U6. Orthogonality, Projections, Least Squares, and SVD

Core nodes:

- dot product / inner product
- orthogonal vectors
- orthogonal complement
- projection
- Gram-Schmidt
- QR factorization
- least squares
- normal equations
- symmetric matrix
- positive definite matrix
- singular value decomposition
- fundamental subspaces via SVD

Likely prerequisite edges:

- dot product -> orthogonal vectors
- orthogonal vectors -> orthogonal complement
- basis -> Gram-Schmidt
- Gram-Schmidt -> QR factorization
- projection -> least squares
- least squares -> normal equations
- eigen-analysis -> symmetric matrix spectral decomposition
- symmetric matrix -> SVD
- positive definite matrix -> normal equations

Paper relevance:

This cluster appears strongly in MIT final exams. It is suitable for IRT
difficulty adaptation because problems vary from direct computation to
multi-step conceptual synthesis.

## Suggested Node Fields for JSON Conversion

Each concept node should later be represented with:

- `id`: stable snake_case identifier
- `label`: human-readable concept name
- `unit`: top-level unit
- `prerequisites`: list of concept ids
- `weight_sources`: `slides`, `flipped`, `mit_exam`
- `estimated_weight`: preliminary score from topic frequency and course role
- `example_sources`: representative Markdown file paths
- `common_error_types`: conceptual, computational, method-selection,
  notation/formula, prerequisite-gap

## Initial High-Weight Concepts

Based on topic frequency, course centrality, and exam relevance, these should
receive high initial weights:

- basis
- dimension
- rank
- nullspace
- column space
- determinant
- eigenvalue and eigenvector
- diagonalization
- orthogonality
- projection
- least squares
- SVD / singular values
- positive definite matrix

## Initial Remediation Chains

The adaptive system should use chains like these when explaining why a student
missed a problem:

- missed eigenvalue problem -> check determinant -> check polynomial roots ->
  check nullspace solving
- missed diagonalization problem -> check eigenvectors -> check basis ->
  check linear independence
- missed least squares problem -> check projection -> check orthogonality ->
  check normal equations
- missed rank/nullity problem -> check row reduction -> check pivot/free
  variables -> check nullspace basis
- missed change-of-basis problem -> check coordinate vectors -> check basis ->
  check linear map representation

