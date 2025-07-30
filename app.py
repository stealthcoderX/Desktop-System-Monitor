from flask import Flask, render_template_string
import psutil, time, os

app = Flask(__name__)

HTML = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Desktop System Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; background: #e0e7ef; margin: 0; }
        .container { max-width: 1200px; margin: 32px auto; background: #fff; border-radius: 32px; box-shadow: 0 8px 32px #b0c4de55; padding: 40px; }
        h2 { color: #3a4a6b; font-size: 2.2em; margin-bottom: 32px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 32px; }
        th, td { text-align: left; padding: 12px 18px; border-bottom: 1px solid #e0e7ef; }
        th { background: #f7f8fa; color: #3a4a6b; }
        tr:last-child td { border-bottom: none; }
        .metric-bar { width: 100%; height: 16px; border-radius: 8px; background: #e0e7ef; margin-top: 6px; }
        .bar-inner { height: 100%; border-radius: 8px; background: #3a4a6b; transition: width 0.7s; }
        .gamer-section { background: #f7f8fa; border-radius: 24px; padding: 24px; margin-top: 32px; border: 2px solid #b0c4de; }
        .refresh { margin-top: 24px; color: #3a4a6b; text-align: right; }
    </style>
    <meta http-equiv="refresh" content="2">
    <script>
        window.onload = function() {
            var bars = document.querySelectorAll('.bar-inner');
            bars.forEach(function(bar) {
                var width = bar.getAttribute('data-width');
                bar.style.width = width + '%';
            });
            var uptimeSpan = document.getElementById('uptime');
            if (uptimeSpan) uptimeSpan.innerText = formatUptime({{ uptime }});
        };
        function formatUptime(seconds) {
            var h = Math.floor(seconds/3600);
            var m = Math.floor((seconds%3600)/60);
            var s = Math.floor(seconds%60);
            return h + 'h ' + m + 'm ' + s + 's';
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>Desktop System Monitor</h2>
        <table>
            <tr><th>Metric</th><th>Value</th><th>Usage</th></tr>
            <tr><td>CPU Usage</td><td>{{ cpu }}%</td><td><div class="metric-bar"><div class="bar-inner" data-width="{{ cpu }}"></div></div></td></tr>
            <tr><td>Memory Usage</td><td>{{ memory }}%</td><td><div class="metric-bar"><div class="bar-inner" data-width="{{ memory }}"></div></div></td></tr>
            <tr><td>Disk Usage (C:)</td><td>{{ disk_usage }}%</td><td><div class="metric-bar"><div class="bar-inner" data-width="{{ disk_usage }}"></div></div></td></tr>
            <tr><td>CPU Cores</td><td>{{ cpu_cores }} / {{ cpu_threads }}</td><td></td></tr>
            <tr><td>CPU Frequency</td><td>{{ cpu_freq }} MHz</td><td></td></tr>
            <tr><td>Total RAM</td><td>{{ total_ram }} GB</td><td></td></tr>
            <tr><td>Available RAM</td><td>{{ available_ram }} GB</td><td></td></tr>
            <tr><td>Total Disk (C:)</td><td>{{ total_disk }} GB</td><td></td></tr>
            <tr><td>Free Disk (C:)</td><td>{{ free_disk }} GB</td><td></td></tr>
        </table>
        <div class="gamer-section">
            <ul style="list-style:none; padding:0; margin:0;">
                <li>Tip: Keep CPU and RAM usage below 80% for best gaming.</li>
                <li>System Uptime: <span id="uptime"></span></li>
                <li>Active Processes: {{ processes }}</li>
                <li>Top 3 Memory Apps:
                    <ol>
                        {% for proc in top_procs %}
                        <li>{{ proc['name'] }} ({{ proc['mem'] }} MB)</li>
                        {% endfor %}
                    </ol>
                </li>
            </ul>
        </div>
        <div class="refresh">(Auto-refreshes every 2 seconds)</div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq()
        cpu_freq = round(freq.current, 1) if freq else 'N/A'
        mem = psutil.virtual_memory()
        total_ram = round(mem.total / (1024**3), 2)
        available_ram = round(mem.available / (1024**3), 2)
        # Detect disk path based on OS
        disk_path = 'C:\\' if os.name == 'nt' else '/'
        disk = psutil.disk_usage(disk_path)
        disk_usage = disk.percent
        total_disk = round(disk.total / (1024**3), 2)
        free_disk = round(disk.free / (1024**3), 2)
        uptime = int(time.time() - psutil.boot_time())
        processes = len(psutil.pids())
        top_procs = []
        for p in psutil.process_iter(['name', 'memory_info']):
            try:
                mem_mb = int(p.info['memory_info'].rss / (1024*1024))
                top_procs.append({'name': p.info['name'], 'mem': mem_mb})
            except Exception:
                continue
        top_procs = sorted(top_procs, key=lambda x: x['mem'], reverse=True)[:3]
        return render_template_string(
            HTML,
            cpu=cpu,
            memory=memory,
            cpu_cores=cpu_cores,
            cpu_threads=cpu_threads,
            cpu_freq=cpu_freq,
            total_ram=total_ram,
            available_ram=available_ram,
            disk_usage=disk_usage,
            total_disk=total_disk,
            free_disk=free_disk,
            uptime=uptime,
            processes=processes,
            top_procs=top_procs
        )
    except Exception as e:
        return f"<h2>Internal Server Error</h2><pre>{e}</pre>", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)