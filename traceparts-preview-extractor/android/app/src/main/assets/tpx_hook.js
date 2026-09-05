(() => {
  if (window.__TPX_HOOKED_V11__) return;
  window.__TPX_HOOKED_V11__ = true;

  let seq = 0;
  let lastPathRequest = null;
  let lastPathXhr = null;
  const nativePost = o => {
    try {
      if (window.TPNative && typeof window.TPNative.postMessage === 'function') {
        window.TPNative.postMessage(JSON.stringify(o));
      }
    } catch (_) {}
  };

  const armed = () => {
    try { return /(?:^|;\s*)tp_capture=1(?:;|$)/.test(document.cookie || ''); }
    catch (_) { return false; }
  };

  const absUrl = u => {
    try { return new URL(String(u || ''), location.href).href; }
    catch (_) { return String(u || ''); }
  };

  const urlInteresting = url => {
    const u = String(url || '').toLowerCase();
    return u.includes('/api/v/path') || u.includes('/api/') ||
      /\.(glb|gltf|bin|obj|stl|ply|3mf|dae|fbx|step|stp|iges|igs|scs|scz|s3d|zip)(?:[?#]|$)/i.test(u) ||
      u.includes('geometry') || u.includes('mesh') || u.includes('manifest') ||
      u.includes('model') || u.includes('stream') || u.includes('viewer');
  };

  const bodyInteresting = (url, ct) => {
    if (!armed()) return false;
    const u = String(url || '').toLowerCase();
    const c = String(ct || '').toLowerCase();
    if (u.includes('/api/v/path')) return true;
    if (/\.(glb|gltf|bin|obj|stl|ply|3mf|dae|fbx|step|stp|iges|igs|scs|scz|s3d|zip)(?:[?#]|$)/i.test(u)) return true;
    if (u.includes('geometry') || u.includes('mesh') || u.includes('manifest') || u.includes('model') || u.includes('stream')) return true;
    if (c.startsWith('model/') || c.includes('gltf') || c.includes('octet-stream') || c.includes('zip') || c.includes('mesh')) return true;
    return false;
  };

  const safeHeaders = headers => {
    const out = [];
    const secret = /^(authorization|cookie|set-cookie|proxy-authorization)$/i;
    try {
      if (headers && typeof headers.forEach === 'function') {
        headers.forEach((v, k) => out.push(secret.test(k) ? `${k}: [redacted]` : `${k}: ${v}`));
      } else if (typeof headers === 'string') {
        String(headers).split(/\r?\n/).forEach(line => {
          if (!line) return;
          const p = line.indexOf(':');
          const k = p >= 0 ? line.slice(0, p).trim() : line.trim();
          out.push(secret.test(k) ? `${k}: [redacted]` : line);
        });
      }
    } catch (_) {}
    return out.join('\n');
  };

  const b64 = bytes => {
    let out = '';
    const step = 8192;
    for (let p = 0; p < bytes.length; p += step) {
      out += String.fromCharCode.apply(null, bytes.subarray(p, Math.min(bytes.length, p + step)));
    }
    return btoa(out);
  };

  const sendBytes = (id, bytes) => {
    const N = 24576;
    for (let p = 0; p < bytes.length; p += N) {
      nativePost({t:'chunk', id, b64:b64(bytes.subarray(p, Math.min(bytes.length, p + N)))});
    }
  };

  const captureBytes = (bytes, meta) => {
    try {
      const id = `${Date.now()}-${++seq}-${Math.random().toString(16).slice(2)}`;
      nativePost({
        t:'begin', id,
        url:String(meta.url || ''),
        ct:String(meta.ct || ''),
        source:String(meta.source || ''),
        status:Number(meta.status || 0),
        headers:String(meta.headers || '')
      });
      if (bytes && bytes.length) sendBytes(id, bytes);
      nativePost({t:'end', id, total:bytes ? bytes.length : 0});
    } catch (e) {
      nativePost({t:'error', where:'captureBytes', message:String(e)});
    }
  };

  const captureResponse = async (response, requestUrl, source) => {
    try {
      const url = response.url || absUrl(requestUrl);
      const ct = response.headers ? (response.headers.get('content-type') || '') : '';
      const hs = response.headers ? safeHeaders(response.headers) : '';
      nativePost({t:'meta', transport:source, url, status:response.status || 0, ct, headers:hs, type:String(response.type || '')});
      if (!bodyInteresting(url, ct)) return;
      const bytes = new Uint8Array(await response.arrayBuffer());
      captureBytes(bytes, {url, ct, source, status:response.status || 0, headers:hs});
    } catch (e) {
      nativePost({t:'error', where:'captureResponse', message:String(e), url:String(requestUrl || '')});
    }
  };

  const headerNames = headers => {
    const names = [];
    try {
      new Headers(headers || {}).forEach((_, k) => names.push(k));
    } catch (_) {}
    return names.join(',');
  };

  const realFetch = window.fetch ? window.fetch.bind(window) : null;
  if (realFetch) {
    window.fetch = function(input, init) {
      let requestUrl = '';
      try { requestUrl = typeof input === 'string' ? input : input.url; } catch (_) {}
      const full = absUrl(requestUrl);
      if (armed() && urlInteresting(full)) {
        let method = 'GET';
        try { method = String((init && init.method) || (input && input.method) || 'GET'); } catch (_) {}
        nativePost({t:'net', phase:'request', transport:'fetch', method, url:full, headerNames:headerNames((init && init.headers) || (input && input.headers))});
      }
      if (armed() && full.includes('/api/v/path')) {
        try { lastPathRequest = new Request(input, init); } catch (_) { lastPathRequest = null; }
      }
      return realFetch(input, init).then(res => {
        try {
          const ct = res.headers ? (res.headers.get('content-type') || '') : '';
          if (armed() && (urlInteresting(res.url || full) || bodyInteresting(res.url || full, ct))) {
            Promise.resolve().then(() => captureResponse(res.clone(), full, 'fetch'));
          }
        } catch (e) {
          nativePost({t:'error', where:'fetchClone', message:String(e), url:full});
        }
        return res;
      });
    };
  }

  const X = window.XMLHttpRequest;
  if (X && X.prototype) {
    const realOpen = X.prototype.open;
    const realSend = X.prototype.send;
    const realSetHeader = X.prototype.setRequestHeader;

    X.prototype.open = function(method, url) {
      this.__tpxUrl = absUrl(url);
      this.__tpxMethod = String(method || 'GET');
      this.__tpxHeaders = {};
      return realOpen.apply(this, arguments);
    };

    X.prototype.setRequestHeader = function(name, value) {
      try { this.__tpxHeaders[String(name)] = String(value); } catch (_) {}
      return realSetHeader.apply(this, arguments);
    };

    X.prototype.send = function(body) {
      if (!this.__tpxInstalled) {
        this.__tpxInstalled = true;
        this.addEventListener('loadend', () => {
          try {
            if (!armed()) return;
            const url = this.responseURL || this.__tpxUrl || '';
            const ct = this.getResponseHeader('content-type') || '';
            const hs = safeHeaders(this.getAllResponseHeaders ? this.getAllResponseHeaders() : '');
            nativePost({t:'meta', transport:'xhr', url, status:this.status || 0, ct, headers:hs, type:String(this.responseType || '')});
            if (!bodyInteresting(url, ct)) return;

            const finish = bytes => captureBytes(bytes, {url, ct, source:'xhr', status:this.status || 0, headers:hs});
            let r = this.response;
            const rt = String(this.responseType || '');
            if ((r == null || (typeof r === 'string' && r.length === 0)) && (rt === '' || rt === 'text')) {
              try { if (typeof this.responseText === 'string') r = this.responseText; } catch (_) {}
            }
            if (r instanceof ArrayBuffer) finish(new Uint8Array(r));
            else if (typeof Blob !== 'undefined' && r instanceof Blob) r.arrayBuffer().then(b => finish(new Uint8Array(b))).catch(e => nativePost({t:'error', where:'xhrBlob', message:String(e), url}));
            else if (typeof r === 'string') finish(new TextEncoder().encode(r));
            else if (r && typeof Document !== 'undefined' && r instanceof Document) finish(new TextEncoder().encode(new XMLSerializer().serializeToString(r)));
            else if (r != null) {
              try { finish(new TextEncoder().encode(JSON.stringify(r))); }
              catch (_) { finish(new Uint8Array(0)); }
            } else finish(new Uint8Array(0));
          } catch (e) {
            nativePost({t:'error', where:'xhrCapture', message:String(e), url:String(this.__tpxUrl || '')});
          }
        });
      }

      const url = this.__tpxUrl || '';
      if (armed() && urlInteresting(url)) {
        nativePost({t:'net', phase:'request', transport:'xhr', method:String(this.__tpxMethod || 'GET'), url, headerNames:Object.keys(this.__tpxHeaders || {}).join(',')});
      }
      if (armed() && url.includes('/api/v/path')) {
        lastPathXhr = {
          method:this.__tpxMethod || 'GET',
          url,
          headers:Object.assign({}, this.__tpxHeaders || {}),
          body:(typeof body === 'string' || body instanceof URLSearchParams) ? String(body) : null
        };
      }
      return realSend.apply(this, arguments);
    };
  }

  const realCreateObjectURL = window.URL && URL.createObjectURL ? URL.createObjectURL.bind(URL) : null;
  if (realCreateObjectURL) {
    URL.createObjectURL = function(obj) {
      const out = realCreateObjectURL(obj);
      try {
        if (armed() && typeof Blob !== 'undefined' && obj instanceof Blob && obj.size > 0) {
          const ct = String(obj.type || '');
          if (bodyInteresting(out, ct) || ct.includes('octet-stream') || ct.startsWith('model/')) {
            obj.arrayBuffer().then(b => captureBytes(new Uint8Array(b), {url:out, ct, source:'blob-url', status:200, headers:''}))
              .catch(e => nativePost({t:'error', where:'blobUrl', message:String(e)}));
          }
        }
      } catch (_) {}
      return out;
    };
  }

  if (window.WebSocket) {
    const RealWebSocket = window.WebSocket;
    const WrappedWebSocket = function(url, protocols) {
      const ws = protocols === undefined ? new RealWebSocket(url) : new RealWebSocket(url, protocols);
      try {
        const full = absUrl(url);
        if (armed()) nativePost({t:'net', phase:'open', transport:'websocket', method:'WS', url:full, headerNames:''});
        ws.addEventListener('message', ev => {
          if (!armed()) return;
          try {
            const d = ev.data;
            if (d instanceof ArrayBuffer) captureBytes(new Uint8Array(d), {url:full, ct:'application/octet-stream', source:'websocket', status:101, headers:''});
            else if (typeof Blob !== 'undefined' && d instanceof Blob) d.arrayBuffer().then(b => captureBytes(new Uint8Array(b), {url:full, ct:d.type || 'application/octet-stream', source:'websocket', status:101, headers:''}));
            else if (typeof d === 'string' && urlInteresting(full) && d.length < 65536) captureBytes(new TextEncoder().encode(d), {url:full, ct:'text/plain', source:'websocket-text', status:101, headers:''});
          } catch (_) {}
        });
      } catch (_) {}
      return ws;
    };
    WrappedWebSocket.prototype = RealWebSocket.prototype;
    Object.setPrototypeOf(WrappedWebSocket, RealWebSocket);
    window.WebSocket = WrappedWebSocket;
  }

  window.__tpxReplayLastPath = async () => {
    if (!armed() || !realFetch) return -2;
    try {
      let res;
      if (lastPathRequest) {
        res = await realFetch(lastPathRequest.clone());
      } else if (lastPathXhr) {
        res = await realFetch(lastPathXhr.url, {
          method:lastPathXhr.method || 'GET',
          headers:lastPathXhr.headers || {},
          body:lastPathXhr.body,
          credentials:'include',
          cache:'no-store'
        });
      } else {
        nativePost({t:'note', message:'No real /api/v/path request has been observed yet; replay skipped.'});
        return -3;
      }
      await captureResponse(res, res.url || '', 'exact-replay');
      return res.status;
    } catch (e) {
      nativePost({t:'error', where:'exactReplay', message:String(e)});
      return -1;
    }
  };

  window.__tpxDumpResources = () => {
    try {
      const urls = [...new Set(performance.getEntriesByType('resource').map(e => e.name).filter(urlInteresting))].slice(0, 250);
      nativePost({t:'note', message:`resource candidates=${urls.length}`});
      urls.forEach(u => nativePost({t:'net', phase:'performance', transport:'resource', method:'GET', url:u, headerNames:''}));
      return urls.length;
    } catch (e) {
      nativePost({t:'error', where:'performance', message:String(e)});
      return -1;
    }
  };

  window.__tpxFindPreview = () => {
    try {
      const clickable = [...document.querySelectorAll('button,a,[role="button"],[role="tab"],summary,[onclick]')];
      const textOf = e => String(e.innerText || e.textContent || e.getAttribute('aria-label') || e.getAttribute('title') || '').replace(/\s+/g, ' ').trim();
      const strong = /(preview|aperçu|3d\s*preview|visualisation\s*3d|vue\s*3d|mod[eè]le\s*3d)/i;
      let hit = clickable.find(e => strong.test(textOf(e)));
      if (!hit) {
        const nodes = [...document.querySelectorAll('span,div,h2,h3,h4')].filter(e => strong.test(textOf(e)));
        for (const n of nodes) {
          const p = n.closest('button,a,[role="button"],[role="tab"],summary,[onclick]');
          if (p) { hit = p; break; }
        }
      }
      if (hit) {
        try { hit.scrollIntoView({behavior:'smooth', block:'center'}); } catch (_) { hit.scrollIntoView(); }
        setTimeout(() => { try { hit.click(); } catch (_) {} }, 250);
        nativePost({t:'note', message:`Preview control clicked: ${textOf(hit).slice(0,80)}`});
        setTimeout(() => window.__tpxDumpResources && window.__tpxDumpResources(), 1800);
        return 'clicked:' + textOf(hit).slice(0,80);
      }
      window.__TPX_PREVIEW_SCAN__ = (window.__TPX_PREVIEW_SCAN__ || 0) + 1;
      const frac = Math.min(0.92, 0.34 + (window.__TPX_PREVIEW_SCAN__ % 5) * 0.14);
      window.scrollTo({top:Math.max(0, document.documentElement.scrollHeight * frac - innerHeight * 0.4), behavior:'smooth'});
      nativePost({t:'note', message:`Preview control not found; scrolled to ${Math.round(frac*100)}% to trigger lazy content.`});
      return 'not-found-scroll:' + frac;
    } catch (e) {
      nativePost({t:'error', where:'findPreview', message:String(e)});
      return 'error:' + e;
    }
  };

  try {
    const po = new PerformanceObserver(list => {
      if (!armed()) return;
      for (const e of list.getEntries()) {
        if (urlInteresting(e.name)) nativePost({t:'net', phase:'observed', transport:'resource', method:'GET', url:e.name, headerNames:''});
      }
    });
    po.observe({type:'resource', buffered:true});
  } catch (_) {}

  nativePost({t:'note', message:'v1.1 capture hook installed', href:String(location.href)});
})();
