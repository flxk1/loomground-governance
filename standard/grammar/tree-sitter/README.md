<!-- SPDX-License-Identifier: Apache-2.0 -->
# tree-sitter-loomground

A tree-sitter grammar for the Loomground textual surface (`.lg`),
specification v0.7. `grammar.js` is the source; the parser, AST, and editor
tooling are generated from it.

## Build & test
```bash
tree-sitter generate          # grammar.js -> src/parser.c (a parser)
tree-sitter test              # run test/corpus against the generated parser
tree-sitter parse FILE.lg   # print the AST of a .lg program
```
Requires the tree-sitter CLI (and a C compiler). The generated parser (`src/`,
bindings) is a build output and is not committed; run `tree-sitter generate`.

## Relationship to the standard
This is the grammar of [`loomground.ebnf`](../loomground.ebnf) and the
[`SYNTAX.md`](../../spec/SYNTAX.md) companion in tree-sitter form. The
specification governs. This grammar
defines syntax only; the specification fixes well-formedness and semantics, and
implementations check them.
