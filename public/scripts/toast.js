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
    const { title = '', description = '', variant = 'info', duration = 4000 } = opts || {};
    const root = ensureRoot();
    const toast = document.createElement('div');
    toast.className = `toast toast--${variant} toast-show`;

    toast.innerHTML = `
      <div class="toast-icon">${iconForVariant(variant)}</div>
      <div class="toast-body">
        <div class="toast-title">${escapeHtml(title)}</div>
        ${description ? `<div class="toast-desc">${escapeHtml(description)}</div>` : ''}
      </div>
      <button class="toast-close" aria-label="Dismiss">\u2715</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
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

  function escapeHtml(s){
    return String(s)
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#039;');
  }

  window.toast = window.toast || { show };
})();
