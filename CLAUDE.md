# CLAUDE.md — Equal3d6

## Project Overview

Equal3d6 is a Python utility for fair D&D-style character attribute generation. It implements multiple dice-rolling methods and validity rules to produce statistically balanced characters for tabletop RPGs (primarily BECMI D&D, Stars Without Number, and LotFP variants).

**Single-file project:** All logic lives in `equal3d6.py` (161 lines).

## Running the Project

```bash
# Run as a script (generates 10 characters using sumOfModifiersIs2 rule)
python3 equal3d6.py

# Import as a library
import equal3d6
```

**Requirements:** Python 3.6+ (uses `random.choices()`). No external dependencies — stdlib only (`random`, `statistics`).

## Architecture

The codebase is organized into four functional layers:

### 1. Probability Distributions (module-level data)
- `Roll3d6Probabilities` — true 3d6 probability distribution (values 0–18)
- `Flat3d6Probabilities` — uniform distribution across 3–18

### 2. Rolling Functions
Each returns a `character`: a list of 6 integer attribute values.

| Function | Method |
|---|---|
| `roll3d6InOrderDieByDie()` | Rolls 3 actual dice per attribute |
| `roll3d6InOrderUsingDistro()` | Samples from `Roll3d6Probabilities` |
| `roll3d6InOrderUsingFlatDistro()` | Samples from `Flat3d6Probabilities` |

### 3. Modifier Systems
Convert attribute values (3–18) to modifiers. Return `-99` for invalid values (< 3).

| Function | System |
|---|---|
| `getBECMIModifier(attribValue)` | BECMI D&D: range −3 to +3 |
| `getSWNModifier(attribValue)` | Stars Without Number: range −2 to +2 |
| `sumModifiers(character, modifierLookupFunction)` | Generic sum; parametric on modifier system |
| `sumModifiersBECMI(character)` | Convenience wrapper for BECMI sum |

### 4. Validity Rules
Each takes `(character, attributeModifierRule)` and returns `bool`.

| Function | Rule |
|---|---|
| `anythingGoes` | Always valid |
| `averageAttribTotal` | Sum of attributes must equal 63 (mean for 18d6) |
| `averageSumOfModifiersRaw` | Modifier sum must equal 0 |
| `averageSumOfModifiersLotFP` | Modifier sum must be 1 or 2 |
| `sumOfModifiersIs2` | Modifier sum must equal 2 (the "Immergleich rule") |
| `LotFPCompliantSumOfModifiers` | Modifier sum must be >= 0 |
| `noSingleAttributeOutside2` | No single attribute modifier outside −2 to +2 |

### 5. Generation & Output
- `rollCharacterUntilCondition(rollFn, modifierFn, validityFn)` — retry loop until valid
- `makeCharacters(n, rollFn, modifierFn, validityFn)` — generate N valid characters
- `printCharacters(characters, printerFn)` — print with aggregate statistics
- `charAsRawValueString(c)` — format character as raw values + BECMI modifier sum + mean
- `charAsModifierOnlyString(c, modifierFn)` — format character as modifier list

## Key Design Patterns

- **Parametric/functional design**: Rolling methods, modifier systems, and validity rules are all first-class functions passed as arguments. This makes it easy to combine any rolling method with any modifier system and any validity rule.
- **Character representation**: A character is simply a Python `list` of 6 integers (e.g., `[12, 8, 15, 9, 11, 14]`), not an object or dict.
- **Rejection sampling**: `rollCharacterUntilCondition` rolls repeatedly until the validity rule passes — no upper bound on iterations, so very strict rules can be slow.

## Known TODOs (from source comments)

- Line 71: `sumModifiers` should use a list comprehension instead of a `for` loop
- Line 145: `printCharacters` should parametrize on modifier type (currently hardcodes BECMI)

## Development Conventions

- **Python version**: 3.6+ required
- **Style**: PEP 8 naming (snake_case functions, PascalCase module-level data)
- **No test suite** exists — manual validation is done by running the script and inspecting output statistics
- **No linting/formatting config** — when adding code, follow the existing style
- **Single-file**: keep all code in `equal3d6.py` unless the project explicitly grows to need modules

## Git Workflow

- Primary branch: `master`
- Feature/AI branches: `claude/<description>` pattern
- Remote: `origin`

## Extending the Project

To add a new **modifier system**: write a function `getXxxModifier(attribValue) -> int` returning a list-indexed modifier (index = attribute value, 0–18; use -99 for invalid values below 3).

To add a new **validity rule**: write a function `myRule(character, attributeModifierRule) -> bool`.

To add a new **rolling method**: write a function `rollXxx() -> list` returning a list of 6 integers in range 3–18.

All three can then be combined freely with `makeCharacters()`.
