const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const root=__dirname,html=fs.readFileSync(path.join(root,'../vrchat-animator-check/index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function fixture(opts={}){
 const elements={checks:{handlers:{}},report:{hidden:true,textContent:''},copyreport:{hidden:true,handlers:{}},copystatus:{textContent:''}};
 for(const el of Object.values(elements))el.addEventListener=(name,fn)=>(el.handlers[name]=fn);
 const boxes=Array.from({length:5},(_,i)=>({number:String(i+1),labels:[],getAttribute(){return this.number},appendChild(x){this.labels.push(x)},querySelector(){return this.labels.map(l=>l.children[0]).find(x=>x.checked)},closest(){return {querySelector:()=>({textContent:`${i+1}. Q${i+1}`})}}}));
 const document={getElementById:id=>elements[id],createTextNode:text=>({textContent:text}),createElement:tag=>tag==='input'?{}:{children:[],appendChild(x){this.children.push(x)}},querySelectorAll:sel=>sel==='[data-question]'?boxes:boxes.map(b=>b.querySelector()).filter(Boolean)};
 let calls=[],resolveCopy,rejectCopy;
 const navigator=opts.unsupported?{}:{clipboard:{writeText(text){calls.push(text);return new Promise((resolve,reject)=>{resolveCopy=resolve;rejectCopy=reject})}}};
 vm.runInNewContext(script,{document,navigator});
 const fire=name=>elements.checks.handlers[name]?.({preventDefault(){}});
 const select=(i,val)=>{boxes[i].labels.forEach(l=>l.children[0].checked=l.children[0].value===val);fire('change')};
 return {elements,calls,select,submit:()=>fire('submit'),copy:()=>elements.copyreport.handlers.click(),resolve:()=>resolveCopy(),reject:()=>rejectCopy()};
}
(async()=>{
 const passed=[];
 assert.match(html,/\[hidden\]\{display:none!important\}/);passed.push('explicit hidden CSS rule overrides button display (static)');
 let f=fixture(); f.copy();assert.equal(f.calls.length,0);assert.equal(f.elements.report.hidden,true);passed.push('initial result cannot be copied');
 for(let i=0;i<5;i++)f.select(i,'ok');f.submit();f.select(0,'risk');assert.equal(f.elements.report.hidden,true);assert.equal(f.elements.report.textContent,'');assert.equal(f.elements.copyreport.hidden,true);assert.match(f.elements.copystatus.textContent,/もう一度/);f.copy();assert.equal(f.calls.length,0);passed.push('answer change invalidates report and prevents stale copy');
 f.submit();assert.match(f.elements.report.textContent,/気になる 1件 ／ 問題なし 4件 ／ 未確認 0件/);assert.equal(f.elements.copyreport.hidden,false);assert.equal(f.elements.copystatus.textContent,'');passed.push('resubmit produces current counts and restores copy');
 f.copy();assert.equal(f.calls.length,1);f.select(1,'risk');const message=f.elements.copystatus.textContent;f.resolve();await Promise.resolve();assert.equal(f.elements.copystatus.textContent,message);passed.push('late clipboard success cannot overwrite answer-change warning');
 f=fixture({unsupported:true});f.submit();f.copy();assert.match(f.elements.copystatus.textContent,/コピー機能が使えません/);passed.push('unsupported clipboard keeps manual fallback');
 const result={status:'passed',passed:passed.length,cases:passed,scope:'Node VM DOM fixture plus CSS source assertion; not a rendered-browser or mobile-device pass',public_site_changed:false};
console.log(JSON.stringify(result,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
