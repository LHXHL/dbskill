param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("create", "target", "remove", "test", "list")]
  [string]$Action,

  [Parameter(Mandatory = $true)]
  [string]$Path,

  [string]$Target
)

$ErrorActionPreference = "Stop"

function Get-ManagedLink([string]$LiteralPath) {
  $item = Get-Item -LiteralPath $LiteralPath -Force -ErrorAction SilentlyContinue
  if ($null -eq $item) {
    return $null
  }

  if ($item.LinkType -in @("Junction", "SymbolicLink")) {
    return $item
  }

  $isReparsePoint = ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
  if ($isReparsePoint -and $item.PSIsContainer) {
    return $item
  }

  return $null
}

function Get-ManagedLinkTarget($Item) {
  $linkTarget = @($Item.Target)[0]
  if (-not [string]::IsNullOrWhiteSpace($linkTarget)) {
    if (-not [System.IO.Path]::IsPathRooted($linkTarget)) {
      $linkTarget = Join-Path $Item.Parent.FullName $linkTarget
    }
    return [System.IO.Path]::GetFullPath($linkTarget)
  }

  $resolveMethod = $Item.GetType().GetMethod("ResolveLinkTarget", [type[]]@([bool]))
  if ($null -ne $resolveMethod) {
    $resolved = $Item.ResolveLinkTarget($false)
    if ($null -ne $resolved) {
      return $resolved.FullName
    }
  }

  return $null
}

switch ($Action) {
  "create" {
    if ([string]::IsNullOrWhiteSpace($Target)) {
      throw "create 操作缺少 Target"
    }

    if (Test-Path -LiteralPath $Path -PathType Any) {
      throw "目标已经存在：$Path"
    }

    New-Item -ItemType Junction -Path $Path -Target $Target | Out-Null
    $item = Get-ManagedLink $Path
    if ($null -eq $item) {
      throw "Junction 创建后校验失败：$Path"
    }
  }

  "target" {
    $item = Get-ManagedLink $Path
    if ($null -eq $item) {
      exit 1
    }

    $linkTarget = Get-ManagedLinkTarget $item
    if ([string]::IsNullOrWhiteSpace($linkTarget)) {
      exit 1
    }

    $linkTarget
  }

  "remove" {
    $item = Get-ManagedLink $Path
    if ($null -eq $item) {
      throw "拒绝删除非 Junction／SymbolicLink 路径：$Path"
    }

    $item.Delete()
  }

  "test" {
    if ($null -eq (Get-ManagedLink $Path)) {
      exit 1
    }
  }

  "list" {
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
      exit 0
    }

    Get-ChildItem -LiteralPath $Path -Force |
      Where-Object {
        $_.LinkType -in @("Junction", "SymbolicLink") -or
        (($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -and $_.PSIsContainer)
      } |
      ForEach-Object { $_.FullName }
  }
}
