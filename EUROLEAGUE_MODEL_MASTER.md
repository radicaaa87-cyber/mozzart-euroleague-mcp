# EuroLeague Player Points Model — Master State

Last updated: 2026-10-04
Repository: radicaaa87-cyber/mozzart-euroleague-mcp

## Purpose
Persistent source of truth for the EuroLeague player-points model so work can continue across chats without losing locked assumptions, model rules, backtest state, or next steps.

## Current locked model
Version: MODEL 1.0
Status: LOCKED BASELINE

Pipeline:
MIN -> ATT -> efficiency -> PTS projection -> opponent/pace correction -> RAW EDGE -> signal confirmation -> BET / NO BET

## Core definitions
- Central player-points line is the only line used for official evaluation.
- RAW EDGE = final projection - central bookmaker line.
- Positive edge -> OVER direction.
- Negative edge -> UNDER direction.
- Results must be evaluated only against the locked pre-game prediction.
- Do not change rules after seeing the result.

## Base projection
PTS_base weighted mean:
- Season: 40%
- Last 10: 25%
- Last 5: 20%
- Last 3: 15%

Primary signals:
- MIN
- ATT / usage / shot volume
- Efficiency

Secondary signals:
- Opponent matchup
- Pace
- Roster / role
- Volatility

## Signal logic
Working thresholds currently being tested:
- BET A: |edge| >= 2.0 AND at least 3 main signals confirm direction
- BET B: |edge| >= 1.0 AND strong confirmation
- Otherwise: NO BET

These are still calibration thresholds, not final optimized production thresholds.

## Edge buckets to track
Mandatory test buckets:
- 0.0–1.0 control group
- 1.0+
- 1.5+
- 2.0+
- 2.5+
- 3.0+

Also track positive and negative edges separately.

## Evaluation rules
- Central line only for official grading.
- DNP / did not play: exclude from W/L.
- Keep NO BET cases as a control group.
- Never optimize by removing losing examples after the fact.
- Lock prediction before checking actual result.
- Track full available offer when possible, not cherry-picked players.
- Lower/higher alternate lines and odds may be stored, but Model 1.0 is graded on the central line only.

## Training / validation
Training focus:
- EuroLeague 2024/25 historical sample

Additional seasons:
- 2025/26 to expand sample and validate robustness
- 2026/27 current season for forward / live validation

Target:
- At least 1,000 graded BET examples before strong conclusions.
- Prefer 2,000+ total evaluated cases if available.
- Desired valid-edge hit rate target discussed: >=65%, but this is a target to test, not an assumed result.
- Control group should remain near market baseline (~50%) if model separation is real.

## Data sources
- Historical bookmaker PDF offers
- Mozzart / other Serbian sportsbook archived offers where available
- EuroLeague player boxscores
- Play-by-play
- Possessions
- Minutes
- Attempts / usage proxies
- Efficiency metrics
- Opponent and pace data
- Line movement when available

## Current historical dataset already created
Known file:
- euroleague_2024_25_model20_line_move_backtest.csv

Known fields include:
season, round, date, player, team, line, under_odds, over_odds, bookmaker, source, verified, game_player, projection, edge, actual_pts, prior_games, actual_over, prev_line, line_move

## Model development roadmap
MODEL 1.0:
- MIN
- ATT
- efficiency
- opponent/pace correction
- raw edge
- signal confirmation

MODEL 2.x experiments:
- threshold calibration
- line-move analysis
- edge bins
- stronger signal confirmation rules

MODEL 3.0 planned:
- matchup detail
- expected lineups / starting five
- minutes trend over last 5
- player role changes
- lineup context

MODEL 4.0 planned:
- news / injury / roster information layer

## Important project rules
DO NOT:
- Mix post-game information into pre-game projection.
- Change formula because one result lost.
- Grade on alternate lines instead of the central line.
- Delete NO BET cases.
- Use tiny samples to declare success.
- Treat model projection alone as enough without checking signal confirmation.
- Mix ACB results directly into EuroLeague grading without an explicit cross-league design decision.

## ACB usage
ACB / Liga Endesa data may be added as contextual player-form information for players who also play EuroLeague.

Important:
- ACB should not automatically be merged into EuroLeague model weights.
- Domestic-league pace, role and minutes can differ from EuroLeague.
- Any ACB contribution must be tested as a separate feature / context layer before becoming part of a locked model version.

## Current open questions
- Exact optimal edge threshold
- Whether UNDER and OVER need different thresholds
- How many confirming signals are optimal
- Whether line movement improves selection quality
- How to weight matchup and pace
- Whether short-term minute / usage trend should receive explicit weighting
- How ACB contextual data should be normalized before use

## Current next step
1. Preserve this master state.
2. Continue expanding the historical EuroLeague offer/backtest dataset.
3. Calibrate hit rate by edge bucket.
4. Compare BET vs NO BET/control.
5. Separate OVER vs UNDER performance.
6. Only after enough sample, lock the next version.

## Change-control rule
Whenever a model rule is changed:
- Increment version or sub-version.
- Record the old rule.
- Record the new rule.
- Record why it changed.
- Record sample size used for the decision.
- Never overwrite history silently.

## ACB pipeline status — 2026-10-04
- Official ACB API client added in radicaaa87-cyber/euroleague-analytics.
- Supported pull: matchweeks, matches, official player boxscores, optional play-by-play.
- ACB 2026/27 edition mapping added (edition_id 91).
- Model-ready ACB player_game_logs.csv builder added.
- ACB↔EuroLeague player identity bridge added.
- Separate EL L5 / ACB L5 recent-form builder added; leagues are not averaged together.
- GitHub Actions workflow added: .github/workflows/acb-pull.yml.
- Current ACB frontend uses X-Apikey on the current api2.acb.com seasondata/matchdata API. Repository secret required: ACB_API_KEY.

- 2026-10-04 update: ACB client migrated from legacy openapilive/Bearer flow to current X-Apikey API; boxscore, play-by-play, shots and official advanced-stats endpoints wired into the pull workflow.
