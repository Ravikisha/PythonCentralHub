(function(){
  // Simple toast system with API: window.toast.show({ title, description, variant, duration })
  const rootId = 'toast-root';
  function ensureRoot(){
    let root = document.getElementById(rootId);
    if(!root){
      root = document.createElement('div');
      root.id = rootId;
      root.setAttribute('aria-live','polite');
      document.body.appendChild(root);
    }
    return root;
  }

  function iconForVariant(variant){
    switch(variant){
      case 'success': return '\u2714'; // check
      case 'error': return '\u26A0'; // caution
      default: return '\u2139'; // info
    }
  }

  function show(opts){
    const { title = '', description = '', variant = 'info', duration = 4000, html = false } = opts || {};
    const root = ensureRoot();
    const toast = document.createElement('div');
    toast.className = `toast toast--${variant} toast-show`;

    // Build DOM structure without ever injecting untrusted strings as markup.
    const icon = document.createElement('div');
    icon.className = 'toast-icon';
    icon.textContent = iconForVariant(variant);

    const body = document.createElement('div');
    body.className = 'toast-body';

    const titleEl = document.createElement('div');
    titleEl.className = 'toast-title';
    // Markup only via explicit opt-in. Default is safe text.
    if(html){ titleEl.innerHTML = title; } else { titleEl.textContent = title; }
    body.appendChild(titleEl);

    if(description){
      const descEl = document.createElement('div');
      descEl.className = 'toast-desc';
      if(html){ descEl.innerHTML = description; } else { descEl.textContent = description; }
      body.appendChild(descEl);
    }

    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.setAttribute('aria-label', 'Dismiss');
    closeBtn.textContent = '\u2715';

    toast.appendChild(icon);
    toast.appendChild(body);
    toast.appendChild(closeBtn);

    const hide = (animate=true)=>{
      if(!toast.__hidden){
        toast.__hidden = true;
        if(animate){
          toast.classList.remove('toast-show');
          toast.classList.add('toast-hide');
          setTimeout(()=>{ if(toast.parentNode) root.removeChild(toast); }, 180);
        } else {
          if(toast.parentNode) root.removeChild(toast);
        }
      }
    };

    closeBtn.addEventListener('click', ()=> hide(true));

    root.appendChild(toast);

    if(duration && duration > 0){
      toast.__timeout = setTimeout(()=> hide(true), duration);
    }

    return {
      hide
    };
  }

  window.toast = window.toast || { show };
})();
