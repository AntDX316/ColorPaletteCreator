export function parseColor(value){
  const text=value.trim();
  if(/^#?[\da-f]{3}$/i.test(text))return '#'+text.replace('#','').split('').map(x=>x+x).join('').toUpperCase();
  if(/^#?[\da-f]{6}$/i.test(text))return '#'+text.replace('#','').toUpperCase();
  const match=text.match(/^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/i);
  if(match&&match.slice(1).every(n=>+n<=255))return hex(match.slice(1).map(Number));
  return null;
}
export const rgb=color=>color.slice(1).match(/../g).map(x=>parseInt(x,16));
export const hex=values=>'#'+values.map(x=>Math.round(Math.max(0,Math.min(255,x))).toString(16).padStart(2,'0')).join('').toUpperCase();
export function hsl(color){let[r,g,b]=rgb(color).map(x=>x/255);let max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min,l=(max+min)/2,h=0,s=d?d/(1-Math.abs(2*l-1)):0;if(d){h=max===r?((g-b)/d)%6:max===g?(b-r)/d+2:(r-g)/d+4;h*=60;}return [(h+360)%360,s*100,l*100];}
export function fromHsl(h,s,l){s/=100;l/=100;const c=(1-Math.abs(2*l-1))*s,x=c*(1-Math.abs(((h%360+360)%360/60)%2-1)),m=l-c/2;const i=Math.floor(((h%360+360)%360)/60);return hex([[c,x,0],[x,c,0],[0,c,x],[0,x,c],[x,0,c],[c,0,x]][i].map(v=>(v+m)*255));}
export function contrast(a,b){const lum=c=>rgb(c).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);const x=lum(a),y=lum(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
export const ink=color=>contrast(color,'#FFFFFF')>contrast(color,'#161817')?'#FFFFFF':'#161817';
export function harmony(base,mode,count=5){const[h,s,l]=hsl(base);const offsets={analogous:[-40,-20,0,20,40],complementary:[0,0,180,180,180],triadic:[0,120,240,120,240],split:[0,150,210,150,210],monochrome:[0,0,0,0,0],square:[0,90,180,270,0]};return Array.from({length:count},(_,i)=>fromHsl(h+(offsets[mode]||offsets.analogous)[i%5],Math.max(20,s),mode==='monochrome'?20+i*15:Math.max(15,Math.min(85,l+(i-2)*7))));}
export function blend(a,b,t,mode){const aa=rgb(a),bb=rgb(b);return hex(aa.map((v,i)=>{const w=bb[i];const target=mode==='multiply'?v*w/255:mode==='screen'?255-(255-v)*(255-w)/255:w;return v*(1-t)+target*t;}));}
