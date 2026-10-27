#!/usr/bin/env python3
"""Build ../index.html (the no-account web version) from summit-scramble.html (the Claude artifact version).

Swaps the Claude `room` capability for direct phone-to-phone connections (WebRTC via PeerJS).
The host's page stays authoritative exactly as before; the shim below exposes the same
presence()/peers() calls the game already uses, so the game code itself is untouched.
Run:  python3 source/make_web.py   (re-run after any change to the Claude version)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'summit-scramble.html')
OUT = os.path.join(HERE, '..', 'index.html')
PEERJS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'peerjs.min.js')

s = open(SRC).read()
ICON = open(os.path.join(HERE, 'icon180.b64')).read().strip()
lib = open(PEERJS).read().replace('//# sourceMappingURL=peerjs.min.js.map', '')

def R(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:120])
    s = s.replace(a, b)

# ---------------------------------------------------------------- document head
R('<title>Summit Scramble</title>',
  '<!doctype html>\n<html lang="en"><head>\n<meta charset="utf-8">\n'
  '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n'
  '<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="mobile-web-app-capable" content="yes">\n'
  '<meta name="theme-color" content="#0b0c26">\n'
  '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
  '<meta name="apple-mobile-web-app-title" content="Summit">\n'
  '<link rel="apple-touch-icon" href="data:image/png;base64,' + ICON + '">\n'
  '<link rel="icon" href="data:image/png;base64,' + ICON + '">\n'
  '<title>Summit Scramble</title>')
R('<style>', '<style>\nhtml,body{margin:0;background:#0b0c26;height:100%;overflow:hidden}\n'
  '#tipBox{position:fixed;inset:0;z-index:30;display:flex;align-items:center;justify-content:center;background:rgba(7,8,28,.8);font-family:var(--font-pixel);padding:16px;box-sizing:border-box}\n'
  '#tipBox[hidden]{display:none}\n'
  '#tipCard #tipX{position:absolute;top:6px;right:6px;width:30px;height:30px;padding:0;font-size:11px;background:transparent;border:2px solid #4a54a8;color:var(--snow)}\n'
  '#tipCard{position:relative;background:var(--night);border:2px solid var(--snow);box-shadow:0 0 0 4px rgba(58,66,144,.6);padding:20px;max-width:420px;color:var(--ink);text-align:center}\n'
  '#tipCard h2{font-size:12px;margin:0 0 14px;font-weight:400;letter-spacing:.06em}\n'
  '#tipCard ol{font-size:9px;line-height:2;margin:0 0 16px;padding-left:22px;text-align:left;color:var(--snow)}\n'
  '#tipCard p{font-size:8px;line-height:1.8;margin:0 0 14px;color:var(--snow);opacity:.8}\n'
  '#tipCard button{font:12px var(--font-pixel);color:var(--ink);background:#ee4655;border:0;border-bottom:3px solid #a82a3a;padding:12px 22px;letter-spacing:.08em}\n', 1)
R('\n<script>\n', '\n</head><body>\n<script>/*! PeerJS 1.5.4 | MIT License | peerjs.com */\n' + lib + '\n</script>\n<script>\n', 1)
TIP = ('<div id="tipBox" hidden><div id="tipCard"><button type="button" id="tipX" aria-label="Close">X</button><h2>FULL SCREEN ON IPHONE</h2>'
  '<ol><li>TAP SAFARI\'S SHARE BUTTON (THE SQUARE WITH AN ARROW).</li><li>SCROLL DOWN, TAP <b>ADD TO HOME SCREEN</b>, THEN ADD.</li>'
  '<li>OPEN SUMMIT SCRAMBLE FROM YOUR HOME SCREEN.</li></ol>'
  '<p>IT OPENS WITH NO ADDRESS BAR OR TABS. TURN THE PHONE SIDEWAYS TO PLAY.</p><button type="button" id="tipOk">GOT IT</button></div></div>\n')
s = s.rstrip() + '\n' + TIP + '</body></html>\n'

# ---------------------------------------------------------------- network shim
SHIM = r"""
// ============================================================ direct connections (PeerJS / WebRTC)
// Acts like the Claude room the game was written for: presence(patch) + peers().
// The host's page holds one connection per friend; friends connect only to the host.
const NETQ=new URLSearchParams(location.search);
const PEER_PREFIX='summitscramble-v1-';
// Optional: put relay (TURN) servers here if friends on cell data can't connect, e.g. from metered.ca.
const EXTRA_ICE=[];
let pendingRoom=(NETQ.get('room')||'').toLowerCase().replace(/[^a-z]/g,'').slice(0,4);
let netBusy=false;
function peerOpts(){const o={debug:0};
  const ph=NETQ.get('peerhost');if(ph){const [h,p]=ph.split(':');o.host=h;o.port=+(p||9000);o.path='/';o.secure=location.protocol==='https:'&&h!=='localhost';}
  if(EXTRA_ICE.length)o.config={iceServers:[{urls:'stun:stun.l.google.com:19302'},{urls:['turn:eu-0.turn.peerjs.com:3478','turn:us-0.turn.peerjs.com:3478'],username:'peerjs',credential:'peerjsp'},...EXTRA_ICE]};
  return o;}
const errText=e=>{const t=e&&e.type;return t==='peer-unavailable'?'NO GAME WITH THAT CODE':t==='unavailable-id'?'CODE IN USE':t==='browser-incompatible'?'THIS BROWSER CAN\'T PLAY ONLINE':
  (t==='network'||t==='server-error'||t==='socket-error'||t==='socket-closed')?'CAN\'T REACH THE GAME SERVER':t==='webrtc'?'CONNECTION FAILED':String((e&&(e.message||t))||e||'ERROR').toUpperCase().slice(0,32);};
function openLink(role,code){return new Promise((resolve,reject)=>{
  if(typeof Peer!=='function'){reject('ONLINE PLAY DIDN\'T LOAD');return;}
  let done=false,pr;const fail=m=>{if(done)return;done=true;clearTimeout(to);try{pr&&pr.destroy();}catch(e){}reject(m);};
  const to=setTimeout(()=>fail(role==='host'?'CAN\'T REACH THE GAME SERVER':'NO ANSWER FROM THAT GAME'),15000);
  try{pr=role==='host'?new Peer(PEER_PREFIX+code,peerOpts()):new Peer(peerOpts());}catch(e){fail(errText(e));return;}
  const L={role,code,pr,mine:{},seq:0,dirty:true,others:new Map(),list:null,live:false,connFns:[],closed:false,iv:0};
  const setLive=v=>{if(L.live===v)return;L.live=v;L.connFns.forEach(f=>{try{f(v);}catch(e){}});};
  const drop=id=>{const o=L.others.get(id);if(!o)return;L.others.delete(id);L.list=null;try{o.conn.close();}catch(e){}
    if(role==='client'){setLive(false);}};
  const attach=conn=>{
    conn.on('data',d=>{if(!d||typeof d!=='object'||d.t!=='p'||typeof d.p!=='object'||!d.p)return;let o=L.others.get(conn.peer);
      if(!o){if(L.others.size>=12){try{conn.close();}catch(e){}return;}o={conn,q:-1,obj:null,last:0};L.others.set(conn.peer,o);}
      o.last=performance.now();const q=+d.q||0;if(q<=o.q&&o.q-q<1e6)return;o.q=q;
      o.obj=Object.freeze({peer:conn.peer,by:null,isMe:false,sameTab:false,kind:'viewer',guest:false,presence:Object.freeze(d.p),updatedAt:Date.now()});L.list=null;});
    conn.on('close',()=>drop(conn.peer));conn.on('error',()=>drop(conn.peer));};
  const sendAll=()=>{const msg={t:'p',q:++L.seq,p:L.mine};for(const o of L.others.values()){if(o.conn.open){try{o.conn.send(msg);}catch(e){}}}};
  let beat=0;
  L.iv=setInterval(()=>{if(L.closed)return;beat++;
    if(L.dirty||beat%15===0){L.dirty=false;sendAll();}
    const now=performance.now();for(const [id,o] of L.others){if(o.obj&&now-o.last>7000)drop(id);else if(!o.obj&&now-(o.born||(o.born=now))>15000)drop(id);}},33);
  pr.on('error',e=>{if(!done){fail(errText(e));return;}if(e&&e.type==='peer-unavailable'&&role==='client')noteErr({code:'HOST GONE'});});
  pr.on('disconnected',()=>{if(L.closed)return;setTimeout(()=>{try{if(!L.closed&&pr.disconnected&&!pr.destroyed)pr.reconnect();}catch(e){}},1500);});
  if(role==='host'){
    pr.on('open',()=>{if(done)return;done=true;clearTimeout(to);setLive(true);resolve(L);});
    pr.on('connection',conn=>{conn.on('open',()=>{if(!L.others.has(conn.peer))L.others.set(conn.peer,{conn,q:-1,obj:null,last:performance.now()});L.dirty=true;});attach(conn);});
  }else{
    pr.on('open',()=>{if(done)return;const conn=pr.connect(PEER_PREFIX+code,{serialization:'json',reliable:false});attach(conn);
      conn.on('open',()=>{L.others.set(conn.peer,{conn,q:-1,obj:null,last:performance.now()});L.dirty=true;setLive(true);if(!done){done=true;clearTimeout(to);resolve(L);}});
      conn.on('close',()=>{if(!done)fail('NO ANSWER FROM THAT GAME');});});
  }
  // the room-shaped API the game uses
  L.presence=patch=>{for(const k in patch){if(patch[k]===null)delete L.mine[k];else L.mine[k]=patch[k];}L.dirty=true;L.selfObj=null;L.list=null;return Promise.resolve();};
  L.peers=()=>{if(L.list)return L.list;if(!L.selfObj)L.selfObj=Object.freeze({peer:pr.id||'me',by:null,isMe:true,sameTab:true,kind:'viewer',guest:false,presence:Object.freeze({...L.mine}),updatedAt:Date.now()});
    const out=[L.selfObj];for(const o of L.others.values())if(o.obj)out.push(o.obj);L.list=Object.freeze(out);return L.list;};
  L.onPeers=()=>()=>{};L.onConnection=(f)=>{L.connFns.push(f);setTimeout(()=>f(L.live),0);return()=>{};};L.connected=()=>L.live;
  L.close=()=>{if(L.closed)return;L.closed=true;clearInterval(L.iv);try{const msg={t:'p',q:++L.seq,p:{}};for(const o of L.others.values())if(o.conn.open)o.conn.send(msg);}catch(e){}
    setTimeout(()=>{try{pr.destroy();}catch(e){}},150);};
});}
async function hostGame(){if(netBusy)return;netBusy=true;toast('OPENING A ROOM...','#ffd23f',8);let L=null,code='';
  for(let tries=0;tries<3&&!L;tries++){code=Array.from({length:4},()=>String.fromCharCode(97+Math.random()*26|0)).join('');
    try{L=await openLink('host',code);}catch(e){netErr=String(e);if(netErr!=='CODE IN USE')break;}}
  netBusy=false;toasts.length=0;
  if(!L){toast('COULD NOT HOST: '+netErr,'#ff6b6b',5);return;}
  ROOM=GROOM=L;L.onConnection(c=>{roomLive=c;});netErr='';
  NET='host';roomCode=code;resetSlots();hostEvents=[];state='lobby';advT=0;SFX.blip();
  try{history.replaceState(null,'',location.pathname+'?room='+code.toUpperCase()+(NETQ.get('peerhost')?'&peerhost='+NETQ.get('peerhost'):''));}catch(e){}}
async function joinGame(code){if(netBusy)return;netBusy=true;toast('JOINING ROOM '+code.toUpperCase()+'...','#ffd23f',16);let L=null;
  try{L=await openLink('client',code);}catch(e){netErr=String(e);}
  netBusy=false;toasts.length=0;
  if(!L){toast('COULD NOT JOIN '+code.toUpperCase()+': '+netErr,'#ff6b6b',5);return;}
  ROOM=GROOM=L;L.onConnection(c=>{roomLive=c;});netErr='';
  NET='client';roomCode=code;myJoin={};lastSnapObj=null;lastEvSeen=-1;curRid=-1;players=[];hostSeenAt=0;joinAt=TG;resetSlots();state='lobby';SFX.blip();}
const STANDALONE=(()=>{try{return navigator.standalone===true||matchMedia('(display-mode: standalone)').matches||matchMedia('(display-mode: fullscreen)').matches;}catch(e){return false;}})();
const IS_IPHONE=/iPhone|iPod/.test(navigator.userAgent);
const CAN_FS=!IS_IPHONE&&!!(document.documentElement.requestFullscreen||document.documentElement.webkitRequestFullscreen);
const isFS=()=>!!(document.fullscreenElement||document.webkitFullscreenElement);
function showFull(){return IS_TOUCH&&!STANDALONE&&!isFS();}
function homeTip(){const b=document.getElementById('tipBox');if(b)b.hidden=false;}
async function goFull(){if(!CAN_FS){homeTip();return;}const el=document.documentElement;
  try{await (el.requestFullscreen?el.requestFullscreen({navigationUI:'hide'}):el.webkitRequestFullscreen());}catch(e){homeTip();return;}
  try{await screen.orientation.lock('landscape');}catch(e){}setTimeout(resize,300);}
document.addEventListener('pointerdown',e=>{if(e.target&&(e.target.id==='tipOk'||e.target.id==='tipX')){e.preventDefault();document.getElementById('tipBox').hidden=true;}});
function inviteLink(){return location.origin+location.pathname+'?room='+roomCode.toUpperCase();}
async function shareInvite(){const url=inviteLink();
  try{if(navigator.share){await navigator.share({title:'Summit Scramble',text:'Join my Summit Scramble game! Room '+roomCode.toUpperCase(),url});return;}}catch(e){if(e&&e.name==='AbortError')return;}
  try{await navigator.clipboard.writeText(url);toast('INVITE LINK COPIED','#7cf09a',3);}catch(e){toast(url.replace(/^https?:\/\//,'').toUpperCase().slice(0,48),'#ffd23f',8);}}
"""

# init: no Claude capabilities on the open web
R("""(async()=>{
  try{if(window.claude&&typeof window.claude.use==='function'){const [r,u]=await Promise.all([window.claude.use('room'),window.claude.use('user')]);ROOM=r;USERCAP=u;}}catch(e){}
  roomState=ROOM?'ready':'none';""", SHIM + """(async()=>{
  roomState='ready';""")

# remove the Claude versions of host/join (the shim defines them)
import re
a = s.index('async function hostGame(){if(!ROOM)')
b = s.index('function leaveOnline(')
s = s[:a] + s[b:]
R("""  if(ROOM){try{ROOM.presence({g:null,hs:null,c:null}).catch(()=>{});}catch(e){}}""",
  """  if(ROOM){try{ROOM.close();}catch(e){}}ROOM=null;roomLive=false;""")

# after the name prompt, follow an invite link straight into the game
# follow an invite link straight into the game once the name prompt closes (PLAY or X)
R("let onBoxClosed=null;","let onBoxClosed=()=>{if(pendingRoom.length===4&&NET==='off'&&state==='menu'){const c=pendingRoom;pendingRoom='';setTimeout(()=>joinGame(c),0);}};")

# ---------------------------------------------------------------- version label
import datetime, zoneinfo
stamp = datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).strftime('%b %d %Y').upper()
R("const BUILD={v:", "const BUILD={v:")
s = s.replace("where:'CLAUDE',date:''}", "where:'GITHUB',date:'" + stamp + "'}", 1)


# ---------------------------------------------------------------- menu: join by code / link
a = s.index("  const on=!!ROOM;\n  btn(16,46,136,20,'LOCAL GAME'")
b = s.index("  TX(IS_TOUCH?'TAP A BUTTON TO PLAY'", a)
s = s[:a] + r"""  if(showFull())btn(4,4,52,11,'FULL SCREEN',goFull,false,false,3.2);
  btn(16,46,136,20,'LOCAL GAME',()=>{NET='off';resetSlots();state='lobby';SFX.blip();},false,false,6);
  TX('SHARE ONE SCREEN WITH KEYBOARDS',84,69,3,'#9aa6e8','center',false);TX('AND GAMEPADS, PLUS CPU PLAYERS',84,74,3,'#9aa6e8','center',false);
  btn(16,86,136,20,'HOST ONLINE GAME',hostGame,true,netBusy,6);
  btn(16,124,136,14,'NAME: '+(myName||'NONE')+'  (EDIT)',()=>openName(null),false,false,4);
  TX('YOU GET A 4-LETTER CODE',84,109,3,'#9aa6e8','center',false);TX('AND AN INVITE LINK TO SEND',84,114,3,'#9aa6e8','center',false);
  panel(164,46,142,96);TX('JOIN A FRIEND',235,51,5,'#eef0ff','center',false);
  ['NO ACCOUNT NEEDED.','','OPEN THE INVITE LINK YOUR','FRIEND SENT, OR TAP BELOW','AND TYPE THEIR ROOM CODE.','','BEST ON THE SAME WIFI.','KEEP THE HOST\'S SCREEN ON.'].forEach((l,i)=>TX(l,235,62+i*7,3,i===0?'#7cf09a':'#9aa6e8','center',false));
  btn(170,122,130,16,'ENTER A ROOM CODE',openCode,true,netBusy,4.5);
""" + s[b:]

# ---------------------------------------------------------------- host lobby: share button
R("""TX('FRIENDS TAP JOIN, OR',W/2+80,13.5,2.8,'#9aa6e8','center',false);TX('ENTER THIS CODE',W/2+80,17.5,2.8,'#9aa6e8','center',false);""",
  """btn(W-82,13,76,11,'SHARE INVITE LINK',shareInvite,true,false,3.2);""")
R("""TX('THE 4 LETTERS SHOWN AT THE TOP OF THE HOST\\'S LOBBY.'""", """TX('THE 4 LETTERS SHOWN AT THE TOP OF THE HOST\\'S LOBBY.'""", 0)  # (tip text lives in the DOM)

open(OUT, 'w').write(s)
print('wrote', OUT, len(s), 'bytes')
