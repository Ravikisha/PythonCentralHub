// for every code segment there is a data-rehype-pretty-code-fragment and also a after element which is a copy button 
// so i need to write the logic where when user clicks on the copy button the code segment is copied to the clipboard
document.addEventListener('DOMContentLoaded', function () {
    const codeSegments = document.querySelectorAll('[data-rehype-pretty-code-fragment]');
    codeSegments.forEach(codeSegment => {
        const copyButton = codeSegment.children[0];
        const codePre = codeSegment.children[1];
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