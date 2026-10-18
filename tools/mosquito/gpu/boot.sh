#!/bin/bash
# Vultr startup script (Ubuntu 24.04 + NVIDIA GPU). Placeholders are filled by deploy step:
#   __IP__ sandbox IP allowed on 443, __TOKEN__ bearer token, __CERT_B64__/__KEY_B64__ pinned TLS cert, __JOBS_B64__ run_jobs.py
# Read-only: the box serves /root/out and /var/log/*.log over HTTPS GET with a token. No remote command execution.
exec >>/var/log/setup.log 2>&1
set -x
export DEBIAN_FRONTEND=noninteractive
mkdir -p /root/ctl /root/out
echo __CERT_B64__ | base64 -d > /root/ctl/cert.pem
echo __KEY_B64__ | base64 -d > /root/ctl/key.pem
echo __JOBS_B64__ | base64 -d > /root/run_jobs.py
echo -n __TOKEN__ > /root/ctl/token
chmod 600 /root/ctl/*

cat > /root/ctl/serve.py <<'PY'
import http.server, ssl, os
TOKEN = open('/root/ctl/token').read().strip()
ROOTS = {'out': '/root/out', 'setup.log': '/var/log/setup.log', 'jobs.log': '/var/log/jobs.log', 'comfy.log': '/var/log/comfy.log'}
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Authorization') != 'Bearer ' + TOKEN:
            self.send_response(403); self.end_headers(); return
        parts = self.path.strip('/').split('/')
        p = ROOTS.get(parts[0])
        if p and parts[0] == 'out':
            name = os.path.basename('/'.join(parts[1:]))
            p = '/root/out/' + name if name else None
            if p is None:
                d = '\n'.join(f'{f} {os.path.getsize("/root/out/"+f)}' for f in sorted(os.listdir('/root/out'))).encode()
            else:
                d = open(p, 'rb').read() if os.path.isfile(p) else None
        elif p:
            d = open(p, 'rb').read()[-60000:] if os.path.isfile(p) else b''
        else:
            d = None
        if d is None: self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header('Content-Length', str(len(d))); self.end_headers(); self.wfile.write(d)
c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); c.load_cert_chain('/root/ctl/cert.pem', '/root/ctl/key.pem')
s = http.server.ThreadingHTTPServer(('0.0.0.0', 443), H); s.socket = c.wrap_socket(s.socket, server_side=True); s.serve_forever()
PY
cat > /etc/systemd/system/serve.service <<'U'
[Service]
ExecStart=/usr/bin/python3 /root/ctl/serve.py
Restart=always
[Install]
WantedBy=multi-user.target
U

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow from __IP__ to any port 443 proto tcp
ufw --force enable
systemctl daemon-reload; systemctl enable --now serve

cat > /root/setup2.sh <<'S2'
#!/bin/bash
exec >>/var/log/setup.log 2>&1
set -x
cd /root
[ -d ComfyUI ] || git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3 -m venv /root/venv
/root/venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
/root/venv/bin/pip install -r requirements.txt
H=https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files
mkdir -p models/diffusion_models models/text_encoders models/vae
aria2c -x8 -s8 -c -d models/diffusion_models -o wan2.2_ti2v_5B_fp16.safetensors $H/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors
aria2c -x8 -s8 -c -d models/text_encoders -o umt5_xxl_fp8_e4m3fn_scaled.safetensors $H/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors
aria2c -x8 -s8 -c -d models/vae -o wan2.2_vae.safetensors $H/vae/wan2.2_vae.safetensors
nohup /root/venv/bin/python main.py --listen 127.0.0.1 --port 8188 > /var/log/comfy.log 2>&1 &
echo SETUP_DONE
nohup python3 /root/run_jobs.py 1 > /var/log/jobs.log 2>&1 &
S2
chmod +x /root/setup2.sh

apt-get update
apt-get install -y git python3-venv python3-pip ffmpeg aria2 curl ubuntu-drivers-common
if ! nvidia-smi; then
  ubuntu-drivers install --gpgpu
  # resume after reboot
  cat > /etc/systemd/system/setup2.service <<'U'
[Service]
Type=oneshot
RemainAfterExit=yes
KillMode=process
ExecStart=/root/setup2.sh
[Install]
WantedBy=multi-user.target
U
  systemctl enable setup2
  echo DRIVER_INSTALLED_REBOOT
  (sleep 5; reboot) &
  exit 0
fi
nohup /root/setup2.sh &
