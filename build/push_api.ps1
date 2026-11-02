# 以 GitHub REST API 推送本機 commit（github.com:443 目前不可達，api.github.com 可達）
# 不印出 token；只印進度。
$ErrorActionPreference = 'Stop'
$env:GIT_TERMINAL_PROMPT = '0'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8

$cred = $null
$token = $env:GH_TOKEN
if (-not $token) {
  $cred = "protocol=https`nhost=github.com`n`n" | git credential fill 2>$null
  $token = ($cred | Where-Object { $_ -like 'password=*' }) -replace '^password=', ''
}
if (-not $token) { throw 'no token' }
$headers = @{ Authorization = "Bearer $token"; 'User-Agent' = 'dsh'; Accept = 'application/vnd.github+json' }
$repo = 'accelon/sdp'
$api = "https://api.github.com/repos/$repo"

function PostJson($url, $obj) {
  $json = $obj | ConvertTo-Json -Depth 10 -Compress
  $bytes = [Text.Encoding]::UTF8.GetBytes($json)
  Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $bytes -ContentType 'application/json; charset=utf-8' -TimeoutSec 120
}

# 0) 空 repo 不能建 blob（409）：先用 Contents API 建第一個 commit
$repoInfo = Invoke-RestMethod -Uri $api -Headers $headers -TimeoutSec 60
$baseCommit = $null
try {
  $ref = Invoke-RestMethod -Uri "$api/git/ref/heads/main" -Headers $headers -TimeoutSec 60
  $baseCommit = $ref.object.sha
  Write-Output "base $baseCommit"
} catch {
  $readmePath = Join-Path 'D:\2026\sdp' 'README.md'
  $readmeText = [IO.File]::ReadAllText($readmePath, [Text.Encoding]::UTF8).Replace("`r`n", "`n")
  $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($readmeText))
  $init = Invoke-RestMethod -Uri "$api/contents/README.md" -Method Put -Headers $headers `
    -Body ([Text.Encoding]::UTF8.GetBytes((@{ message = '初始化 sdp 工作區'; content = $b64 } | ConvertTo-Json -Compress))) `
    -ContentType 'application/json; charset=utf-8' -TimeoutSec 120
  $baseCommit = $init.commit.sha
  Write-Output "init $baseCommit (README.md)"
}

# 1) 本機 HEAD 的檔案清單（blob sha + 路徑）
$tree = @()
$entries = git -c core.quotepath=false ls-tree -r HEAD
foreach ($line in $entries) {
  if ($line -notmatch '^(\d+) blob ([0-9a-f]+)\t(.+)$') { continue }
  $mode = $Matches[1]; $sha = $Matches[2]; $path = $Matches[3]
  $full = Join-Path 'D:\2026\sdp' $path
  $data = [IO.File]::ReadAllBytes($full)
  if ($path -notmatch '\.(jpg|jpeg|png|woff2?|zip)$') {
    $text = [Text.Encoding]::UTF8.GetString($data)
    if ($text.Contains("`r`n")) {
      $data = [Text.Encoding]::UTF8.GetBytes($text.Replace("`r`n", "`n"))
    }
  }
  $b64 = [Convert]::ToBase64String($data)
  $blob = PostJson "$api/git/blobs" @{ content = $b64; encoding = 'base64' }
  $tree += @{ path = $path; mode = $(if ($mode -eq '100755') { '100755' } else { '100644' }); type = 'blob'; sha = $blob.sha }
  Write-Output ("blob {0} {1}" -f $path, $blob.sha.Substring(0, 8))
}

# 2) tree（以現有 commit 的 tree 為基底）
$baseTree = (Invoke-RestMethod -Uri "$api/git/commits/$baseCommit" -Headers $headers -TimeoutSec 60).tree.sha
$newTree = PostJson "$api/git/trees" @{ base_tree = $baseTree; tree = $tree }
Write-Output "tree $($newTree.sha)"

# 3) commit
$msg = (git log -1 --pretty=%B) -join "`n"
$msg = $msg.TrimEnd()
$now = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$commit = PostJson "$api/git/commits" @{
  message = $msg
  tree    = $newTree.sha
  parents = @($baseCommit)
  author  = @{ name = 'yapcheahshen'; email = 'yapcheahshen@gmail.com'; date = $now }
  committer = @{ name = 'yapcheahshen'; email = 'yapcheahshen@gmail.com'; date = $now }
}
Write-Output "commit $($commit.sha)"

# 4) ref（快轉）
$body = [Text.Encoding]::UTF8.GetBytes((@{ sha = $commit.sha; force = $false } | ConvertTo-Json -Compress))
$ref = Invoke-RestMethod -Uri "$api/git/refs/heads/main" -Method Patch -Headers $headers -Body $body -ContentType 'application/json; charset=utf-8' -TimeoutSec 60
Write-Output "ref $($ref.ref) -> $($ref.object.sha.Substring(0, 12))"
