import test from 'node:test';
import assert from 'node:assert/strict';
import {parseColor,contrast,blend,harmony,hsl,fromHsl} from '../color.js';
test('strict color parsing handles shorthand and RGB without accepting invalid channels',()=>{assert.equal(parseColor('#abc'),'#AABBCC');assert.equal(parseColor('rgb(255, 0, 16)'),'#FF0010');for(const v of ['rgb(256,0,0)','rgb(1,2,3)bad','#12345','bad color'])assert.equal(parseColor(v),null);});
test('contrast has known black/white endpoints and is symmetric',()=>{assert.equal(contrast('#000000','#FFFFFF'),21);assert.equal(contrast('#ABCDEF','#ABCDEF'),1);assert.equal(contrast('#123456','#654321'),contrast('#654321','#123456'));});
test('mixing preserves endpoints and computes multiply and screen',()=>{assert.equal(blend('#000000','#FFFFFF',.5,'normal'),'#808080');assert.equal(blend('#FF0000','#00FF00',1,'multiply'),'#000000');assert.equal(blend('#FF0000','#00FF00',1,'screen'),'#FFFF00');});
test('harmony produces valid colors across the hue boundary',()=>{for(const mode of ['analogous','complementary','monochrome','triadic','split','square']){const colors=harmony('#FE1010',mode);assert.equal(colors.length,5);assert.ok(colors.every(c=>parseColor(c)===c));}assert.equal(fromHsl(...hsl('#37A0D2')),'#37A0D2');});
