# 基金套利提醒

每天 14:30 抓取 QDII-LOF 溢价信息，并通过 WxPusher 推送到微信。

## 本地运行

```powershell
cd "C:\Users\11025\Documents\基金套利"
python -m pip install -r requirements.txt
$env:WXPUSHER_APP_TOKEN="你的 WxPusher appToken"
$env:WXPUSHER_UID="UID_ESoc1pNAZNtEBsGrSjbmHQzri9ni"
python alert.py
```

可选参数：

```powershell
$env:PREMIUM_THRESHOLD="0.02"
$env:MAX_ITEMS="10"
$env:DEBUG="1"
```

## GitHub Actions 自动推送

把本目录上传到 GitHub 仓库后，进入：

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

添加：

```text
WXPUSHER_APP_TOKEN = 你的 WxPusher appToken
WXPUSHER_UID = UID_ESoc1pNAZNtEBsGrSjbmHQzri9ni
```

`.github/workflows/fund-arb-alert.yml` 已配置为北京时间周一到周五 14:30 自动运行。

如果要立即测试，进入 GitHub 仓库的 `Actions` 页面，选择 `fund-arb-alert`，点击 `Run workflow`。
