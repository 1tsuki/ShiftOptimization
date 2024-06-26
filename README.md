# ShiftOptimization

進化的アルゴリズムを用いて研修医の最適なシフトを生成するためのサンプルコード

## How To Use

Python3 実行環境が必要

- `python3 -m optimizer` で実行可能、パラメタ指定は以下オプションにて実施
  - `--year 2024` or `-y 2024`
  - `--month 4` or `-m 4`
  - `--er 15` or `-e 15`
  - `--icu 5` or `-i 5`
  - `--attempt 1000` or `-a 1000`
- コマンド実行例 `python3 -m optimizer -y 2024 -m 4 -e 15 -i 5 -a 10000`

- 有給取得希望は `optimizer/__main__.py` にて pto_requests を追加すれば処理可能
  - 指定の I/F が要改善だが一旦動く

## Development

- `python3 -m unittest discover tests` でテスト実行
