---
title: "<small>Zadání zápočtového projektu NDBI047</small><br/>Predikce hodnocení filmů"
author: "Dominik Matula, 4. 4. 2019"
header-includes:
   - \usepackage{amsmath}
output:  
  html_document:
    keep_md: true
    highlight: tango
    toc: true
    toc_float: true
    toc_depth: 1
    includes:
      in_header: "../../hlavicka_logo.html"
---

<style>
body {
  font-family: Helvetica;
}

.leftindent {
  padding-left: 80px;
}

.dulezite {
  color: red;
}

.neplati {
  color: red;
  text-decoration: line-through;
}


.nedulezite {
  color: gray
}

details {
  margin: 1em 0;
}

details > summary {
  cursor: pointer;
  background-color: auto;
  padding: 0 1em;
  border-style: dotted;
  border-width: 1px;
  border-color: gray;
}

details[open], .bonus {
  background-color: #fff3e1;
  cursor: default;
  border-style: dotted;
  border-width: 1px;
  border-color: gray;
}
details[open] > summary {
  background-color: #fff3e1;
  border-style: none;
}

hr {
    display: block;
    height: 1px;
    border: 0;
    border-top: 2px dotted #ccc;
    margin: 1em 1em;
    padding: 5px; 
}

</style>




## Poznámky úvodem {.tabset}

### Důležité odkazy

* Stránka předmětu [NDBI047](https://is.cuni.cz/studium/predmety/index.php?do=predmet&kod=NDBI047) 
* GitHub [repozitář](https://github.com/profinit/MFF-BDT) předmětu
* Kaggle stránka [úlohy](https://www.kaggle.com/t/d707bf187ab64d4bbe9008c133e8c9b8)
    * Pokud nemáte účet na Kaggle, založte si jej.
* Kontakt: `dominik.matula@profinit.eu`

### Podmínky zápočtu 


* Celkem je možné získat 100 bodů:
    * 40 b. za vypracování **povinných** úloh
    * 20 b. za vypracování **bonusových** úloh
    * 20 b. za implementaci (spolu s reportem odevzdáváte i své řešení/kód)
    * 20 b. za report

* K úspěšnému složení je potřeba získat **alespoň 50 bodů**, přičemž známkování je následovné:
    * **1** ... >80 b.
    * **2** ... 65-80 b.
    * **3** ... 50-64 b.
    * **4** ... <50 b.

* Svá řešení odevzdejte do (<span class='dulezite'> [bude doplněno] </span>, předběžně: alespoň 5 dní před termínem zkoušky), nejlépe e-mailem na adresu cvičícího.
* Na zkoušce proběhne diskuse nad Vaším řešením.

    


### Poznámky

* Budeme se zabývat __předpovídáním uživatelských hodnocení filmů__ nad datasetem pocházejícím z projektu [MovieLens.org](movielens.org).
* Postupně zkonstruujeme sérii predikcí hodnocení na základě známé historie hodnocení (daného uživatele, ostatních  uživatelů i jednotlivých filmů).
* Předpovědi budeme vyhodnocovat centrálně pomocí __malé interní soutěže__ na platformě [Kaggle](https://www.kaggle.com/c/mff-ndbi047-2019). 
    * __Umístění__ v této soutěži nicméně __nemá samo o sobě vliv na hodnocení zápočtového projektu.__
    * Nejprve je třeba registrovat se na portále [Kaggle](kaggle.com).
    * Posléze můžete vstoupit do soutěže přes tento link: `https://www.kaggle.com/t/d707bf187ab64d4bbe9008c133e8c9b8`
    * Podrobnější intro k _malé interní soutěži_ - viz cvičení, na němž byl zápočtový projekt zadán.
* __Cílem tohoto projektu__ není implementovat bezchybný nástroj na predikci uživatelských hodnocení, nýbrž ___demostrovat schopnost používat různé Big data nástroje/technologie__ na symysluplné úloze.
* Není-li řečeno jinak, je seznam otázek pouze návodný.
    * Tj. na jednu stranu není nutné zodpovědět všechny podbody otázek, na druhou stranu iniciativě se meze nekladou :).
    * Výstupem by mělo být smysluplné pojetí daného problému, resp. demonstrace schopnosti takové řešení podat.).
    * Jednotlivé kapitoly jsou doplněné o __bonusové__ úlohy. 
* V případě dotazů/nesrovnalostí/připomínek se obracejte na `dominik.matula@profinit.eu`.



```bash
# spusteni na Metacentru: 
export PYTHONIOENCODING=utf8
pyspark --master yarn --num-executors 2 --executor-memory 4G \
--packages com.databricks:spark-csv_2.10:1.5.0

# POZN: pro velké úlohy (napr. UU-CF) bude patrne
# potreba navysit prostredky. 
```


### Značení

V textu budeme používat mj. následující označení:

* __Uživatel__: $u \in U$
* __Film__: $f \in F$
* __Hodnocení__ filmů uživateli - matice $R = \left( r_{u,f} \right)_{u\in U, f\in F}$
* __Predikce__ hodnocení filmů uživateli - matice $P = \left( p_{u,f} \right)_{u \in U, f \in F}$

* Pro uživatele $u \in U$ dále označíme
    * $F_u$ - viděné/hodnocené filmy,
    * $R_u$ - hodnocení,
    * $P_u$ - predikce hodnocení.

* Pro film $f \in F$ dále označíme
    * $U_f$ - diváky/hodnotitele,
    * $R_f$ - hodnocení,
    * $P_f$ - predikce hodnocení.

* Pokud v průběhu řešení projektu dojde k redukci úloh (např. pro nemožnost napočítat kýžené věci na Metacentru), budou vše probráno na cvičení a v zadání budou příslušné části zadání označeny <span class="neplati">takto</span>.


</div>

***

<div>

# Načtení a explorace dat {.tabset}

> <span class='nedulezite'>základ: 5 b.<br>bonus: 2 b.</span>

* Stáhněte si data z [Kaggle](https://www.kaggle.com/c/mff-ndbi047-2019/data) stránky interní *soutěže*.
    * Datovou sadu nahrajte na [Metacentrum](https://www.metacentrum.cz/cs/hadoop/index.html) na HDFS.
* Jedná se o upravenou datovou sadu [MovieLens](https://movielens.org). V rámci explorace data, jenž máte k dispozici, prozkoumejte a udělejte si o nich názor. Mj. zodpovězte následující otázky:
    * __Jaká data máte k dispozici? Co obsahují? Jaký je mezi nimi vztah?__ (Přestože námi zkoumaný dataset je značně upravený, hodí se nahlédnout do [ReadMe](http://files.grouplens.org/datasets/movielens/ml-latest-README.html) původního datasetu.)
    * __Jak velká je testovací a trénovací množina__ (počet uživatelů, počet filmů, počet hodnocení)? 
    * __Kteří uživatelé jsou nejaktivnější v hodnocení?__ (počet hodnocení, průměrné hodnocení)
    * __Které filmy jsou nejatraktivnější?__ (počet hodnocení, průměrné hodnocení)
    * __Jaké je časové zasazení testovací a trénovací množiny?__ (Při prezentaci výsledků nezapomeňte převést `timestamp` do čitelnějšího formátu - mohla by se vám hodit funkce `to_utc_timestamp` z modulu `pyspark.sql.functions`). 
    * __Vyskytují se v datech nějaké nesrovnalosti?__ (např. opakovaná hodnocení téhož filmu jedním uživatelem, ...)
    * __Jaké procento uživatelů hodnotilo alespoň 1 % filmů? A naopak?__ (příp. zkuste i jiné hraniční hodnoty, např. 0.1 %, ...)
    * ... 
* Využijte vazby mezi tabulkami a zodpovězte obdobné otázky pro _tagy_, resp. _genome-tagy_ a _žánry filmů_. Například:
    * __Které tagy jsou nejčastější__ (počet výskytů, počet udělivších uživatelů, počet označených filmů)
    * __Jak jsou zastoupené jednotlivé žánry filmů?__ (počet filmů, počet hodnocení, počet hodnotivších uživatelů; <span class="pozn">V případě žánrů bude nejprve potřeba udělat preprocessing tabulky `movies.csv`)</span>. 
    * __Kteří uživatelé jsou nejvíce/nejméně vyhranění?__ (hodnotí jen filmy dané žánru)
    * __Jaké je průměrné _stáří hodnocení_ dle žánru filmu?__ (obdobně lze pro tagy, ...) Co když vezmete v úvahu rok, ve kterém byl film publikován?
    * ...

<details><summary>BONUS</summary>

* Místo prosté odpovědi (např. _'Nejatraktivnějším filmem je LotR'_) je dobrým zvykem přidat základní popisné statistiky.
    * __Zkuste zachytit odpověď formou tabulky dávající čtenáři souhrnnou informaci__ (např. u nejatraktivnějších filmů můžeme zaznamenat počet hodnocení, průměrném hodnocení, medianovém hodnocení, od kdy je film hodnocen, ...)
* Často je lepší namísto tabulek uvádět grafy (umožní rychlejší náhled na věc, srovnání jednotlivých položek, ...). 
    * __Vyberte si alespoň některé z výše položených otázek a odpověď doprovoďte vhodným grafem.__
    * Nezapomeňte doplnit správné a informativní popisky (titulek, osy, legenda).
* Najděte si další data provázatelnná s tímto datasetem, např. [Imdb](https://www.imdb.com/interfaces/) dataset. Je-li to licenčně vpořádku, nahrajte tento dataset rovněž na HDFS Metacentra.
    * __Jaká data jste našli?__ (kde, licence) Co v datech je? K čemu je můžeme využít?
    * __Jak se váží k původním datům?__
    * __Uveďte základní popisné statistiky těchto dat.__

</details>




# Základní modely {.tabset}

> <span class='nedulezite'>základ: 5 b.<br>bonus: 4 b.</span>

V této části projektu se konečně dostaneme k predikování uživatelských hodnocení. <span class="nedulezite">Řešením odevzdávaným k ohodnocení Kagglem by měl být `.csv` soubor o dvou sloupcích - `Id` (z `ratings_TEST.csv`) a `Predicted` (predikované hodnocení; reálné číslo, ideálně mezi 0 a 5; použijte desetinnou tečku).</span> Začneme od základních odhadů získaných agregací hodnocení podle různých kritérií.

* Zkuste predikovat hodnocení filmů následujícími přístupy:
    * __Celkový průměr hodnocení__ ( $\bar{r}$ )
    * __Průměrné hodnocení uživatele__  ( $\bar{r}_u$ )
    * __Průměrné hodnocení filmu__ ( $\bar{r}_f$ )
* Poměrně přímočarým zobecněním výše uvedených _predikcí průměrem_ by byla konstrukce průměrných hodnocení pro různé socio-demografické skupiny.
    * Např. `muži/ženy`, `staří/mladí`, `lidé žijící ve městech/na venkově`, skupiny dle `země`, `etnika`, `příjmu`, ...
    * Bohužel v našem datasetu tuto informaci nemáme k dispozici a proto tento krok **přeskočíme**.
* Víc informací máme o filmech - můžeme se zkusit použít __průměrné hodnocení žánru__, do nějž hodnocený film spadá.
    * Vzhledem k tomu, že daný film má zpravidla uvedeno několik žánrů, budete při predikci muset jednotlivé průměry zkombinovat;
    * Nabízí se **průměr**, tj. průměr průměrných hodnocení všech žánrů, do nichž byl daný film zařazen; lepší variantou by mohl být **vážený průměr** (viz bonusové otázky).
* Intuitivně chápeme, že tyto modely budou příliš hrubé. Lepších výsledků bychom potenciálně mohli dosáhnout tím, že vezmeme **vpotaz vícero z těchto základních modelů**. Zkuste implementovat následující řešení:
$$ 
p_{u,f} = \bar{r} + b_u  + b_f,
$$
kde _baseline predictors_ ($b_u$ - pro uživatele $u \in U$,  $b_f$ - pro film $f \in F$) mají následující předpis: 
\begin{align}
b_u &= \frac{1}{|F_u|}\cdot\sum_{f\in F_u}(r_{u,f} - \bar{r}), \tag{1} \\
b_f &= \frac{1}{|U_f|}\cdot\sum_{u\in U_f}(r_{u,f} - b_u - \bar{r}). \tag{2}
\end{align}

    * __Jak byste interpretovali $b_u$ a $b_f$?__    
    * __Překonává tento model svým výkonem _prosté průměry_ použité výše?__

<details><summary>BONUS</summary>

* V případě kombinování průměrných hodnocení dle žánrů lze postupovat sofistikovaněji. 
    * Zkuste např. __vážený průměr__ (kde vahou může být normovaný počet hodnocení, filmů, či uživatelů hodnotivších daný žánr). __Který přístup zafungoval nejlépe?__
    * Obdobně můžeme predikovat na základě průměrných hodnocení `genome-tag`ů. Zde můžeme k vážení použít `genome-scores`.
* K dispozici mám vcelku rozsáhlou historii hodnocení. __Jak se změní výkonnost modelů, pokud se omezím na hodnocení:__
    * z posledních $k$ let?
    * z první $k$ let?
    * z daného roku? (<span class="nedulezite">Nejprve je potřeba pro každý film stanovit, ze kterého roku pochází - tuto informaci můžete získa z `title` v datasetu `movies.csv`. K tomu se může hodit funkce `regexp_extract`...</span>)
    * ...
* V případě, že má entita, na jejíž úrovni provádím výpočet (tj. v našem případě film, uživatel, žánr, ...), __jen málo pozorování, je takto získaný odhad značně nestabilní__. 
    * Zkuste tento problém vyřešit kombinací spočtených predikcí - např. průměrné hodnocení uživatele nahraďte celkovým průměrným hodnocením všech uživatelů, pokud daný uživatel hodnotil méně než __20 filmů__. Zkuste i pro jiné hranice. __Jak se změnila výkonnost predikcí?__
    * Obdobně můžeme upravit _baseline predictors_ (1, 2) přidáním regularizačních konstant $\beta_u$ ($\in R_0^+$), resp. $\beta_f$ ($\in R_0^+$): 
\begin{align}
b_u^* &= \frac{1}{|F_u| + \beta_u}\cdot\sum_{f\in F_u}(r_{u,f} - \bar{r}), \tag{1'}\\
b_f^* &= \frac{1}{|U_f| + \beta_f}\cdot\sum_{u\in U_f}(r_{u,f} - b_u - \bar{r}). \tag{2'}
\end{align}
        * __Zkuste toto implementovat pro různé hodnoty regularizačních koeficientů__ (např. (20, 20), (100, 15), ...). Došlo ke zlepšení?
        * __Jaký mají tyto regularizační parametry význam__?
    * Další možností je přidat _baseline predictor_ pro jinou entitu/vlastnost - například žánr hodnoceného filmu. 
        * __Jaký by mohl mít předpis $b_z$?__ (Vyjděte z předpisu (2) pro $b_f$.) Vzhledem k tomu, že jeden film nezřídka spadá do více žánrů, budeme při predikci hodnocení muset vhodně zkombinovat. Nabízí se jednotlivá $b_z$ zprůměrovat, tj.
        $$\tag{3}p_{u,f} = \frac{1}{|Z_f|}\sum_{z \in Z_f} b_z, \forall u \in U$$ kde $Z_f$ je množina žánrů, do nichž byl film $f$ zařazen.
        * __Zlepšila se výkonost modelu? Jak?__
* Pokud jste v předchozí části získali další datové sady (např. IMDb), zkuste vytvořit několik dalších baseline modelů. Například:
    * __Průměrné hodnocení režiséra__
    * __Průměrné hodnocení herců__. Jeden film má zpravidla celou žadu herců; budeme muset postupovat stejně jako v (3) v případě žánrů.
* Průměr není příliš robustní (jedno odlehlé pozorování dokáže nadělat paseku; nicméně pro pevně stanovený a poměrně úzký interval hodnocení, jak máme v našem případě, by to neměl být příliž velký problém).
    * Jak si povedou baseline prediktory, když místo průměru použiji `median`? 

</details>






# Pokročilé modely {.tabset .tabset-pills}

V této části se budeme zabývat pokročilejšími způsoby predikce uživatelských hodnocení na základě 

* předchozích hodnocení daného uživatele,
* hodnocení ostatních uživatelů,
* dalších informací (charakteristiky filmů, ...)

Vzhledem k tomu, že na **Metacentru** máme k dispozici poměrně **zastaralou verzi Apache Spark**, jenž má poměrně omezené možnosti (srovnejte dokumentaci v [1.6.0](https://spark.apache.org/docs/1.6.0/api/python/index.html) a [poslední verze](https://spark.apache.org/docs/latest/api/python/index.html)), bude třeba řadu věcí připravit od píky. <span class="nedulezite">Příkladem je _násobení řídkých matic_ (již jste implementovali na cvičení v první polovině března).</span> 



## A) User-User Collaborative filtering {.leftindent}

### User-User Collaborative filtering

> <span class='nedulezite'>základ: 8 b.<br>bonus: 3 b.</span>

* **Myšlenka**: Najděme $k$ uživatelů, kteří hodnotí filmy podobně jako uživatel $u$. Hledanou predikcí $p_{u,f}$ pak bude <span class="nedulezite">(vážený)</span> průměr hodnocení filmu $f$ těmito uživateli.
* Viz též třeba [wiki](https://en.wikipedia.org/wiki/Collaborative_filtering).


### Postup

<details>
  <summary>Určíme podobnost uživatelů $sim(u,v), \forall u,v\in U$.</summary>
  
* V datech máme jen málo informace o uživatelích. Můžeme ale vyjít ze samotných hodnocení $R$.
    * <b>hint</b>: vytvořte z hodnocení _řídkou matici_. 
    * <b>hint</b>: Vzhledem k rozsáhlosti dat je vhodné se podívat do modulu `pyspark.mllib.linalg.distributed`; přímo se nabízí `CoordinateMatrix`

* __Zkuste implementovat__ následující metody:
    * __[Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)__ 
        * <b>hint</b>: po doplnění chybějících hodnocení 0 a znormování hodnocení lze řešit *skalárním osučinem vektorů*.
        * Mimochodem, ve sparku `2.0.0` už je k dispozici metoda `columnSimilarities()` třídy `CoordinateMatrix`, která tohle udělá za vás. Bohužel na Metacentru si toto budete muset napsat sami. 
    * __[Pearsonův korelační koeficient](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient)__
</details>

<details>
  <summary>Pro každého uživatele najdeme jeho okolí $N_u$ představující $k$ nejbližších (nejpodobnějších) uživatelů.</summary>

* Samozřejmě pro každou podobnost zvlášť.
* __Zvolte $k$ "rozumně" velké__, resp. zopakujte pro různé volby $k$. 
    *  (Zkuste např. 10, 20, 50 či 100 filmů)
    * <b>hint</b> Nezapomeňte, že při předpovídání berete v úvahu **pouze ty sousedy, kteří daný film již hodnotili**. 
* Při hledání sousedů berte vpotaz pouze uživatele, s nimiž má vyšetřovaný uživatel _nezápornou_ podobností; je-li takových uživatelů méně než $k$, vezměte všechny dostupné.
* Viz též [wiki](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)
</details>

<details>
  <summary>Predikujte hodnocení uživatele $u$ filmu $f$ ($r_{u,f}$) na základě hodnocení filmu $f$ jeho nejbližšími sousedy.</summary>
  
* Označme $N_f(u)$ ty sousedy uživatele $u$, kteří film $f$ skutečně hodnotili). Kýženou predikci můžeme spočítat jako průměr hodnocení sousedů, a sice:
    * __Neváženě__, tj. $$\tag{4a} p_{u,f} = \frac{1}{N_f(u)}\cdot\sum_{v\in N_f(u)}r_{v,f}$$
    * __Váženě__, tj. $$\tag{4b} p_{u,f} = \frac{1}{N_f(u)}\cdot\frac{\sum_{v\in N_f(u)} sim(v,u) \cdot r_{v,f}}{\sum_{v\in N_f(u)}|sim(v,u)|}.$$ 
    * __Implementujte a ověřte výkonnost obou přístupů.__
* Vzhledem k tomu, že různí uživatelé mohou hodnotit na různých škálách <span class="nedulezite">(př. _optimisté_ dávající nejhůř 3 hvězdičky vs. _pesimisté_ dávající 3 hvězdičky jen těm nejlepším filmům...)</span>, je vhodné namísto hodnocení pracovat s odchylkami:
    * __Neváženě__: $$\tag{4a'} p_{u,f} = \bar{r}_u + \frac{1}{N_f(u)}\cdot\sum_{v\in N_f(u)}(\bar{r}_v - r_{v,f})$$
    * __Váženě__: $$\tag{4b'} p_{u,f} = \bar{r}_u + \frac{1}{N_f(u)}\cdot\frac{\sum_{v\in N_f(u)}sim(v,u)\cdot (\bar{r}_v - r_{v,f})}{\sum_{v\in N_f(u)}|sim(v,u)|}.$$
    * Opět __implementujte a ověřte výkonnost obou přístupů.__
    * V případě průměrování odchylek se může stát, že výsledná predikce bude mimo platnou škálu 0-5 hvězdiček.
        * __Proč/Kdy k tomu může dojít?__
        * __Jak se v takovém případě zachovat?__
* Pokud jste zvolili příliš malé $k$, může se stát, že $N_f(u) = \emptyset$.
    * __Jak se v takovém případě zachováte?__
    * <b>hint</b>: zkuste použít predikce z některého ze základních přístupů.
</details>


<details><summary>BONUS</summary>

* Při výpočtu podobnosti se __doporučuje vycházet z reziduí__ po některém ze základních modelů.
    * Tj. namísto podobnosti vektorů hodnocení $\mathbf{r}_u, \mathbf{r_v}$ zjišťuji podobnost vektorů $\mathbf{r}_u - \mathbf{b}_u$ a $\mathbf{r}_v - \mathbf{b}_v$. Nebo ještě jinak, namísto matice $R$ budeme používat matici s prvky $$\begin{cases}
    r_{u,f} - b_{u,f},& \exists r_{u,f}\\
    0,              & \text{jinak.}
\end{cases}$$
    * Zkuste implementovat a zjistěte, zda došlo ke zlepšení predikcí.
    * <b>hint</b>: Nezapomeňte, že v případě (4a') a (4b') __je třeba také nahradit__ průměrné hodnocení uživatele $v$ (tj. $r_v$) za jeho __průměrné reziduum__ (tj. průměrnou odchylku od daného _baseline_ predikce $b_{v,f}$).
    * __K čemu je tato úprava dobrá?__
* Namísto vah $sim(v,u)$ můžeme použít jejich __vhodnou transformaci.__
    * Příkladem mohou být váhy $sim(v,u)^2$, které dávají větší důraz na podobnější jedince.
    * Zkuste tuto úpravu implementovat a zjistěte, zda došlo ke zlepšení predikcí.
    * <b>hint</b>: nezapomeňte adekvátně upravit i jmenovatel výrazu.
* Zkuste implementovat i nějakou další míru podobnosti uživatelů, např.:
    * **_Adjusted Cosine similarity_**, která je definována jako podobnost odchylek hodnocení uživatelů od jejich průměrného hodnocení. <br/>Tj. standardní _cosine similarity_ aplikovaná na vektory $r_u -\bar{r}_u$. (Jak toto souvisí s prvním bodem těchto bonusových úloh?)
    * **Koeficient [Spearmenovy pořadové korelace](https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient)**, či **[mean-squared difference]()**, ...
    * Další možností je **_Jacardova vzdálenost_**: $$ J(x,y) = \frac{|F_x \cap F_y|}{|F_x \cup F_y|}.$$ Ano, zanedbáváme zde konkrétní hodnocení jednotlivých filmů; namísto toho se opíráme o _self-filtering_. (Tj. budu se dívat jen na ty filmy, o kterých se apriori domnívám, že se mi budou libit.) 
    * Tímto přístupem (Jacardova vzdálenost) nicméně přicházím o informaci o skutečných hodnoceních. Jednou z možností, jak tuto informaci alespoň částečně zachovat, je provedení následující transformace: hodnocení méně než 3 hvězdičky nebudu při výpočtu _Jacardovy vzdálenosti_ uvažovat. 
* Při hledání nejbližších sousedů jsme uvažovali jen ty dvojice uživatelů, mezi nimiž existuje _"nezáporná podobnost."_ **Zkusme tuto podmínku odstranit.**
    * __Jak se změnila výkonnost modelu?__
    * Jak můžeme __vystvětlit použití sousedů se _"zápornou podobností"_?__ Je tento přístup vhodný? 
* Při vytváření predikcí postupujeme takto:
    * nejprve určíme okolí klienta a pak se díváme, jak daný film hodnotili uživatelé v tomto okolí. 
    * Může se stát, že nikdo z uživatelů v okolí daný film nehodnotil. V takovém případě použijeme některý ze základních modelů (tj. $\bar{r}$, $\bar{r}_u$, $\bar{r}_f$, ...).
    * Alternativou by bylo pro každý hodnocený film vzít $k$ hodnotitelů nejpodobnějších danému uživateli $u$ a zprůměrovat (neváženě, váženě) jejich hodnocení.
    * Zkuste implementovat. Dává tento přístup lepší výsledky? Pro velká $k$ by se měl rozdíl stírat.

</details>



## B) Item-Item Collaborative filtering {.leftindent}

### Item-Item Collaborative filtering

> <span class='nedulezite'>základ: 3 b.<br>bonus: 1 b.</span>

* Při predikci hodnocení $r_{u,f}$ hledáme $k$ __filmů__, které daný klient už viděl ($f' \in F_u$), které jsou nejpodobnější hodnocenému filmu $f$ (tj. jsou týmiž uživateli hodnoceni podobně, jako film $f$). 
* Kýženou predikcí pak budiž (vážený) průměr hodnocení uživatele $u$ těchto filmů.
* Viz též [wiki](https://en.wikipedia.org/wiki/Item-item_collaborative_filtering)

### Postup

* Postupujeme obdobně jako v případě `user-user collaborative filtering` (__viz předchozí kapitolka__).

<details>
  <summary>Určíme podobnost __filmů__:  $sim(f_i,f_j), \forall f_i,f_j\in F$.</summary>
  
* Vyjdeme přitom z hodnocení $R$.
    * <b>hint</b>: Použijte _řídkou matici_ vytvořenou v předchozí úloze.
* __Zkuste opět implementovat__ následující metody:
    * __[Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)__ 
    * __[Pearsonův korelační koeficient](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient)__
    * <b>hint</b>: Pokud transponujete matici hodnocení, převedete úlohu na známý případ...
</details>

<details>
  <summary>Pro každé predikované  hodnocení $r_{u,f}$ najdeme __okolí filmu $f$__ mezi filmy viděnými uživatelem $u$ (tj. $F_u$) __představující $k$ nejbližších (nejpodobnějších) filmů__</summary>

* Samozřejmě pro každou podobnost zvlášť.
* __Zvolte $k$ "rozumně" velké__, resp. zopakujte pro různé volby $k$ (zkuste např. 10, 20, 50 či 100 filmů). 
* Při hledání sousedů berte vpotaz pouze filmy, s nimiž má hodnocený film _nezápornou podobnost_; je-li takových filmů méně než $k$, vezměte všechny dostupné.
* Viz též [wiki](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm) 
</details>

<details><summary>Stanovíme $p_{u,f}$, predikci hodnocení filmu $r_{u,f}$.</summary>

* Předpisy pro predikce jsou obdobné těm, které byly uvedeny v části `user-user collaborative filtering`, tj. (4a, 4a') a (4b, 4b').
    * Namísto $N_f(u)$ (= sousedé uživatele $u$, kteří viděli film $f$) budeme používat okolí $N_u(f)$ (= sousedé filmu $f$, které viděl uživatel $u$); atp.
    * V případě dotazů se obraťte na cvičícího, příp. bude doplněno do tohoto textu.

</details>


<details><summary>BONUS</summary>

* Při hledání bonusových úloh se inspirujte v případě `user-user collaborative filtering`. Zejména:
    * Zkuste zvolit další míry podobnosti mezi filmy.
    * Zkuste uvažovat i filmy s _negativní podobností_, pokud to daný způsob stanovení podobnosti umožňuje.
    * Zkuste vyjít z reziduí. Má tento přístup smysl?
</details>



## C) Content-based models {.leftindent}

### Content-based models

> <span class='nedulezite'>základ: 7 b.<br>bonus: 2 b.</span>

* V této části projektu se zaměříme na modelování hodnocení uživatelů na základě vlastností filmů. Tím se tato metoda liší od `item-item collaborative filtering`, jíž jsme uvažovali výše.
    * Namísto matice hodnocení budeme vycházet z příznaků (features), které si pro filmy připravíme z dat.
    * V datasetu, který máme k dispozici, se nevyskytuje příliš mnoho informací o jednotlivých filmech. 
        * **Využijeme proto k predikcím `tagy`.**
    * Nicméně pokud jste v úvodní části dokázali najít dodatečná data (např. z IMDb.com), směle je použijte v rámci Bonusové části.

### Postup

<details><summary>Nejprve potřebujeme stanovit významnost (váhu) jednotlivých tagů. Existuje víc přístupů, my se omezíme na metodu [__TF-IDF__](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)</summary>

* __Vypočítejte TF-IDF__ (Term-frequency Inverse document frequency). Pro film $f_j$ a tag $t_i$ (vyskytující se v $n_i$ filmech celkem a ve filmu $f_j$ právě $k_{i,j}$-krát) platí: 
$$TF-IDF(t_i, f_j) = TF(t_i, f_j) \cdot \log\left(\frac{|F|}{n_i}\right),$$
kde $$TF(t_i, f_j) = \frac{k_{i,j}}{\max_m k_{m,j}}.$$
* Znormujte: $$w_{i,j} = \frac{TF-IDF(t_i, f_j)}{\sqrt{\sum_{s=1}^{|T|} TF-IDF(t_s, f_j)^2}}.$$
* Výsledkem je $|T|\cdot|F|$-rozměrná matice, kde $T$ je množina všech tagů. 
* <b>hint</b>: Uvědomme si, že rozhodně nepůjde o _řídkou matici_.
* <b>hint</b>: Pokud se vám toto nepodaří implementovat, zkuste alespoň použít build-in modul `pyspark.mllib.feature`. Naštěstí je dostupný i v PySpark v. `1.6.0`.
</details>

<details><summary>Stanovte podobnost filmů</summary>

* Z matice TF-IDF $W = \lbrace w_{i,j}\rbrace$ __spočítejte podobnost filmů__ 
    * Použijte __[cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)__, resp. __[Pearsonův korelační koeficient](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient)__. Použijte kód implementovaný v rámci `Item-Item Collaborative filtering` (resp. obdobně jako v (4a, 4a') a (4b, 4b') v případě `User-User Collaborative filtering`).
    * V případě nejasností se obraťte na cvičícího.
</details>

<details><summary>Spočítejte predikce hodnocení $r_{u,f}$</summary>

* Nyní máte k dispozici matici vzdáleností (podobností) filmů.
* **Spočítejte predikce stejným postupem, jako v případě `Item-item collaborative filtering.`.** 
</details>




<details><summary>BONUS</summary>

* Obdobný postup můžeme použít i **v případě `genome-tagů`**. Který přístup funguje lépe?
* Vedle $TF-IDF$ samozřejmě existuje celá řada dalších přístupů, jak vytěžit z jednotlivých položek (v našem případě filmů) zajímavé informace, na jejichž základě pak lze predikovat hodnocení.
    * Triviální přístup - použijeme všechny tagy, aniž bychom uvažovali jejich váhu (tj. $w_{i,j} = \delta_{t_i \in T_{f_j}}$ )
    * ...
    * Zkuste některou také implementovat a ověřit její výkonnost.
* Pokud jste v úvodní části projektu získali další informace o jednotlivých filmech (další datasety), můžete vyzkoušet popsanou techniku na těchto datech. 
    * Pozor, v některých případech bude třeba nejprve provést vhodný preprocessing dat...


</details>



## D) Redukce dimenze {.leftindent}

### Redukce dimenze

> <span class='nedulezite'>základ: 5 b.<br>bonus: 5 b.</span>


* Jde o velmi zajímavou metodu, nicméně pro naše data není patrně úplně vhodná (viz otázky v úvodní kapitole). Uvidíme.
* Klíčovou myšlenkou tohoto přístupu je předpoklad, že existuje $k$ latentních veličin (přičemž $k << |F|$ i $k << |U|$), jimiž lze uspokojivě vystvětlit uživatelská hodnocení filmů. 
    * Příklady latentních veličin - jak zřejmé  (žánr, množství akčních scén, doba, kdy je na scéně Nicolas Cage,...), tak subtilnější (síla příběhu, vývoj postav, ...) či úplně neinterpretovatelné
    * O každém __filmu__ $f$ pak předpokládáme, že spojen s vektorem $\phi_f \in \mathbb{R}^k$ představujícím zastoupení jednotlivých faktorů v daném filmu.
    * O každém __uživateli__ $u$ předpokládáme, že je spojen s vektorem $\psi_u \in \mathbb{R}^k$ představujícím uživatelovu oblibu daného aspekut.
* Predikcí je pak skalární součin příslušných vektorů.

### Postup

* V základní části použijeme pouze *build-in* řešení, které je implementováno v modulu `pyspark.ml.recommendation`.
    * V rámci pyspark `v1.6.0` je k dispozici faktorizace matice hodnocení metodou *Alternating Least Squares*. 
    * Viz též [dokumentace](https://spark.apache.org/docs/1.6.0/api/python/pyspark.ml.html#pyspark.ml.recommendation.ALS))
* Postup je tedy vcelku přímočarý:
    * Připravte si podklady (dataframe hodnocení; měli byste je mít již k dispozici)
    * Zvolte hyperparametry - počet latentních faktorů, ... 
    * Fitněte model.
    * Vytvořte predikce.
* Zkuste zopakovat pro více voleb hyperparametrů. 
    * Jaké parametry jste zvolili?
    * Jak si model
* Podívejte se na zastoupení (váhu) latentních faktorů mezi filmy (zkuste [itemFactors](https://spark.apache.org/docs/1.6.0/api/python/pyspark.ml.html#pyspark.ml.recommendation.ALSModel.itemFactors)).
    * Podaří se vám interpretovat význam některého z faktorů?
    * Existuje vztah mezi latentními faktory a třeba žánrem filmu? (<b>hint</b>: zde by se mohl hodit obrázek...)



### Bonus

Pro fajnšmekry - implementujme celé řešení sami.

<details><summary>Vytvořte matici hodnocení $R = \lbrace r_{i,j}\rbrace$</summary>

* Viz poznámky pro `User-User Collaborative filtering`.
</details>

<details><summary>Rozložte matici hodnocení na součin matic</summary>

* Existuje celá řada přístupů, my se zde zaměříme na metody založené na [SVD](https://en.wikipedia.org/wiki/Singular_value_decomposition).
    * Bohužel v PySpark je SVD až od [v 2.2.0](https://spark.apache.org/docs/2.2.0/api/python/pyspark.mllib.html#pyspark.mllib.linalg.distributed.SingularValueDecomposition)). Bude proto třeba nejprve implementovat.
    * <b>hint</b>: návod <span class="nedulezite">(bez ověření správnosti)</span> je třeba [tu](https://stackoverflow.com/questions/33428589/pyspark-and-pca-how-can-i-extract-the-eigenvectors-of-this-pca-how-can-i-calcu/33500704#33500704) na StackOverflow.
    * <b>hint</b>: nezapomeňte, že je třeba __doplnit chybějící pozorování__. Opět existuje řada možností, Jednou z nich je přechod k matici reziduí $\tilde{r}_{ij} = r - \bar{r}$ a chybějící pozorování posléze doplnit nulami. (Alternativně lze použít rezidua po odečtení některého z *baseline predictors*.)
* Spočítejme proto následující matice:
$$R = \Phi \cdot \Sigma \cdot \Psi^\top.$$
    * Z matice $\Sigma$ (je diagonální!) vytvoříme __pro vhodné $k$__ (opět můžete zkusti různé volby) matici:
    $$\sqrt{\Sigma} = \left\lbrace \sqrt{\sigma_{i,j}}\cdot\delta_{i=j, i\leq k} \right\rbrace.$$
    * Budeme uvažovat matice $$\Phi^* = \Phi \cdot \sqrt{\Sigma}, \Psi^* = \sqrt{\Sigma}\cdot \Psi^\top.$$ Tyto matice ($\Phi^*$ a $\Psi^*$) představují výše popsanou vztah mezi filmem/uživatelem a $k$ latentními faktory.
    * <span class="nedulezite"><b>hint</b>: lze se omezit jen na ty řádky/sloupce matic $P^*$ a $Q^*$, které nejsou celé nulové...</span>

</details>

<details><summary>Napočítáme predikce hodnocení.</summary>

* Nyní již vytvoříme predikce hodnocení skalárním součinem příslušných vektorů $\phi_f$ a $\psi_u$.

</details>






# Clusterování

> <span class='nedulezite'>základ: 5 b.<br>bonus: 3 b.</span>

* <span class='dulezite'> [bude doplněno] </span> 
    * (Na přednášce se budeme tomuto tématu věnovat 12. 4.; tato část zadání bude patrně doplněna k tomuto datu).




# Overfitting a schopnost zobecňovat

> <span class='nedulezite'>základ: 2 b.</span>

Jak bylo probráno na přednášce, je důležitou schopností modelů __zobecnitelnost na další data__, která neviděly v průběhu učení. Pokud toho model schopný není, hovoříme o tzv. __přeučení__ ([overfitting](https://en.wikipedia.org/wiki/Overfitting)).

[Kaggle](www.kaggle.com) nám umožní otestovat tuto schopnost u modelů, jejichž predikce jsme odevzdali. Veškerá hodnocení, která vidíte na Leaderboardu, byla provedena **na 70 %** náhodně vybraných pozorování z testovacího datasetu. (Ano, pro všechny predikce je to vždy stejných 70 % pozorování). 

Ke konci semestru (konkrétně `05/20/2019 11:59 PM UTC`) dojde k **vyhodnocení predikcí na zbylých 30 %**. Do této části máte možnost vybrat jednoho kandidáta-šampiona; na základě jeho úspěchu pak bude stanoveno konečné pořadí v naší mini-soutěži. K tomu ještě dvě poznámnky:

* Jak již bylo řečeno výše, konečné pořadí **nemá** dopad na výslednou známku. 
* I po deadline soutěže bude možné odevzdávat svá řešení a nechávat si je ohodnotit. I nadále tedy bude možné vypracovat zápočtový projekt na výbornou.

---

V poslední části se zaměřte na to, **jak jsou vaše modely použitelné v praxi** (především ve smyslu schopnosti zobecňovat). Zkuste zodpovědět například tyto otázky:

* __Jaký model mi zafungoval nejlépe?__ 
* __Jak se při hodnocení na neznámých datech dařilo vašim dosud nejlepším modelům?__
* __Jak si vedly `základní` modely ve srovnání s `pokročilejšími` metodami?__




