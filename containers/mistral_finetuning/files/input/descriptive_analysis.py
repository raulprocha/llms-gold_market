import pandas as pd

# Load
df = pd.read_csv("input/training_database.csv")

# Columns your prompt likely uses (adjust if your build_prompt differs)
PROMPT_TEXT_COLS = [
    "generated_headline",       # usually core of the prompt
    "explanation",              # supporting rationale text
    "correlation_description",  # context text
    "impact_timing_description" # timing text
]
PROMPT_META_COLS = [
    "symbol", "symbol_name", "sentiment_strength"  # often included in prompt context
]
REQUIRED_FOR_PROMPT = PROMPT_TEXT_COLS + PROMPT_META_COLS

# Target columns (not JSON yet; used later to build the assistant response)
TARGET_COLS = [
    "direction_6h","magnitude_6h",
    "direction_12h","magnitude_12h",
    "direction_24h","magnitude_24h",
    "direction_48h","magnitude_48h",
]

# 1) Basic presence check for required columns
missing_cols = [c for c in REQUIRED_FOR_PROMPT + TARGET_COLS if c not in df.columns]
if missing_cols:
    print("❌ Missing required columns:", missing_cols)

# 2) Null & blank checks (without modifying df)
null_mask = df[REQUIRED_FOR_PROMPT].isnull().any(axis=1)

def is_blank_series(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().eq("")

blank_mask = pd.DataFrame({
    c: is_blank_series(df[c]) for c in PROMPT_TEXT_COLS  # blanks in text columns are risky
}).any(axis=1)

unsafe_mask = null_mask | blank_mask
unsafe_rows = df.index[unsafe_mask]

print(f"\n🧯 Rows unsafe for prompt construction (nulls or blank text in prompt-critical cols): {unsafe_mask.sum()}")
if unsafe_mask.sum() > 0:
    print("First few unsafe row indices:", unsafe_rows[:10].tolist())
    # Optional: show why each is unsafe (first few rows)
    preview_cols = REQUIRED_FOR_PROMPT
    print("\nExample problematic rows (truncated view):")
    print(df.loc[unsafe_rows[:5], preview_cols])

# 3) Sanity check: allowed vocab in targets
ALLOWED_DIRECTIONS = {"Up", "Down", "Neutral"}
ALLOWED_MAGNITUDES = {"low impact","medium-low impact","medium-high impact","high impact"}

bad_dirs = {}
bad_mags = {}
for col in TARGET_COLS:
    vals = df[col].dropna().astype(str).str.strip()
    if "direction" in col:
        bad = set(vals.unique()) - ALLOWED_DIRECTIONS
        if bad:
            bad_dirs[col] = bad
    else:
        bad = set(vals.unique()) - ALLOWED_MAGNITUDES
        if bad:
            bad_mags[col] = bad

print("\n🧪 Unexpected direction values:", bad_dirs if bad_dirs else "None")
print("🧪 Unexpected magnitude values:", bad_mags if bad_mags else "None")

# 4) Class proportions (quick view)
from collections import Counter
dirs = []
mags = []
for c in TARGET_COLS:
    if "direction" in c:
        dirs.extend(df[c].dropna().astype(str).str.strip().tolist())
    else:
        mags.extend(df[c].dropna().astype(str).str.strip().tolist())

print("\n📊 Direction counts:", Counter(dirs))
print("📊 Magnitude counts:", Counter(mags))

# 5) What you would drop if you chose to filter (but we do NOT mutate df here)
would_drop_n = int(unsafe_mask.sum())
would_keep_n = int((~unsafe_mask).sum())
print(f"\n📝 If you dropped unsafe rows now: keep={would_keep_n}, drop={would_drop_n} (of total={len(df)})")
