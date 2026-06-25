module.exports = {
  apps: [{
    name: 'rarayvision-backend',
    script: '/usr/bin/python3',
    args: '-m uvicorn backend.main:app --host 0.0.0.0 --port 5000',
    cwd: '/www/wwwroot/rarayvision.dfs.co.id',
    interpreter: 'none',
    watch: false,
    env: { NODE_ENV: 'production' }
  }]
}