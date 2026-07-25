"""Start academic-agent with DeepSeek settings loaded from env/Windows."""
import os
import subprocess
import sys


def read_windows_env(var_name: str) -> str:
    for scope in ("Machine", "User"):
        r = subprocess.run(
            [
                'powershell.exe',
                '-NoProfile',
                '-Command',
                f'[Environment]::GetEnvironmentVariable("{var_name}","{scope}")',
            ],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
        )
        value = r.stdout.strip()
        if value:
            return value
    return ""


key = (
    os.environ.get('LLM_API_KEY', '').strip()
    or os.environ.get('OPENAI_API_KEY', '').strip()
    or os.environ.get('CARAGENT_LLM_API_KEY', '').strip()
    or read_windows_env('CARAGENT_LLM_API_KEY')
    or read_windows_env('CUSTOM_OPENAI_API_KEY')
)

if not key:
    print('ERROR: missing LLM API key. Checked LLM_API_KEY / OPENAI_API_KEY / CARAGENT_LLM_API_KEY / CUSTOM_OPENAI_API_KEY')
    sys.exit(1)

base_url = (
    os.environ.get('LLM_BASE_URL', '').strip()
    or os.environ.get('OPENAI_API_BASE', '').strip()
    or 'https://api.deepseek.com/v1'
)
model = os.environ.get('LLM_MODEL', '').strip() or 'deepseek-v4-flash'

os.environ['LLM_API_KEY'] = key
os.environ['OPENAI_API_KEY'] = key
os.environ['CARAGENT_LLM_API_KEY'] = key
os.environ['LLM_BASE_URL'] = base_url
os.environ['OPENAI_API_BASE'] = base_url
os.environ['LLM_MODEL'] = model
print(f'LLM ready: model={model}, base={base_url}, key_len={len(key)}')

result = subprocess.run(
    [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8080'],
    cwd='/mnt/d/AI项目/xueshuagent')
sys.exit(result.returncode)
