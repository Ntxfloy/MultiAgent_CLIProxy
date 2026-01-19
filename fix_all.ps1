$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$toolsPath = Join-Path $ScriptDir "tools\file_ops.py"

$toolsContent = @'
import os
from pathlib import Path

# Корень рабочего пространства
BASE_DIR = Path(__file__).parent.parent.resolve()
WORKSPACE_ROOT = BASE_DIR / 'workspace'
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file in the workspace."""
    try:
        full_path = (WORKSPACE_ROOT / filepath).resolve()
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'File {filepath} written successfully.'
    except Exception as e:
        return f'Error writing file: {str(e)}'

def read_file(filepath: str) -> str:
    """Reads content from a file in the workspace."""
    try:
        full_path = (WORKSPACE_ROOT / filepath).resolve()
        if not full_path.exists():
            return f'Error: File {filepath} not found.'
        return full_path.read_text(encoding='utf-8')
    except Exception as e:
        return f'Error reading file: {str(e)}'

def list_files(directory: str = '.') -> str:
    """Lists all files in a directory within the workspace."""
    try:
        target_dir = (WORKSPACE_ROOT / directory).resolve()
        if not target_dir.exists():
            return f'Error: Directory {directory} not found.'
        files = [str(p.relative_to(WORKSPACE_ROOT)) for p in target_dir.rglob('*') if p.is_file()]
        return '\n'.join(files) if files else 'Directory is empty.'
    except Exception as e:
        return f'Error listing files: {str(e)}'
'@

Set-Content -Path $toolsPath -Value $toolsContent -Encoding UTF8
Write-Host "✅ Fixed: $toolsPath" -ForegroundColor Green