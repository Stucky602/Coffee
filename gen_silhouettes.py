import geopandas as gpd
from shapely.geometry import MultiPolygon, Point
import json

w50 = gpd.read_file('ne50.geojson')
NAME='NAME' if 'NAME' in w50.columns else 'name'

def norm_and_path(polys, flipY=True):
    """Given list of shapely polygons, normalize into 0..100 box, return SVG path (straight-line)."""
    allc=[]
    for p in polys: allc+=list(p.exterior.coords)
    xs=[c[0] for c in allc]; ys=[c[1] for c in allc]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    span=max(maxx-minx, maxy-miny)
    if span==0: span=1
    # center within 100 box
    offx=(100-(maxx-minx)/span*100)/2
    offy=(100-(maxy-miny)/span*100)/2
    def tx(x,y):
        nx=offx+(x-minx)/span*100
        ny=offy+((maxy-y) if flipY else (y-miny))/span*100
        return nx,ny
    subs=[]
    for p in polys:
        cs=list(p.exterior.coords)
        subs.append('M'+' L'.join(f'{tx(x,y)[0]:.1f} {tx(x,y)[1]:.1f}' for x,y in cs)+'Z')
    return ' '.join(subs)

def _span_tol(polys, frac=0.006):
    """Tolerance as a fraction of the bounding-box span, so small and large countries
    keep a comparable NUMBER of vertices (avoids collapsing small islands to spikes)."""
    xs=[];ys=[]
    for p in polys:
        x0,y0,x1,y1=p.bounds; xs+=[x0,x1]; ys+=[y0,y1]
    span=max(max(xs)-min(xs), max(ys)-min(ys)) or 1
    return span*frac

def get_country(name, frac=0.006, area_frac=0.12, max_polys=None):
    row=w50[w50[NAME]==name]
    if row.empty: return None
    geom=row.geometry.values[0]
    polys=sorted(geom.geoms,key=lambda p:p.area,reverse=True) if isinstance(geom,MultiPolygon) else [geom]
    main=polys[0].area
    polys=[p for p in polys if p.area>main*area_frac]
    if max_polys: polys=polys[:max_polys]
    tol=_span_tol(polys, frac)
    polys=[p.simplify(tol,preserve_topology=True) for p in polys]
    return norm_and_path(polys)

def get_island(country, cx, cy, frac=0.004):
    """Extract the single island polygon nearest (cx,cy). Uses span-relative tolerance
    with a FINER fraction than mainland, since islands have the spikiest coastlines."""
    geom=w50[w50[NAME]==country].geometry.values[0]
    polys=list(geom.geoms) if isinstance(geom,MultiPolygon) else [geom]
    target=Point(cx,cy)
    best=min(polys, key=lambda p:p.centroid.distance(target))
    tol=_span_tol([best], frac)
    best=best.simplify(tol,preserve_topology=True)
    return norm_and_path([best])

def get_islands_multi(country, centers, frac=0.004):
    """Extract multiple islands (for Hawaii chain) nearest each center, keep as multi-subpath."""
    geom=w50[w50[NAME]==country].geometry.values[0]
    polys=list(geom.geoms) if isinstance(geom,MultiPolygon) else [geom]
    chosen=[]
    for (cx,cy) in centers:
        t=Point(cx,cy)
        p=min(polys,key=lambda q:q.centroid.distance(t))
        if p not in chosen: chosen.append(p)
    tol=_span_tol(chosen, frac)
    chosen=[p.simplify(tol,preserve_topology=True) for p in chosen]
    return norm_and_path(chosen)

mainland={
 'Brazil':'Brazil','Colombia':'Colombia','Ethiopia':'Ethiopia','Kenya':'Kenya','Vietnam':'Vietnam',
 'India':'India','Mexico':'Mexico','Peru':'Peru','Papua New Guinea':'Papua New Guinea',
 'Guatemala':'Guatemala','Costa Rica':'Costa Rica','Honduras':'Honduras','Nicaragua':'Nicaragua',
 'El Salvador':'El Salvador','Yemen':'Yemen','Tanzania':'Tanzania','Rwanda':'Rwanda','Ecuador':'Ecuador',
 'Bolivia':'Bolivia','Uganda':'Uganda','Malawi':'Malawi','Zambia':'Zambia','Zimbabwe':'Zimbabwe',
 'Burundi':'Burundi','Thailand':'Thailand','China (Yunnan)':'China','Timor-Leste':'Timor-Leste',
 'Jamaica':'Jamaica','Panama':'Panama','DR Congo':'Dem. Rep. Congo',
}
out={}
for key,ne in mainland.items():
    # Ecuador: drop Galapagos (far west islands); Yemen: drop Socotra; handled by area_frac
    af=0.12
    if key in ('Ecuador','Yemen','India','Chile','Tanzania','Papua New Guinea'): af=0.20
    p=get_country(ne, area_frac=af)
    out[key]=p

# Indonesian islands by centroid (lon,lat)
out['Indonesia (Sumatra)']=get_island('Indonesia',101.6,-0.4)
out['Java']=get_island('Indonesia',110.2,-7.3)
out['Sulawesi (Toraja)']=get_island('Indonesia',121.2,-2.1)
out['Flores (Bajawa)']=get_island('Indonesia',121.3,-8.6)
# Bali is small; try 50m, fallback handled below
try:
    out['Bali (Kintamani)']=get_island('Indonesia',115.1,-8.3,frac=0.003)
except: out['Bali (Kintamani)']=None
# Hawaii main islands from USA
try:
    out['Hawaii (Kona)']=get_islands_multi('United States of America',
        [(-155.5,19.6),(-156.3,20.8),(-157.0,21.3),(-158.0,21.5),(-159.5,22.0)])
except Exception as e:
    print('hawaii fail',e); out['Hawaii (Kona)']=None

# report
ok=sum(1 for v in out.values() if v)
print(f'generated {ok}/{len(out)}')
for k,v in out.items():
    if not v: print('  MISSING:',k)
    else:
        pts=v.count('L')+v.count('M')
        if pts<8: print(f'  low-detail {k}: {pts}')
json.dump(out, open('real_silhouettes.json','w'))
print('saved real_silhouettes.json')
