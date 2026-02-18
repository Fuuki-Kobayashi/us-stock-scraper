# US Stock Surge Analyzer

米国株の急騰銘柄を自動検出・追跡・分析するWebアプリケーション。

Polygon.io API（Free tier）を使用して、設定した閾値（デフォルト+20%）以上の日次変動を示した銘柄を検出し、急騰後のパフォーマンス（1日/3日/7日/30日後）を自動追跡します。

## 主な機能

| 機能 | 説明 |
|------|------|
| 急騰検出 | 全銘柄OHLCVから閾値以上の銘柄を自動検出 |
| 追跡分析 | 急騰後1日/3日/7日/30日のパフォーマンスを追跡 |
| 統計ダッシュボード | セクター別・曜日別・月次トレンド・リピーターランキング |
| 閾値設定 | UI上で急騰判定の閾値を変更可能（デフォルト20%） |
| チャート | TradingView Lightweight Chartsでローソク足+出来高を表示 |
| 検索 | Cmd+K でティッカー・会社名をファジー検索 |
| バックフィル | 過去データの一括取得（Admin画面から実行） |

## 技術スタック

| Layer | Technology |
|-------|-----------|
| バックエンド | FastAPI (Python 3.11+) |
| フロントエンド | Next.js 15 (TypeScript) |
| データベース | SQLite (WALモード) |
| チャート | TradingView Lightweight Charts |
| UI | shadcn/ui + Tailwind CSS (ダークテーマ) |
| 状態管理 | Zustand (UI) + React Query (サーバー) |
| スケジューラ | APScheduler |
| API | Polygon.io Free tier (5 req/min) |

## 必要な環境

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/)（Pythonパッケージ管理）
- [Polygon.io APIキー](https://polygon.io/)（無料アカウントでOK）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/Fuuki-Kobayashi/us-stock-scraper.git
cd us-stock-scraper
```

### 2. 環境変数を設定

```bash
cp .env.example .env
```

`.env` を編集して Polygon.io APIキーを設定：

```
POLYGON_API_KEY=your_polygon_api_key_here
DATABASE_URL=sqlite+aiosqlite:///data/stocks.db
SURGE_THRESHOLD_PCT=20.0
```

### 3. バックエンドのセットアップ

```bash
cd backend
uv sync
```

### 4. フロントエンドのセットアップ

```bash
cd frontend
npm install
```

## 起動方法

### ローカル起動（推奨）

ターミナルを2つ開いて、それぞれ実行：

**バックエンド（ポート8000）：**

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**フロントエンド（ポート3000）：**

```bash
cd frontend
npm run dev
```

ブラウザで http://localhost:3000 にアクセスするとダッシュボードが表示されます。

### Docker Compose で起動

```bash
docker compose up --build
```

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## 使い方

### 初回データ収集

1. http://localhost:3000/admin にアクセス
2. 「Manual Collection」で日付を選択し「Run Collection」をクリック
3. 過去データが必要な場合は「Backfill」で日付範囲を指定して「Run Backfill」をクリック

> **注意**: Free tierは5リクエスト/分の制限があります。バックフィルは1日あたり1APIコールで処理されるため、レートリミッターが自動的に制御します。

### 自動収集

バックエンド起動時にAPSchedulerが自動起動し、以下のジョブが実行されます：

| ジョブ | スケジュール | 内容 |
|--------|------------|------|
| 日次収集 | 毎日 22:00 UTC（月〜金） | Grouped Daily APIで全銘柄取得 → 閾値以上を保存 |
| ティッカー同期 | 毎週日曜 02:00 UTC | ティッカーメタデータ（セクター等）を更新 |

### 画面の説明

| ページ | URL | 内容 |
|--------|-----|------|
| ダッシュボード | `/dashboard` | サマリーカード、月次トレンド、セクター分布、曜日別分布 |
| 急騰一覧 | `/surges` | 急騰イベントのフィルタ・ソート・検索 |
| 銘柄詳細 | `/stocks/[symbol]` | ローソク足チャート、急騰履歴、追跡データ |
| 追跡分析 | `/tracking` | 急騰後パフォーマンスの統計（平均リターン、勝率） |
| 設定 | `/settings` | 急騰判定の閾値変更 |
| 管理 | `/admin` | スケジューラ状態、手動収集、バックフィル |

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | `/api/surges/` | 急騰イベント一覧（フィルタ・ページネーション対応） |
| GET | `/api/surges/today` | 当日の急騰銘柄 |
| GET | `/api/surges/{id}` | 急騰イベント詳細（追跡データ含む） |
| GET | `/api/surges/stats` | 統計（セクター別、曜日別、月次、リピーター） |
| GET | `/api/tracking/` | 急騰後パフォーマンス分析 |
| GET | `/api/tracking/by-sector` | セクター別追跡分析 |
| GET | `/api/stocks/{symbol}/chart` | OHLCV（チャート用） |
| GET | `/api/search?q=` | ティッカー検索 |
| GET | `/api/settings` | 設定取得 |
| PUT | `/api/settings` | 設定更新 |
| GET | `/api/admin/status` | スケジューラ状態 |
| POST | `/api/admin/collect` | 手動データ収集 |
| POST | `/api/admin/backfill` | ヒストリカルバックフィル |

インタラクティブなAPIドキュメントは http://localhost:8000/docs で確認できます。

## テスト

```bash
# バックエンドテスト
cd backend
uv run pytest -v

# フロントエンドビルド確認
cd frontend
npm run build
```

## Polygon.io Free tier の制約

| 項目 | 制限 |
|------|------|
| リクエスト数 | 5回/分（Token Bucketで自動制御） |
| データ種別 | EOD（終値）のみ |
| 履歴 | 過去2年分 |
| WebSocket | 利用不可（ポーリングで代替） |

## ディレクトリ構成

```
us-stock-scraper/
├── backend/
│   ├── app/
│   │   ├── data_sources/    # Polygon.io APIクライアント
│   │   ├── models/          # SQLAlchemy ORMモデル
│   │   ├── routers/         # FastAPI ルーター
│   │   ├── schemas/         # Pydantic スキーマ
│   │   ├── services/        # ビジネスロジック
│   │   ├── tasks/           # スケジューラジョブ
│   │   ├── utils/           # レートリミッター等
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js ページ
│   │   ├── components/      # UIコンポーネント
│   │   ├── hooks/           # React Query フック
│   │   ├── lib/             # APIクライアント、ユーティリティ
│   │   ├── stores/          # Zustand ストア
│   │   └── types/           # TypeScript 型定義
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```
