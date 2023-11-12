
// for every code segment there is a data-rehype-pretty-code-fragment and also a after element which is a copy button 
// so i need to write the logic where when user clicks on the copy button the code segment is copied to the clipboard
// and also the copy button text changes to copied

/* 
<div data-rehype-pretty-code-fragment=""><div data-rehype-pretty-code-title="" data-language="python" data-theme="dark">main.py</div><pre class="github-dark-dimmed" style="background-color: #22272e" tabindex="0" data-language="python" data-theme="dark" dir="ltr"><code data-line-numbers="" style="counter-set: line 0;display: grid;" data-language="python" data-theme="dark" data-line-numbers-max-digits="1"><span data-line=""><span style="color: #F47067">from</span><span style="color: #ADBAC7"> starlette.applications </span><span style="color: #F47067">import</span><span style="color: #ADBAC7"> Starlette</span></span>
<span data-line=""><span style="color: #F47067">from</span><span style="color: #ADBAC7"> starlette.responses </span><span style="color: #F47067">import</span><span style="color: #ADBAC7"> JSONResponse</span></span>
<span data-line=""> </span>
<span data-line=""><span style="color: #ADBAC7">app </span><span style="color: #F47067">=</span><span style="color: #ADBAC7"> Starlette(</span><span style="color: #F69D50">debug</span><span style="color: #F47067">=</span><span style="color: #6CB6FF">True</span><span style="color: #ADBAC7">)</span></span>
<span data-line=""><span style="color: #ADBAC7">app.add_route(</span><span style="color: #96D0FF">"/"</span><span style="color: #ADBAC7">, homepage)</span></span>
<span data-line=""><span style="color: #ADBAC7">app.add_route(</span><span style="color: #96D0FF">"/items/</span><span style="color: #F47067">{item_id}</span><span style="color: #96D0FF">"</span><span style="color: #ADBAC7">, item_detail) </span><span style="color: #F47067">==&gt;</span><span style="color: #ADBAC7"> lkjsddddddddddddddddddddddddddddddddddddddddddddddahjdfhlaksjdfahlsjdjfhlaskdjfhlskjdh</span></span></code></pre><div data-rehype-pretty-code-title="" data-language="python" data-theme="light">main.py</div><pre class="github-light" style="background-color: #fff" tabindex="0" data-language="python" data-theme="light" dir="ltr"><code data-line-numbers="" style="counter-set: line 0;display: grid;" data-language="python" data-theme="light" data-line-numbers-max-digits="1"><span data-line=""><span style="color: #D73A49">from</span><span style="color: #24292E"> starlette.applications </span><span style="color: #D73A49">import</span><span style="color: #24292E"> Starlette</span></span>
<span data-line=""><span style="color: #D73A49">from</span><span style="color: #24292E"> starlette.responses </span><span style="color: #D73A49">import</span><span style="color: #24292E"> JSONResponse</span></span>
<span data-line=""> </span>
<span data-line=""><span style="color: #24292E">app </span><span style="color: #D73A49">=</span><span style="color: #24292E"> Starlette(</span><span style="color: #E36209">debug</span><span style="color: #D73A49">=</span><span style="color: #005CC5">True</span><span style="color: #24292E">)</span></span>
<span data-line=""><span style="color: #24292E">app.add_route(</span><span style="color: #032F62">"/"</span><span style="color: #24292E">, homepage)</span></span>
<span data-line=""><span style="color: #24292E">app.add_route(</span><span style="color: #032F62">"/items/</span><span style="color: #005CC5">{item_id}</span><span style="color: #032F62">"</span><span style="color: #24292E">, item_detail) </span><span style="color: #D73A49">==&gt;</span><span style="color: #24292E"> lkjsddddddddddddddddddddddddddddddddddddddddddddddahjdfhlaksjdfahlsjdjfhlaskdjfhlskjdh</span></span></code></pre></div>
*/

document.addEventListener('DOMContentLoaded', function () {
    const codeSegments = document.querySelectorAll('[data-rehype-pretty-code-fragment]');
    console.log(codeSegments);
    // const copyButtons = codeSegments.querySelectorAll('[data-rehype-pretty-code-title]')
    // console.log(copyButtons);
    codeSegments.forEach(codeSegment => {
        const copyButton = codeSegment.children[0];
        const codePre = codeSegment.children[1];
        const afterElement = window.getComputedStyle(copyButton, "::after");
       copyButton.addEventListener('click', () => {
            copyButton.setAttribute('data-open', 'true');
            copyToClipboard(codePre.innerText);
            setTimeout(() => {
                copyButton.setAttribute('data-open', 'false');
            }, 2000);
       });
    })
});

const copyToClipboard = (codeSegment) => {
    const el = document.createElement('textarea');
    el.value = codeSegment;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}