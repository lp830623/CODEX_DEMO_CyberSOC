"use client";
import {useEffect, useRef, useState} from 'react';
type Envelope<T> = {data:T;revision:number};
export function useDemo<T>(seed:T,key:string,reduce:(data:T,path:string,body:Record<string,unknown>)=>void) {
  const [state,setState]=useState(seed); const [mode,setMode]=useState<'loading'|'browser'|'server'>('loading');
  const [busy,setBusy]=useState(false); const [error,setError]=useState('');
  const current=useRef<Envelope<T>>({data:seed,revision:0}); const lock=useRef(false);
  const apply=(next:Envelope<T>)=>{current.current=next;setState(next.data);};
  useEffect(()=>{let active=true;
    async function load(){
      try {const response=await fetch('/api/state');if(!response.ok)throw new Error();const data:Envelope<T>=await response.json();if(active){apply(data);setMode('server');}}
      catch {if(active){try{const saved=localStorage.getItem(key);if(saved){const next:Envelope<T>=JSON.parse(saved);if(next.data&&typeof next.revision==='number')apply(next);}}catch{localStorage.removeItem(key);}setMode('browser');}}
    } void load();return()=>{active=false;};
  // A repository has one immutable fixture and storage key.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);
  async function mutate(path:string,body:Record<string,unknown>={},method='POST') {
    if(lock.current||mode==='loading')return;lock.current=true;setBusy(true);setError('');
    try {
      let next:Envelope<T>;
      if(mode==='server'){
        const response=await fetch(path,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify({...body,expected_revision:current.current.revision})});
        if(!response.ok){if(response.status===409){const fresh=await fetch('/api/state');if(fresh.ok)apply(await fresh.json());}throw new Error(response.status===409?'Stan zmienił się w innej karcie. Wczytano aktualne dane; ponów działanie.':'Nie udało się zapisać zmiany. Spróbuj ponownie.');}
        next=await response.json();
      }else{
        const data=structuredClone(path==='/api/reset'?seed:current.current.data);
        if(path!=='/api/reset')reduce(data,path,body);
        next={data,revision:current.current.revision+1};
        try{localStorage.setItem(key,JSON.stringify(next));}catch{throw new Error('Brak miejsca na zapis w przeglądarce. Wyeksportuj raport i zresetuj demo.');}
      }
      apply(next);return true;
    }catch(e){setError(e instanceof Error?e.message:'Błąd demonstracji.');return false;}finally{lock.current=false;setBusy(false);}
  }
  return {state,mode,busy,error,mutate};
}
export function downloadReport(data:unknown,name:string){const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
