# Reading Shane Telescope PostgreSQL Dumps

## What You Have

Steve Allen has provided dumps from the Shane telescope's PostgreSQL database. These are text files containing database records that document:
- Keywords tracked by various systems (keygrabber instances)
- How those keywords map to FITS headers in telescope images
- Metadata about what each keyword means

## File Types

### 1. Dump Files (*.dump)

**What it is:** A PostgreSQL dump file is a text file containing SQL commands that recreate database tables.

**Format:** Created with:
```bash
pg_dump --table=<table_name> keywordlog > <table_name>.dump
```

**What's inside:** Plain text records, one per line, tab-separated values representing database rows.

**Size note:** The `shanepoco` dump is very large (takes >24 hours to create and covers multiple years of data).

### 2. Keyword Definition Files

**gshowmet3apflonghelp** and **gshowpocolonghelp**

These are documentation files created with:
```bash
gshow -s met3apf -longhelp > gshowmet3apflonghelp
gshow -s poco -longhelp > gshowpocolonghelp
```

They contain library documentation explaining what each KTL (Keyword Translation Layer) keyword means and how it's used.

### 3. pocokwd2db File

A reference file documenting:
- How KTL keywords are mapped to FITS WCS (World Coordinate System) keywords
- Which keywords should be monitored for changes
- How values translate between the KTL vocabulary and standard astronomical conventions

## How to Read These Files in Python

### Reading Dump Files

```python
import pandas as pd

# Read a PostgreSQL dump file as tab-separated values
df = pd.read_csv('tablename.dump', sep='\t', header=None)

# Or using a streaming approach for very large files:
chunks = pd.read_csv('tablename.dump', sep='\t', header=None, chunksize=10000)
for chunk in chunks:
    # Process each chunk
    print(chunk.head())
```

### Reading Keyword Definition Files

```python
# Simple text file reading
with open('gshowpocolonghelp', 'r') as f:
    content = f.read()
    print(content)

# Or parse it into a structured format if it has consistent formatting
lines = content.split('\n')
```

### Parsing pocokwd2db

```python
# Read as a configuration or reference file
with open('pocokwd2db', 'r') as f:
    lines = f.readlines()
    
# Extract actual content vs comments
keywords = [line for line in lines if not line.strip().startswith('#')]
```

## Next Steps

1. **Explore the structure** of individual dump files to understand column meanings
2. **Parse keyword definitions** to create a lookup table of keyword → meaning
3. **Map POCO keywords** to FITS WCS standards using pocokwd2db
4. **Combine data** to create a comprehensive metadata registry for Shane observations

## Notes

- Dump files are text-based and can be very large; process in chunks if needed
- The keyword documentation files are human-readable but may have inconsistent formatting
- All files are essentially text/ASCII and don't require binary parsing
