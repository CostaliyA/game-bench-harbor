// Task-specific extension for joric/ootss. No reference solutions are bundled here.
export const DELTA = {right:[1,0],up:[0,1],left:[-1,0],down:[0,-1]};
const clone = x => JSON.parse(JSON.stringify(x));
const same = (a,b) => a[0]===b[0] && a[1]===b[1];
export class Game {
 constructor(board) { this.board=clone(board); this.reset(); }
 reset() {
  const b=this.board;
  this.s={heroes:b.objs.filter(o=>o.t==='Guy').map(o=>({id:o.id,kind:o.k==='wizard'?'wizard':'gemsman',p:o.p.slice(0,2),dir:['right','up','left','down'][o.d],rod:false})),rocks:b.objs.filter(o=>o.t==='Rock').map(o=>({id:o.id,p:o.p.slice(0,2)})),rod:b.objs.find(o=>o.t==='Artifact').p.slice(0,2),active:0};
  this.history=[]; return this.snapshot();
 }
 snapshot(){ return clone(this.s); }
 wall(p){ return (this.board.cols[p.join(',')]||[]).includes(0); }
 floor(p){const c=this.board.cols[p.join(',')];return !!c&&c.includes(-1)&&!c.includes(0);}
 inside(p){const [x0,y0,x1,y1]=this.board.bounds;return p[0]>=x0&&p[0]<=x1&&p[1]>=y0&&p[1]<=y1;}
 piece(p){return [...this.s.heroes,...this.s.rocks].find(o=>same(o.p,p));}
 fenced(a,b){return this.board.objs.some(o=>{if(o.t!=='Fence'||!o.f.blocking)return false;const d=Object.values(DELTA)[o.d],p=o.p,q=[p[0]+d[0],p[1]+d[1]];return (same(a,p)&&same(b,q))||(same(b,p)&&same(a,q));});}
 collect(){if(this.s.rod){const h=this.s.heroes.find(h=>same(h.p,this.s.rod));if(h){h.rod=true;this.s.rod=null;}}}
 won(){const exits=this.board.objs.filter(o=>o.t==='Door');return exits.length===2&&exits.every(e=>this.s.heroes.some(h=>same(h.p,e.p)));}
 shove(piece,d,seen=new Set()) {
  if(seen.has(piece.id))return false;seen.add(piece.id);
  let p=[piece.p[0]+d[0],piece.p[1]+d[1]];
  while(this.inside(p)&&this.wall(p))p=[p[0]+d[0],p[1]+d[1]];
  if(!this.floor(p))return false;
  const other=this.piece(p);
  if(other&&!this.shove(other,d,seen))return false;
  piece.p=p;return true;
 }
 step(action) {
  const allowed=[...Object.keys(DELTA),'switch','activate','undo','reset'];
  if(!allowed.includes(action))return {valid:false,changed:false,won:this.won(),reason:'invalid_action'};
  if(action==='reset'){this.reset();return {valid:true,changed:true,won:false,reason:'reset'};}
  if(action==='undo'){const old=this.history.pop();if(old)this.s=old;return {valid:true,changed:!!old,won:this.won(),reason:'undo'};}
  const before=this.snapshot(),h=this.s.heroes[this.s.active];let reason='blocked';
  if(action==='switch'){this.s.active=1-this.s.active;reason='switch';}
  else if(action==='activate'){
   if(h.rod){const d=DELTA[h.dir],p=[h.p[0]+d[0],h.p[1]+d[1]],target=this.piece(p);if(target&&this.shove(target,d))reason='rod';else this.s=clone(before);}
   else reason='no_rod';
  } else {
   const d=DELTA[action];let target;
   if(h.kind==='wizard'){
    let p=[h.p[0]+d[0],h.p[1]+d[1]];
    while(this.inside(p)&&!this.wall(p)) {target=this.piece(p);if(target)break;p=[p[0]+d[0],p[1]+d[1]];}
   }
   if(target){const old=h.p;h.p=target.p;target.p=old;h.dir=action;reason='swap';}
   else {const p=[h.p[0]+d[0],h.p[1]+d[1]];if(this.floor(p)&&!this.piece(p)&&!this.fenced(h.p,p)){h.p=p;h.dir=action;reason='walk';}}
  }
  this.collect();const changed=JSON.stringify(before)!==JSON.stringify(this.s);
  if(changed)this.history.push(before);
  return {valid:true,changed,won:this.won(),reason};
 }
}
