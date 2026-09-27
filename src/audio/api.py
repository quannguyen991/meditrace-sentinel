"""Small dependency-free HTTP API and review UI for the audio intake MVP."""

from __future__ import annotations

import argparse
import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .pipeline import AudioPipeline
from .storage import SessionNotFound, SessionStore

UI = r'''<!doctype html><html lang="vi"><meta charset="utf-8"><title>MediTrace Audio Intake</title>
<style>body{font:16px system-ui;max-width:920px;margin:40px auto;color:#20242a}button,select,input{font:inherit;padding:8px;margin:4px}section{border:1px solid #ddd;border-radius:10px;padding:18px;margin:16px 0}.seg{padding:12px 0;border-top:1px solid #eee}.muted{color:#667085}.danger{color:#b42318}#timer{font-size:2rem}</style>
<h1>Ghi âm ca khám</h1><section><button id="start">Bắt đầu ghi âm</button><button id="pause" disabled>Tạm dừng</button><button id="stop" disabled>Kết thúc</button><div id="timer">00:00:00</div><p id="state" class="muted">Chưa có phiên ghi âm</p><input id="file" type="file" accept="audio/*"><button id="upload">Tải audio lên</button></section>
<section><h2>Trạng thái xử lý</h2><pre id="steps">Chưa bắt đầu</pre><button id="process" disabled>Xử lý audio</button></section><section><h2>Kiểm tra transcript</h2><audio id="player" controls style="width:100%"></audio><div id="transcript" class="muted">Chưa có transcript</div><button id="send" disabled>Chuẩn bị input cho MediTrace</button><pre id="result"></pre></section>
<script>
let sid=null,rec,parts=[],started,clock; const $=id=>document.getElementById(id); const status=t=>$('state').textContent=t;
function tick(){let s=Math.floor((Date.now()-started)/1000);$('timer').textContent=new Date(s*1000).toISOString().slice(11,19)}
async function create(){let r=await fetch('/sessions',{method:'POST'});sid=(await r.json()).session_id;return sid}
$('start').onclick=async()=>{try{await create();let stream=await navigator.mediaDevices.getUserMedia({audio:true});await fetch('/sessions/'+sid+'/recording/start',{method:'POST'});rec=new MediaRecorder(stream,{mimeType:'audio/webm'});parts=[];rec.ondataavailable=e=>e.data.size&&parts.push(e.data);rec.onstop=async()=>{clearInterval(clock);await fetch('/sessions/'+sid+'/recording/stop',{method:'POST'});status('Đã ghi âm cuộc khám');let data=new Blob(parts,{type:'audio/webm'});await fetch('/sessions/'+sid+'/audio',{method:'POST',headers:{'Content-Type':'audio/webm','X-Filename':'raw.webm'},body:data});$('process').disabled=false};rec.start();started=Date.now();clock=setInterval(tick,250);$('start').disabled=true;$('pause').disabled=false;$('stop').disabled=false;status('Đang ghi âm')}catch(e){status('Không thể truy cập microphone: '+e.message)}};
$('pause').onclick=()=>{if(rec.state==='recording'){rec.pause();$('pause').textContent='Tiếp tục';status('Đã tạm dừng')}else{rec.resume();$('pause').textContent='Tạm dừng';status('Đang ghi âm')}};$('stop').onclick=()=>{rec.stop();$('pause').disabled=true;$('stop').disabled=true};
$('upload').onclick=async()=>{let f=$('file').files[0];if(!f)return status('Chọn file audio trước');await create();await fetch('/sessions/'+sid+'/audio',{method:'POST',headers:{'Content-Type':f.type||'application/octet-stream','X-Filename':f.name},body:f});$('process').disabled=false;status('Đã tải audio lên')};
$('process').onclick=async()=>{status('Đang xử lý');await fetch('/sessions/'+sid+'/process',{method:'POST'});let s;do{await new Promise(r=>setTimeout(r,300));s=await (await fetch('/sessions/'+sid)).json();$('steps').textContent=JSON.stringify(s,null,2)}while(['processing_audio','diarizing','transcribing'].includes(s.status));let t=await fetch('/sessions/'+sid+'/transcript');render(await t.json());$('send').disabled=false};
function render(items){$('player').src='/sessions/'+sid+'/audio';$('transcript').innerHTML=items.map(x=>`<div class="seg"><b>${x.speaker_id}</b> <span class="muted">${x.start_time.toFixed(2)}–${x.end_time.toFixed(2)}s</span> <button onclick="playSegment(${x.start_time},${x.end_time})">▶ Nghe lại</button><br><input data-id="${x.segment_id}" value="${x.text_original}" style="width:55%"><select data-role="${x.speaker_id}" onchange="mapRole('${x.speaker_id}',this.value)"><option value="unknown">Chưa xác định</option><option value="doctor">Bác sĩ</option><option value="patient">Bệnh nhân</option><option value="family_member">Người nhà</option><option value="other">Khác</option></select><button onclick="save('${x.segment_id}')">Lưu</button></div>`).join('')};function playSegment(a,b){let p=$('player');p.currentTime=a;p.play();let stop=()=>{if(p.currentTime>=b){p.pause();p.removeEventListener('timeupdate',stop)}};p.addEventListener('timeupdate',stop)};async function save(id){let text=document.querySelector(`input[data-id="${id}"]`).value;await fetch(`/sessions/${sid}/transcript/${id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});status('Đã lưu chỉnh sửa')};async function mapRole(speaker,role){await fetch(`/sessions/${sid}/speaker-map`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mapping:{[speaker]:role}})});status('Đã cập nhật vai trò người nói')};$('send').onclick=async()=>{$('result').textContent=JSON.stringify(await (await fetch('/sessions/'+sid+'/meditrace',{method:'POST'})).json(),null,2)};
</script></html>'''


class Handler(BaseHTTPRequestHandler):
    pipeline: AudioPipeline
    store: SessionStore

    def _json(self, value, code=200):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def _body_json(self):
        length = int(self.headers.get("Content-Length", "0")); return json.loads(self.rfile.read(length) or b"{}")

    def _error(self, exc):
        code = str(exc) or "request_failed"; status = 404 if isinstance(exc, SessionNotFound) else 400
        self._json({"error": {"code": code, "message": "Yêu cầu không thực hiện được.", "recoverable": True}}, status)

    def do_GET(self):
        path = urlparse(self.path).path.strip("/").split("/")
        try:
            if self.path == "/" or not path[0]:
                raw=UI.encode("utf-8"); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
            if len(path)==2 and path[0]=="sessions": return self._json(self.store.load(path[1]))
            if len(path)==3 and path[0]=="sessions" and path[2]=="transcript": return self._json(self.pipeline.transcript(path[1]))
            if len(path)==3 and path[0]=="sessions" and path[2]=="audio":
                session=self.store.load(path[1]); f=Path(session["raw_audio_path"]); raw=f.read_bytes(); self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(f.name)[0] or "application/octet-stream"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
            self._json({"error":"not_found"},404)
        except Exception as exc: self._error(exc)

    def do_POST(self):
        path=urlparse(self.path).path.strip("/").split("/")
        try:
            if self.path=="/sessions": return self._json(self.store.create(),201)
            if len(path)==3 and path[0]=="sessions" and path[2]=="audio":
                length=int(self.headers.get("Content-Length","0")); return self._json(self.pipeline.upload(path[1],self.rfile.read(length),self.headers.get("X-Filename","raw.webm")))
            if len(path)==4 and path[0]=="sessions" and path[2]=="recording" and path[3]=="start": return self._json(self.pipeline.start_recording(path[1]))
            if len(path)==4 and path[0]=="sessions" and path[2]=="recording" and path[3]=="stop": return self._json(self.pipeline.stop_recording(path[1]))
            if len(path)==3 and path[0]=="sessions" and path[2]=="process":
                result={"session_id":path[1],"status":"processing"}; threading.Thread(target=self._process,args=(path[1],),daemon=True).start(); return self._json(result,202)
            if len(path)==3 and path[0]=="sessions" and path[2]=="speaker-map": return self._json({"transcript":self.pipeline.map_speakers(path[1],self._body_json().get("mapping",{}))})
            if len(path)==3 and path[0]=="sessions" and path[2]=="meditrace": return self._json(self.pipeline.meditrace_input(path[1]))
            self._json({"error":"not_found"},404)
        except Exception as exc: self._error(exc)

    def _process(self, session_id):
        try: self.pipeline.process(session_id)
        except Exception: pass

    def do_PATCH(self):
        path=urlparse(self.path).path.strip("/").split("/")
        try:
            if len(path)==4 and path[0]=="sessions" and path[2]=="transcript":
                body = self._body_json()
                return self._json({"transcript":self.pipeline.edit_segment(path[1],path[3],body.get("text",""),body.get("edited_by","user"))})
            self._json({"error":"not_found"},404)
        except Exception as exc: self._error(exc)

    def log_message(self, *_): pass


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--host",default="127.0.0.1"); parser.add_argument("--port",type=int,default=8765); parser.add_argument("--data-dir",default="data/audio"); args=parser.parse_args()
    store=SessionStore(args.data_dir); Handler.store=store; Handler.pipeline=AudioPipeline(store); server=ThreadingHTTPServer((args.host,args.port),Handler); print(f"MediTrace Audio Intake: http://{args.host}:{args.port}"); server.serve_forever()

if __name__ == "__main__": main()
