import {test,expect} from '@playwright/test';
test('complete synthetic demo journey',async({page})=>{
 await page.goto('/');await expect(page.getByText('Lokalne API',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Resetuj demo',exact:true}).click();
 await page.getByRole('button',{name:'Symuluj Brute force',exact:true}).click();
 await page.getByRole('button',{name:'Incydenty',exact:true}).click();
 await page.getByRole('button',{name:'Otwórz INC-1043',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText('Udane logowanie po serii błędów');
 await page.getByLabel('Status incydentu',{exact:true}).selectOption('resolved');
 await page.getByLabel('Zweryfikuj dowody i zakres incydentu',{exact:true}).check();
 await page.getByRole('button',{name:'Zamknij szczegóły'}).click();
 await page.reload();
 await page.getByRole('button',{name:'Dziennik działań',exact:true}).click();
 await expect(page.getByText('INC-1043: zmiana statusu na resolved.',{exact:true})).toBeVisible();
 await page.setViewportSize({width:390,height:844});
 await expect(page.getByRole('navigation')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
});
