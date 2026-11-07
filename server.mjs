import http from 'node:http';
import {readFile} from 'node:fs/promises';
const types={'.html':'text/html','.css':'text/css','.js':'text/javascript'};
http.createServer(async(req,res)=>{const path=new URL(req.url,'http://localhost').pathname;const file=path==='/'?'index.html':path.slice(1);if(!['index.html','style.css','app.js','color.js'].includes(file)){res.writeHead(404).end();return;}try{const data=await readFile(file);res.writeHead(200,{'Content-Type':types[file.slice(file.lastIndexOf('.'))]});res.end(data);}catch{res.writeHead(404).end();}}).listen(4173,'127.0.0.1',()=>console.log('http://127.0.0.1:4173'));
