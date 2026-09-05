(() => {
  if (window.__VEX_HOOKED__) return;
  window.__VEX_HOOKED__ = true;

  const frameId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const glCanvases = new Set();
  const seen = new Map();
  const recaptured = new Set();
  let armed = false;
  let seq = 0;

  const norm = u => {
    try {
      const x = new URL(String(u || ''), location.href);
      x.hash = '';
      return x.href;
    } catch (_) {
      return String(u || '').split('#')[0];
    }
  };

  const post = o => {
    try {
      if (!window.ViewerNative || typeof window.ViewerNative.postMessage !== 'function') return;
      o.frameId = frameId;
      o.href = String(location.href);
      o.isMain = window === window.top;
      window.ViewerNative.postMessage(JSON.stringify(o));
    } catch (_) {}
  };

  const strongExt = u => /\.(glb|gltf|bin|obj|stl|ply|3mf|dae|fbx|step|stp|iges|igs|scs|scz|s3d|drc|ktx|ktx2|basis|zip)(?:[?#]|$)/i.test(u);
  const commonStatic = u => /\.(css|woff2?|ttf|otf|png|jpe?g|gif|webp|svg|ico|mp4|webm|mp3|wav)(?:[?#]|$)/i.test(u);

  const priority = (url, ct, initiator) => {
    const u = String(url || '').toLowerCase();
    const c = String(ct || '').toLowerCase();
    if (strongExt(u)) return 4;
    if (c.startsWith('model/') || c.includes('gltf') || c.includes('octet-stream') || c.includes('zip') || c.includes('draco')) return 4;
    if (u.includes('geometry') || u.includes('mesh') || u.includes('manifest') || u.includes('model') || u.includes('scene') || u.includes('stream') || u.includes('viewer')) return 3;
    if ((c.includes('json') || c.includes('protobuf')) && (initiator === 'fetch' || initiator === 'xmlhttprequest')) return 2;
    if ((initiator === 'fetch' || initiator === 'xmlhttprequest') && !commonStatic(u)) return 1;
    return 0;
  };

  const remember = (url, initiator, ct) => {
    const u = norm(url);
    if (!u || u.startsWith('blob:') || u.startsWith('data:')) return;
    const p = priority(u, ct || '', initiator || '');
    const old = seen.get(u);
    if (!old || p > old.p) seen.set(u, {url:u, initiator:initiator || '', ct:ct || '', p});
  };

  const b64 = bytes => {
    let out = '';
    const step = 0x8000;
    for (let p = 0; p < bytes.length; p += step) {
      out += String.fromCharCode.apply(null, bytes.subarray(p, Math.min(bytes.length, p + step)));
    }
    return btoa(out);
  };

  const sendBytes = (id, bytes) => {
    const n = 24576;
    for (let p = 0; p < bytes.length; p += n) {
      post({t:'chunk', id, b64:b64(bytes.subarray(p, Math.min(bytes.length, p + n)))});
    }
  };

  const captureBytes = (url, ct, source, status, bytes) => {
    if (!armed || !bytes || !bytes.length) return;
    const id = `${Date.now()}-${++seq}-${Math.random().toString(16).slice(2)}`;
    post({t:'begin', id, url:String(url || ''), ct:String(ct || ''), source:String(source || ''), status:Number(status || 0)});
    sendBytes(id, bytes);
    post({t:'end', id, total:bytes.length});
  };

  const captureResponse = async (response, requestUrl, source, initiator) => {
    try {
      if (!armed) return;
      const url = response.url || String(requestUrl || '');
      const ct = response.headers ? (response.headers.get('content-type') || '') : '';
      remember(url, initiator || source, ct);
      if (priority(url, ct, initiator || source) <= 0) return;
      const id = `${Date.now()}-${++seq}-${Math.random().toString(16).slice(2)}`;
      post({t:'begin', id, url, ct, source, status:Number(response.status || 0)});
      let total = 0;
      if (response.body && response.body.getReader) {
        const reader = response.body.getReader();
        while (true) {
          const r = await reader.read();
          if (r.done) break;
          if (r.value && r.value.length) {
            total += r.value.length;
            if (total > 157286400) throw new Error('resource exceeded 150MB');
            sendBytes(id, r.value);
          }
        }
      } else {
        const bytes = new Uint8Array(await response.arrayBuffer());
        total = bytes.length;
        if (total <= 157286400) sendBytes(id, bytes);
      }
      post({t:'end', id, total});
    } catch (e) {
      post({t:'error', where:'captureResponse', message:String(e)});
    }
  };

  try {
    const realGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type) {
      const ctx = realGetContext.apply(this, arguments);
      try {
        const t = String(type || '').toLowerCase();
        if (t === 'webgl' || t === 'webgl2' || t === 'experimental-webgl' || t === 'webgpu') glCanvases.add(this);
      } catch (_) {}
      return ctx;
    };
  } catch (_) {}

  const realFetch = window.fetch ? window.fetch.bind(window) : null;
  if (realFetch) {
    window.fetch = function(input, init) {
      let requestUrl = '';
      try { requestUrl = typeof input === 'string' ? input : input.url; } catch (_) {}
      remember(requestUrl, 'fetch', '');
      return realFetch(input, init).then(res => {
        try {
          const ct = res.headers ? (res.headers.get('content-type') || '') : '';
          remember(res.url || requestUrl, 'fetch', ct);
          if (armed && priority(res.url || requestUrl, ct, 'fetch') > 0) {
            const clone = res.clone();
            Promise.resolve().then(() => captureResponse(clone, requestUrl, 'fetch', 'fetch'));
          }
        } catch (e) {
          post({t:'error', where:'fetchClone', message:String(e)});
        }
        return res;
      });
    };
  }

  try {
    const X = window.XMLHttpRequest;
    if (X && X.prototype) {
      const realOpen = X.prototype.open;
      const realSend = X.prototype.send;
      X.prototype.open = function(method, url) {
        this.__vexUrl = String(url || '');
        remember(this.__vexUrl, 'xmlhttprequest', '');
        return realOpen.apply(this, arguments);
      };
      X.prototype.send = function() {
        if (!this.__vexInstalled) {
          this.__vexInstalled = true;
          this.addEventListener('loadend', () => {
            try {
              const url = this.responseURL || this.__vexUrl || '';
              const ct = this.getResponseHeader('content-type') || '';
              remember(url, 'xmlhttprequest', ct);
              if (!armed || priority(url, ct, 'xmlhttprequest') <= 0) return;
              const r = this.response;
              if (r instanceof ArrayBuffer) captureBytes(url, ct, 'xhr', this.status, new Uint8Array(r));
              else if (typeof Blob !== 'undefined' && r instanceof Blob) r.arrayBuffer().then(x => captureBytes(url, ct, 'xhr', this.status, new Uint8Array(x)));
              else if (typeof r === 'string' && r.length) captureBytes(url, ct, 'xhr-text', this.status, new TextEncoder().encode(r));
            } catch (e) {
              post({t:'error', where:'xhrCapture', message:String(e)});
            }
          });
        }
        return realSend.apply(this, arguments);
      };
    }
  } catch (_) {}

  try {
    const realCreateObjectURL = URL.createObjectURL.bind(URL);
    URL.createObjectURL = function(obj) {
      const u = realCreateObjectURL(obj);
      try {
        if (obj instanceof Blob && armed && obj.size > 0 && obj.size <= 157286400) {
          obj.arrayBuffer().then(x => captureBytes(u, obj.type || '', 'blob-object-url', 200, new Uint8Array(x)));
        }
      } catch (_) {}
      return u;
    };
  } catch (_) {}

  const libraryHint = () => {
    try {
      if (window.THREE) return 'three.js';
      if (window.BABYLON) return 'babylon.js';
      if (window.Autodesk) return 'autodesk';
      if (window.Cesium) return 'cesium';
      if (window.xeokit) return 'xeokit';
      if (window.Potree || window.potree) return 'potree';
    } catch (_) {}
    return '';
  };

  const visible = r => r && r.width >= 70 && r.height >= 70 && r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;

  const reportViewer = () => {
    try {
      const all = Array.from(document.querySelectorAll('canvas'));
      let pool = all.filter(c => glCanvases.has(c) && visible(c.getBoundingClientRect()));
      let known = true;
      if (!pool.length) {
        pool = all.filter(c => visible(c.getBoundingClientRect()));
        known = false;
      }
      pool.sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
      if (pool.length) {
        const r = pool[0].getBoundingClientRect();
        post({t:'viewer', kind:'canvas', knownWebgl:known, y:r.top, bottom:r.bottom, x:r.left, right:r.right, w:r.width, h:r.height, area:r.width*r.height, lib:libraryHint()});
      } else {
        const mv = document.querySelector('model-viewer');
        if (mv) {
          const r = mv.getBoundingClientRect();
          if (visible(r)) post({t:'viewer', kind:'model-viewer', knownWebgl:true, y:r.top, bottom:r.bottom, x:r.left, right:r.right, w:r.width, h:r.height, area:r.width*r.height, lib:'model-viewer'});
        }
      }

      if (window === window.top) {
        Array.from(document.querySelectorAll('iframe')).slice(0, 50).forEach((f, i) => {
          const r = f.getBoundingClientRect();
          if (!visible(r)) return;
          post({t:'framebox', index:i, src:norm(f.src || f.getAttribute('src') || ''), y:r.top, bottom:r.bottom, x:r.left, right:r.right, w:r.width, h:r.height});
        });
      }
    } catch (e) {
      post({t:'error', where:'viewerScan', message:String(e)});
    }
  };

  const forward = msg => {
    try {
      Array.from(document.querySelectorAll('iframe')).forEach(f => {
        try { f.contentWindow.postMessage(msg, '*'); } catch (_) {}
      });
    } catch (_) {}
  };

  const candidates = () => {
    try {
      performance.getEntriesByType('resource').forEach(e => remember(e.name, e.initiatorType || '', ''));
    } catch (_) {}
    return Array.from(seen.values()).filter(x => x.p > 0).sort((a,b) => b.p - a.p).slice(0, 120);
  };

  const recapture = () => {
    const list = candidates();
    post({t:'note', message:`selected frame resource candidates=${list.length}`});
    list.forEach((x, i) => {
      setTimeout(() => {
        if (!armed) return;
        post({t:'candidate', url:x.url, initiator:x.initiator || '', priority:x.p});
        if (!realFetch || recaptured.has(x.url)) return;
        recaptured.add(x.url);
        realFetch(x.url, {credentials:'include', cache:'force-cache'})
          .then(res => captureResponse(res.clone(), x.url, 'recapture-fetch', x.initiator || 'fetch'))
          .catch(e => post({t:'error', where:'recaptureFetch', message:String(e), url:x.url}));
      }, i * 55);
    });
  };

  const handleCommand = msg => {
    if (!msg || msg.__VEX_CMD !== true) return;
    if (msg.action === 'scan') reportViewer();
    if (msg.action === 'capture') {
      if (norm(msg.targetHref) === norm(location.href)) {
        armed = true;
        post({t:'note', message:'selected viewer frame armed'});
        reportViewer();
        recapture();
      }
    }
    if (msg.action === 'stop') armed = false;
    forward(msg);
  };

  window.addEventListener('message', ev => {
    try { handleCommand(ev.data); } catch (_) {}
  });

  window.__VEX_SCAN_ALL = () => handleCommand({__VEX_CMD:true, action:'scan'});
  window.__VEX_CAPTURE_ALL = href => handleCommand({__VEX_CMD:true, action:'capture', targetHref:String(href || '')});
  window.__VEX_STOP_ALL = () => handleCommand({__VEX_CMD:true, action:'stop'});
  post({t:'ready', message:'generic viewer hook installed'});
})();
