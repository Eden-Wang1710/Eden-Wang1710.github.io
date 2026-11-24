const dialog = document.getElementById('figure-dialog');
const image = document.getElementById('dialog-image');
const titles = {architecture:'Figure 1: SRCV Harness',reader:'Figure 2: Selective Reader'};
document.querySelectorAll('[data-figure]').forEach(button => button.addEventListener('click', () => {
  const source=button.querySelector('img');
  image.src=source.src; image.alt=source.alt;
  document.getElementById('dialog-title').textContent=titles[button.dataset.figure];
  dialog.showModal();
}));
document.getElementById('close-figure').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
const progress=document.querySelector('.reading-progress span');
function updateProgress(){const h=document.documentElement;progress.style.width=(h.scrollHeight>h.clientHeight?100*h.scrollTop/(h.scrollHeight-h.clientHeight):0)+'%';}
addEventListener('scroll',updateProgress,{passive:true});updateProgress();
const printState=new Map();
addEventListener('beforeprint',()=>document.querySelectorAll('details').forEach(d=>{printState.set(d,d.open);d.open=true;}));
addEventListener('afterprint',()=>{printState.forEach((v,d)=>d.open=v);printState.clear();});
