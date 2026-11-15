import {Game} from './game.mjs';
const board=await (await fetch('board.json')).json();const game=new Game(board);
const definitions=`title Heroes and Artifacts 7
noaction
noundo
norestart
text_color white
background_color #101722

OBJECTS

Background
#22394c
00000
00000
00000
00000
00000

Floor
#dac79b
00000
00000
00000
00000
00000

Wall
#a8604a #733f35
11111
00001
11111
01000
11111

Goal
#25bd86 #dbffe9
00000
01110
01010
01110
00000

Gemsman
#ff9e39 Pink DarkBrown
.000.
.111.
00000
.000.
.2.2.

Wizard
#2266FF Pink
.000.
.010.
00000
.000.
00000

Rock
#777777 #bbbbbb
.111.
11001
10001
10001
.111.

Rod
#ffe12e
..0..
.000.
..0..
..0..
.....

Held
#ffe12e
.....
.....
....0
...00
....0

FenceL
#442b10 #efbd68
10...
10...
10...
10...
10...

FacingUp
white
..0..
.000.
.....
.....
.....

FacingDown
white
.....
.....
.....
.000.
..0..

FacingLeft
white
.....
.0...
00...
.0...
.....

FacingRight
white
.....
...0.
...00
...0.
.....

LEGEND
Player = Gemsman or Wizard
`;
const dirName={up:'FacingUp',down:'FacingDown',left:'FacingLeft',right:'FacingRight'};
function render(){
 const [x0,y0,x1,y1]=board.bounds;let rows=[],lookup=new Map(),legend=[];
 const alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!$%&*+-/:;<>?@^_~';
 for(let y=y1;y>=y0;y--){let row='';for(let x=x0;x<=x1;x++){
  const p=[x,y],parts=['Background'];if(game.floor(p))parts.push('Floor');else if(game.wall(p))parts.push('Wall');
  if(board.objs.some(o=>o.t==='Door'&&o.p[0]===x&&o.p[1]===y))parts.push('Goal');
  if(game.s.rod&&game.s.rod[0]===x&&game.s.rod[1]===y)parts.push('Rod');
  const piece=game.piece(p);if(piece){parts.push(piece.kind==='wizard'?'Wizard':piece.kind==='gemsman'?'Gemsman':'Rock');if(piece.kind){parts.push(dirName[piece.dir]);if(piece.rod)parts.push('Held');}}
  if(board.objs.some(o=>o.t==='Fence'&&o.p[0]===x&&o.p[1]===y&&o.d===2))parts.push('FenceL');
  const key=parts.join(' and ');if(!lookup.has(key)){const ch=alphabet[lookup.size];if(!ch)throw Error('Too many tile types');lookup.set(key,ch);legend.push(ch+' = '+key);}row+=lookup.get(key);
 }rows.push(row);}
 const src=definitions+legend.join('\n')+'\n\nSOUNDS\n\nCOLLISIONLAYERS\nBackground\nFloor, Wall\nGoal, Rod\nGemsman, Wizard, Rock\nFenceL\nFacingUp, FacingDown, FacingLeft, FacingRight\nHeld\n\nRULES\n\nWINCONDITIONS\nall Goal on Player\n\nLEVELS\n'+rows.join('\n');
 compile(['loadLevel',0],src);if(errorCount)throw Error('PuzzleScript compile: '+errorStrings.join(';'));
 textMode=false;canvasResize();redraw();
 const grid=document.querySelector('#grid');grid.width=canvas.width;grid.height=canvas.height;
 const ctx=grid.getContext('2d');ctx.strokeStyle='rgba(15,20,30,.22)';ctx.lineWidth=1;
 for(let i=0;i<=x1-x0+1;i++){ctx.beginPath();ctx.moveTo(xoffset+i*cellwidth,yoffset);ctx.lineTo(xoffset+i*cellwidth,yoffset+(y1-y0+1)*cellheight);ctx.stroke();}
 for(let i=0;i<=y1-y0+1;i++){ctx.beginPath();ctx.moveTo(xoffset,yoffset+i*cellheight);ctx.lineTo(xoffset+(x1-x0+1)*cellwidth,yoffset+i*cellheight);ctx.stroke();}
 ctx.fillStyle='#c4cedb';ctx.font='11px Arial';ctx.textAlign='center';
 for(let i=0;i<=x1-x0;i++)ctx.fillText(String(i),xoffset+(i+.5)*cellwidth,yoffset-3);
 for(let i=0;i<=y1-y0;i++)ctx.fillText(String(i),xoffset-10,yoffset+(i+.5)*cellheight+4);
 const h=game.s.heroes[game.s.active];document.querySelector('#status').textContent=`ACTIVE: ${h.kind.toUpperCase()} | `+game.s.heroes.map(h=>`${h.kind}: facing ${h.dir}${h.rod?' · carries ROD':''}`).join(' | ');
 document.querySelector('#result').textContent=game.won()?'SUCCESS':'';
}
window.evalGame={reset(){game.reset();render();return game.snapshot();},observe(){return {state:game.snapshot(),won:game.won()};},step(a){const r=game.step(a);render();document.querySelector('#feedback').textContent=`Last action: ${a} — ${r.reason}`;return r;}};
// Native keyboard movement is disabled: all evaluation input goes through the extension.
window.addEventListener('keydown',e=>{e.preventDefault();e.stopImmediatePropagation();},{capture:true});
render();window.evalReady=true;
