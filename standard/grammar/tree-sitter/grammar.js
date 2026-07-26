// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 flxk1
// A tree-sitter grammar for the Loomground textual surface (the .lg netlist),
// specification v0.7. Generatable: `tree-sitter generate` produces a parser and
// an AST. The normative grammar is the specification companion (SYNTAX) and
// standard/grammar/loomground.ebnf; this is that grammar in tree-sitter form.
//
// Scope: syntax only. It accepts the base netlist and the `rack` macro layer
// (which the specification expands by a pre-pass). Value-domain checks (e.g. a
// risk outside {low,medium,high,critical}) and all well-formedness/semantics are
// fixed by the specification and checked by an implementation, not here — so a
// risk value is accepted lexically and `$`-placeholders are allowed in rack
// bodies.

function commaSep1(rule) {
  return seq(rule, repeat(seq(",", rule)));
}

module.exports = grammar({
  name: "loomground",
  word: $ => $.id,
  extras: $ => [/\s/, $.comment],

  rules: {
    source_file: $ => repeat($._statement),

    comment: _ => token(seq("#", /[^\n]*/)),

    _statement: $ => choice(
      $.actor_decl,
      $.human_decl,
      $.gate_decl,
      $.cord,
      $.reserve_decl,
      $.prohibit_decl,
      $.obligation_decl,
      $.redress_decl,
      $.rack_def,
      $.rack_use,
    ),

    actor_decl: $ => seq("actor", field("id", $.id), repeat(choice(
      seq("party", field("party", $.id)),
      seq("on-behalf-of", field("delegator", $.id)),
      seq("grade", field("grade", $._grade_value)),
      seq("name", $.text_to_eol),
    ))),

    human_decl: $ => seq("human", field("id", $.id), repeat(choice(
      seq("role", field("role", $.id)),
      seq("name", $.text_to_eol),
    ))),

    gate_decl: $ => seq("gate", field("id", $.id), repeat($._gate_opt), optional($.grant_clause)),
    _gate_opt: $ => choice(
      seq("risk", field("risk_floor", $._risk_value)),
      seq("grade", field("grade_required", $._grade_value)),
      seq("party", field("party", $.id)),
      seq("name", $.id),
    ),
    grant_clause: $ => seq("grant", repeat1($.grant)),
    grant: $ => seq(field("actor", $.id), optional(seq(
      "[", commaSep1($.id), optional(seq(":", commaSep1($._risk_value))), "]",
    ))),

    cord: $ => seq("cord", field("from", $.endpoint), "->", field("to", $.endpoint)),
    endpoint: $ => choice($.id, $.master),
    master: _ => "master",

    reserve_decl: $ => seq("reserve", field("kind", $.id), "by", field("target", $.target),
      optional(seq("when", $.guard)),
      optional(seq("duration", $.duration, ":", $.on_elapse))),

    prohibit_decl: $ => seq("prohibit", field("kind", $.id), optional(seq("when", $.guard))),

    obligation_decl: $ => seq("obligation", field("obligation", $.obligation), "on", field("gate", $.id)),

    redress_decl: $ => seq("redress", field("kind", $.id), "by", field("by", $.id),
      optional("overturn"), optional(seq("within", $.duration))),

    target: $ => choice(
      seq($.id, "and", $.id),
      seq($.number, "of", "{", commaSep1($.id), "}"),
      $.id,
    ),

    // A guard parses generically as <field> <op> <value>. The valid field domain
    // {kind, risk, party, tags} and the valid (field, op) pairing (kind/party with
    // `=`, risk with `>=`|`=`, tags with `contains`) are enforced at apply — the
    // no-id wall: a guard over `id` or `provenance`, or an invalid pairing, parses
    // here and is rejected at apply, exactly as an out-of-domain `_risk_value` is.
    guard: $ => seq($.id, $.guard_op, $._risk_value),
    guard_op: _ => choice(">=", "=", "contains"),
    on_elapse: _ => choice("halt", "proceed"),

    obligation: $ => choice(
      "ai-interaction-disclosure",
      "synthetic-content-marking",
      "emotion-or-biometric-disclosure",
      "deepfake-disclosure",
      "data-minimisation",
      $.id,
    ),

    // a risk *value*: a recognised level, or any identifier (out-of-domain
    // values and rack `$`-placeholders are accepted here and checked elsewhere).
    _risk_value: $ => choice($.risk, $.id),
    risk: _ => choice("low", "medium", "high", "critical"),

    // an autonomy grade *value*: a default-ladder level, or any identifier (values
    // outside the active ladder and rack `$`-placeholders are accepted here and
    // checked at apply). grade is a config attribute (granted on actor, required on
    // a SOURCE gate), never a token field and never guardable; grade_required on a
    // non-source (piped) gate is ill-formed at apply.
    _grade_value: $ => choice($.grade, $.id),
    grade: _ => choice("L0", "L1", "L2", "L3", "L4"),

    // the rack macro layer (a pre-pass in the specification)
    rack_def: $ => seq("rack", field("name", $.id),
      "(", optional(commaSep1($.id)), ")", ":",
      repeat($._statement), "end"),
    rack_use: $ => seq("rack-use", field("name", $.id),
      "(", optional(commaSep1($.binding)), ")"),
    binding: $ => seq(field("param", $.id), "=", field("value", choice($.id, $.risk, $.number))),

    duration: _ => token(seq(/[0-9]+/, /[mhd]/)),
    number: _ => /[0-9]+/,
    id: _ => token(choice(/[A-Za-z][A-Za-z0-9_-]*/, /\$[A-Za-z0-9_]+/)),
    text_to_eol: _ => /[^\n]+/,
  },
});
