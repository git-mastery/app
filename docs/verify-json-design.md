# Design: JSON output for `gitmastery verify`

The CLI option is implemented. Desktop adoption described below remains a separate integration step.

## 1. Goals

Adding `gitmastery verify --json` is feasible and reasonable. The CLI already receives a structured `GitAutograderOutput`, and [`verify.py`](../app/commands/verify.py) renders its status and comments separately from grading. No grader or dependency change is needed.

- Give desktop clients a stable subprocess interface for the current attempt's grading result.
- Preserve every feedback comment without depending on terminal formatting or stream chunk boundaries.
- Keep ordinary `gitmastery verify` output, grading, progress persistence, remote submission, and exit codes backward compatible.

The desktop currently spawns `["verify"]` in [`runVerify`](../../git-mastery-desktop/src/electron/ipc/gitmastery.ts). `_checkCorrectSolution` and `_checkIncorrectSolution` search for `INFO  Status:` strings. `_getComments` assumes the header and first comment arrive in the same chunk and extracts only that comment. Node stream chunks do not correspond to output lines, so even unchanged CLI wording can break this parser.

This is a structured output option for an existing command. It does not introduce a service, change grading rules, or make verification free of side effects.

## 2. JSON structure

When a grading result exists, stdout contains exactly one JSON object followed by a newline:

```json
{
  "exercise_name": "under-control",
  "status": "Completed",
  "comments": []
}
```

This illustrates the contract for a completed attempt with no feedback.

| Field | Type | Meaning |
| --- | --- | --- |
| `exercise_name` | string | Exercise identifier from the resolved exercise configuration; lets a client match the result to its request. |
| `status` | string enum | `Completed`, `Incomplete`, or `Error`. |
| `comments` | string[] | All grader comments in their original order; normalize absent comments to `[]`. |

Use the existing mapping: `SUCCESSFUL` → `Completed`, `UNSUCCESSFUL` → `Incomplete`, `ERROR` → `Error`. These become fixed contract values, independent of future display wording. Preserve comment content, including newlines and Unicode, through JSON escaping. Do not insert the display placeholder `"No comments"`.

These three fields cover the desktop's grading needs. Timestamps, numeric scores, redundant `correct`/`incorrect` booleans, and a schema version are unnecessary for this first contract. Consumers should ignore additional fields; changing existing field types or status values would be a breaking change.

**Streams and exit codes:**

- JSON mode sends diagnostic text to stderr, including version warnings, repository fetching, grader prints, verbose subprocess output, and progress-saving messages. Stdout has no prefixes, ANSI escapes, or progress text.
- Preserve current exit behavior: a returned grading result can have any of the three statuses and still exit `0` when the command finishes normally. Exercise correctness comes from `status`, not the process exit code.
- Emit the result at the same point as today's `_print_output`, before `_submit_progress`. If progress submission subsequently fails, retain the grading JSON and the existing nonzero exit behavior. The result describes grading, not successful persistence.
- Failures before a grading result exists, such as missing exercise configuration or failure entering `ExercisesRepo`, produce empty stdout, diagnostics on stderr, and a nonzero exit. Do not fabricate a grading result. Usage errors and `--help` retain Click's normal behavior.

## 3. Implementation detail

### CLI implementation

| File | Change |
| --- | --- |
| [`app/commands/verify.py`](../app/commands/verify.py) | Add `@click.option("--json", "json_output", is_flag=True, default=False, ...)` and a typed `json_output: bool` callback parameter. Branch only the result renderer: serialize an explicit three-field dictionary or call the existing `_print_output`. Keep `_execute_verify` and `_submit_progress` behavior and ordering. Install the output scope outside the exercise/root guard decorators so their diagnostics are covered. |
| [`app/utils/click.py`](../app/utils/click.py) | Add a reusable, scoped JSON output context: retain the original stdout stream for the JSON writer and redirect ordinary Python stdout to stderr using `contextlib.redirect_stdout`. Nested use should reuse the saved stream, and `finally` must restore it. This covers existing `info`/`warn`/`error`, `click.echo`, and `print` calls without changing their default behavior. |
| [`app/cli.py`](../app/cli.py) | Extend `LoggingGroup.resolve_command` to identify JSON verification before the group callback runs and enter the same output scope around invocation. Resolve the command, including `v`, and inspect its options through Click rather than searching `sys.argv` substrings. This is necessary because `cli()` prints version warnings before `verify()` runs. Help and usage handling remain normal. |
| [`tests/test_verify_json.py`](../tests/test_verify_json.py) | Add deterministic contract tests using `CliRunner`, temporary configurations, and mocked grading/version/GitHub operations, plus a binary smoke test using the existing runner and a local verifier. Cover legacy text output and unchanged progress records in isolated tests. Run this contract suite separately from the existing happy-path E2E workflow. |
| [`README.md`](../README.md) | Document `verify --json`, the three fields, separate streams, exit semantics, and continued progress submission; link this design. |

The output context also wraps direct invocation of the verify command, which the REPL uses without `LoggingGroup`. The standalone subprocess contract does not include REPL banners or prompts. Avoid retaining JSON mode across subsequent commands.

Use the standard `json` module and explicitly write and flush the payload to the saved stdout stream. Its default Unicode escaping produces ASCII JSON that round-trips on Windows, Linux, and macOS without relying on the terminal encoding. Do not serialize the entire dependency dataclass, which would expose unnecessary fields and datetime serialization details.

[`app/utils/command.py`](../app/utils/command.py) already captures subprocess streams; its verbose Python prints are covered by the scope. Any verifier subprocess that inherits stdout directly must explicitly send diagnostic output to stderr: `redirect_stdout` redirects Python writes, not OS file descriptor 1.

The existing guard decorators, progress-file format, Git/GitHub helpers, packaging, and CI configuration need no edits.

### Desktop adoption in the sibling repository

| File | Proposed change |
| --- | --- |
| [`src/electron/ipc/gitmastery.ts`](../../git-mastery-desktop/src/electron/ipc/gitmastery.ts) | Request `["verify", "--json"]` when supported. Collect raw stdout without `[[terminal-line]]`, decode the complete buffer and parse once on process `close`. Keep stderr streaming as diagnostics; a stderr chunk alone must not determine failure. Render the parsed status and every comment into terminal feedback. |
| `src/electron/utils/cli/verification.ts` (new) | Isolate JSON validation and capability detection. Require the three fields, a recognized status, string comments, and the expected exercise identifier. Adapt to existing IPC data: `correct = status === "Completed"`, `incorrect = status !== "Completed"`, and `comments = comments.join("\n")`. |
| `tests/electron/verification.test.ts` (new) | Test validation, legacy capability selection, and mapping to existing desktop feedback. |
| [`tests/e2e/cli.mjs`](../../git-mastery-desktop/tests/e2e/cli.mjs), [`tests/e2e/happy-paths.e2e.ts`](../../git-mastery-desktop/tests/e2e/happy-paths.e2e.ts) | Update fixture commands and invocation expectations for capability probing and JSON verification; exercise split output chunks and preserved completion behavior. |
| [`docs/architecture/cli-output-in-terminal.md`](../../git-mastery-desktop/docs/architecture/cli-output-in-terminal.md), [`docs/development/happy-path-e2e-tests.md`](../../git-mastery-desktop/docs/development/happy-path-e2e-tests.md) | Replace descriptions of grading text parsing with the structured contract and updated fixture behavior. |

Keep the existing process-success gate and renderer IPC shape. A nonzero exit remains a task failure, even when grading JSON is available; retain that JSON for feedback. Malformed or mismatched JSON on exit `0` is also a task failure and must not patch exercise progress. The existing [`ActivityProvider`](../../git-mastery-desktop/src/ui/providers/ActivityProvider.tsx) and [`types.d.ts`](../../git-mastery-desktop/types.d.ts) can continue consuming the adapted fields without changes.

Release the CLI option first. Because the desktop resolves a separately installed binary, probe `verify --help` for the advertised `--json` option and cache support until the executable changes. Use the existing text path only for CLIs that lack the option. A failed probe should report a CLI problem. Never retry grading after malformed JSON or a submission failure: verification saves progress and could otherwise run twice.

## 4. Test cases

| Case | Expected result |
| --- | --- |
| Ordinary `verify`, including each grading status | Existing text, comment formatting, exit behavior, and progress submission remain unchanged. |
| JSON for each grading status | The entire stdout parses as one object with the specified mapping; normal completion exits `0`. |
| No comments; multiple comments; quotes, newlines, Unicode | `[]` for absent feedback; all other strings round-trip in order without display bullets or placeholders. |
| Version warning, repository message, grader `print`, migration warning, `--verbose` | Diagnostics appear on stderr; stdout remains valid JSON. Test the full group invocation, not just the verify callback. |
| Missing exercise/root; repository initialization failure | Empty stdout, stderr diagnostic, nonzero exit, and no fabricated grade. |
| Wrong-answer, invalid-state, unexpected exception inside grading | Existing `_execute_verify` conversion yields `Incomplete` or `Error` with comments in JSON. |
| Progress save/sync succeeds, warns, or fails after grading | Submission is attempted once with the same output; JSON remains intact. Warnings preserve existing exit behavior; fatal failures remain nonzero. |
| Alias `v --json`, help, invalid arguments, sequential invocations | Alias uses the contract; Click help/errors remain normal; later text commands retain their original stdout behavior. |
| Desktop receives JSON in arbitrary chunks; stderr warning; malformed/unknown/mismatched result | Parse only after complete stdout; valid results map correctly. Invalid results never mark completion or trigger another verify attempt. |
| Desktop uses older CLI; capability probe fails; executable changes | Older CLI uses the legacy path; probe failure is reported; changed executable is probed again. |
| Cross-platform binary smoke test | Separate stdout/stderr, JSON parsing, and unchanged progress persistence pass on the existing Windows, Linux, and macOS matrix. Desktop retains its existing Windows cwd gate. |

Use isolated progress directories for new cases: the current `verified_exercise_dir` fixture is session-scoped, and its legacy test expects exactly one progress entry. Mock remote operations in contract tests so they do not submit real progress.

Local validation passed: 25 CLI tests, including the packaged executable smoke test, plus Ruff and mypy checks for changed Python files. Run this contract suite on Windows and Linux as well; the existing CI matrix covers happy-path E2E tests. Desktop cases apply when that integration is implemented.
