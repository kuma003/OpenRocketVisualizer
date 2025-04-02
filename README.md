# OpenRocket Visualizer
OpenRocketのシミュレーションをアニメーションで描画するためのソフトウェア.


## Installation
pipとJAVAがインストールされているのが前提です.  
JAVAのバージョンが古いとOpenRocketのjarファイル(後述)を上手く読み込めないので, なるべく最新のものをインストールしてください
(インストールの詳細は詳しい人に聞いてください).
```bash
# Clone the repository
git clone https://github.com/yourusername/ScienceDayPy.git
# or you can install from github directly

# Navigate to the project directory
cd ScienceDayPy

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
また, OpenRocketの実行ファイルが必要です.
ディレクトリ直下にjarファイルがない場合は実行時に自動でDLされますが, 必要に応じて手動でDLしてください.

## Requirements

- Python 3.10+ : match記法を使うため

他はrequirements.txtを参照ください.
pythonやpipはすべて最新にすれば問題ないと思います.


## File Structures
- ```main.py``` : メインの実行ファイル.
- ```setttings.toml``` : 設定ファイル. シミュレーション諸元などもここに.
- ```requirements.txt``` : 依存関係.

## For Developer
ぜひIssuesから着手してください.

formatterはblackを使っています.
[Qiitaの記事](https://qiita.com/tsu_0514/items/2d52c7bf79cd62d4af4a)などを参照して, vs codeに導入するのを推奨します.

