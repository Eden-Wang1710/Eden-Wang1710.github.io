document.body.classList.add('js-enabled');
const tracks=[...document.querySelectorAll('.track')];
const allSteps=[...document.querySelectorAll('.step')];
const status=document.getElementById('status');
const search=document.getElementById('step-search');
const active={baseline:0,srcv:0};
let view='compare';
function visibleSteps(id){return [...document.getElementById(id).querySelectorAll('.step:not([hidden])')];}
function updateControls(id){
  const steps=visibleSteps(id);active[id]=Math.min(active[id],Math.max(0,steps.length-1));
  document.querySelector(`[data-position="${id}"]`).textContent=steps.length?`${active[id]+1} / ${steps.length} milestones`:'0 milestones';
  document.querySelector(`[data-prev="${id}"]`).disabled=!steps.length||active[id]===0;
  document.querySelector(`[data-next="${id}"]`).disabled=!steps.length||active[id]===steps.length-1;
  document.getElementById(id).querySelector('.empty').hidden=steps.length>0;
}
function setView(next){
  view=next;
  tracks.forEach(t=>t.hidden=view!=='compare'&&t.id!==view);
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
  document.getElementById('tracks').classList.toggle('single-view',view!=='compare');
}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
function selectStep(id,index,scroll=false){
  const steps=visibleSteps(id);if(!steps.length)return;
  active[id]=Math.max(0,Math.min(index,steps.length-1));
  steps.forEach((d,i)=>d.open=i===active[id]);
  const current=steps[active[id]];
  updateControls(id);
  history.replaceState(null,'','#'+current.id);
  if(scroll)current.scrollIntoView({behavior:'auto',block:'nearest'});
  status.textContent=`${id==='srcv'?'SRCV':'CLM-Agent'}: ${current.querySelector('.step-title').childNodes[0].textContent.trim()}`;
}
for(const id of ['baseline','srcv']){
  document.querySelector(`[data-prev="${id}"]`).addEventListener('click',()=>selectStep(id,active[id]-1,true));
  document.querySelector(`[data-next="${id}"]`).addEventListener('click',()=>selectStep(id,active[id]+1,true));
  updateControls(id);
}
allSteps.forEach(step=>step.querySelector('summary').addEventListener('click',()=>{
  const id=step.closest('.track').id;
  active[id]=visibleSteps(id).indexOf(step);updateControls(id);
  history.replaceState(null,'','#'+step.id);
}));
search.addEventListener('input',()=>{
  const query=search.value.trim().toLowerCase();
  allSteps.forEach(d=>{d.hidden=!!query&&!d.textContent.toLowerCase().includes(query);if(query&&!d.hidden)d.open=true;});
  for(const id of ['baseline','srcv']){active[id]=0;updateControls(id);}
  status.textContent=query?`${allSteps.filter(d=>!d.hidden).length} matching milestones across both systems`:'';
});
document.getElementById('expand-all').addEventListener('click',()=>tracks.filter(t=>!t.hidden).forEach(t=>t.querySelectorAll('.step:not([hidden])').forEach(d=>d.open=true)));
document.getElementById('collapse-all').addEventListener('click',()=>tracks.filter(t=>!t.hidden).forEach(t=>t.querySelectorAll('.step').forEach(d=>d.open=false)));
function revealHash(){
  const id=location.hash.slice(1);const step=document.getElementById(id);
  if(!step?.classList.contains('step'))return;
  if(search.value){search.value='';search.dispatchEvent(new Event('input'));}
  const track=step.closest('.track');if(track.hidden)setView('compare');
  step.hidden=false;step.open=true;active[track.id]=visibleSteps(track.id).indexOf(step);updateControls(track.id);
  requestAnimationFrame(()=>step.scrollIntoView({block:'start'}));
}
addEventListener('hashchange',revealHash);revealHash();
document.querySelectorAll('[data-link]').forEach(button=>button.addEventListener('click',async()=>{
  const url=new URL(location.href);url.hash=button.dataset.link;
  try{await navigator.clipboard.writeText(url.href);status.textContent='Step link copied.';button.textContent='Copied ✓';setTimeout(()=>button.textContent='Copy step link →',1800);}
  catch{history.replaceState(null,'',url);status.textContent='This step is now in the address bar. Copy the URL to share it.';}
}));
const printState=new Map();let savedView;
addEventListener('beforeprint',()=>{savedView=view;setView('compare');allSteps.forEach(d=>{printState.set(d,{open:d.open,hidden:d.hidden});d.open=true;d.hidden=false;});});
addEventListener('afterprint',()=>{printState.forEach((s,d)=>{d.open=s.open;d.hidden=s.hidden;});printState.clear();setView(savedView||'compare');});
