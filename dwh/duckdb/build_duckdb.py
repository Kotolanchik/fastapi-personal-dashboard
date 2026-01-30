import argparse
import os

import duckdb


def main():
    parser = argparse.ArgumentParser(description="Build DuckDB views over Parquet data.")
    parser.add_argument("--parquet-dir", default="dwh/parquet", help="Parquet base directory")
    parser.add_argument("--db", default="dwh/duckdb/analytics.duckdb", help="DuckDB file")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.db), exist_ok=True)
    con = duckdb.connect(args.db)
    parquet_dir = args.parquet_dir

    con.execute(
        f"create or replace view health as select * from read_parquet('{parquet_dir}/health/*.parquet')"
    )
    con.execute(
        f"create or replace view finance as select * from read_parquet('{parquet_dir}/finance/*.parquet')"
    )
    con.execute(
        f"create or replace view productivity as select * from read_parquet('{parquet_dir}/productivity/*.parquet')"
    )
    con.execute(
        f"create or replace view learning as select * from read_parquet('{parquet_dir}/learning/*.parquet')"
    )
    con.close()


if __name__ == "__main__":
    main()
