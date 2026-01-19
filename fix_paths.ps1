$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$toolsPath = Join-Path $ScriptDir "tools\file_ops.py"

$toolsContent = @'
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
WORKSPACE_ROOT = BASE_DIR / 'workspace'
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

def _clean_path(path: str) -> Path:
    # Убираем типичные артефакты путей AI-агентов
    p = path.replace('\\', '/').replace('/tmp/workspace/', '').lstrip('/')
    return (WORKSPACE_ROOT / p).resolve()

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file. filepath is relative to workspace root."""
    try:
        full_path = _clean_path(filepath)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        return f'File {filepath} written successfully to workspace.'
    except Exception as e:
        return f'Error: {str(e)}'

def read_file(filepath: str) -> str:
    """Reads content from a file."""
    try:
        full_path = _clean_path(filepath)
        return full_path.read_text(encoding='utf-8')
    except Exception as e:
        return f'Error: {str(e)}'

def list_files(directory: str = '.') -> str:
    """Lists files recursively."""
    try:
        target_dir = _clean_path(directory)
        files = [str(p.relative_to(WORKSPACE_ROOT)) for p in target_dir.rglob('*') if p.is_file()]
        return '\n'.join(files) if files else 'Directory is empty.'
    except Exception as e:
        return f'Error: {str(e)}'
'@

Set-Content -Path $toolsPath -Value $toolsContent -Encoding UTF8
Write-Host "✅ Tools are now Agent-Proof!" -ForegroundColor Green